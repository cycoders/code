import asyncio
import socket
import ssl
from typing import List
from tls_inspector.cert_analyzer import analyze_chain
from tls_inspector.models import TLSReport
from tls_inspector.output import console  # for errors

COMMON_CIPHERS = [
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
]

PROTO_VERSIONS = [
    ("TLS 1.3", ssl.TLSVersion.TLSv1_3),
    ("TLS 1.2", ssl.TLSVersion.TLSv1_2),
    ("TLS 1.1", ssl.TLSVersion.TLSv1_1),
    ("TLS 1.0", ssl.TLSVersion.TLSv1),
]


async def inspect_tls(host: str, port: int = 443, ipv6: bool = False) -> TLSReport:
    family = socket.AF_INET6 if ipv6 else socket.AF_INET
    try:
        protocols = await probe_protocols(host, port, family)
        neg_proto, neg_cipher, chain_der = await get_negotiated(host, port, family)
        certs, chain_valid = analyze_chain(chain_der)
        ciphers = await probe_ciphers(host, port, family)
        hsts = await get_hsts(host, port, family)
        grade = compute_security_grade(protocols, neg_cipher, ciphers, certs[0] if certs else None, hsts)
        return TLSReport(
            host=host,
            port=port,
            protocols=protocols,
            negotiated_protocol=neg_proto,
            negotiated_cipher=neg_cipher,
            supported_ciphers=ciphers,
            cert_chain=certs,
            chain_valid=chain_valid,
            hsts=hsts,
            security_grade=grade,
        )
    except asyncio.TimeoutError:
        raise ValueError("Connection timeout")
    except ssl.SSLError as e:
        raise ValueError(f"TLS handshake failed: {e}")
    except OSError as e:
        raise ValueError(f"Connection failed: {e}")


async def probe_protocols(host: str, port: int, family: int) -> List[str]:
    sem = asyncio.Semaphore(4)

    async def test_proto(name: str, ver: ssl.TLSVersion):
        async with sem:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.minimum_version = ver
            ctx.maximum_version = ver
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            try:
                await asyncio.wait_for(_open_connection(host, port, family, ctx), timeout=3.0)
                return name
            except:
                return None

    tasks = [test_proto(name, ver) for name, ver in PROTO_VERSIONS]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r]


async def probe_ciphers(host: str, port: int, family: int) -> List[str]:
    sem = asyncio.Semaphore(8)

    async def test_cipher(ciph: str):
        async with sem:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.set_ciphers(ciph)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            try:
                await asyncio.wait_for(_open_connection(host, port, family, ctx), timeout=2.0)
                return ciph
            except:
                return None

    tasks = [test_cipher(ciph) for ciph in COMMON_CIPHERS]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r]


async def get_negotiated(host: str, port: int, family: int):
    ctx = ssl.create_default_context()
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port, family=family, ssl=ctx), timeout=10.0
    )
    sslsock = writer.get_extra_info("ssl_object")
    neg_proto = sslsock.version() or "Unknown"
    neg_cipher = sslsock.cipher()[0] if sslsock.cipher() else "Unknown"
    chain_der = sslsock.getpeercert(True) or b""
    writer.close()
    await writer.wait_closed()
    return neg_proto, neg_cipher, chain_der


async def get_hsts(host: str, port: int, family: int) -> dict | None:
    ctx = ssl.create_default_context()
    reader, writer = await asyncio.open_connection(host, port, family=family, ssl=ctx)
    req = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()
    writer.write(req)
    await writer.drain()
    data = await asyncio.wait_for(reader.read(8192), timeout=5.0)
    writer.close()
    await writer.wait_closed()

    headers = {}
    for line in data.decode(errors="ignore").split("\r\n")[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()

    hsts_header = headers.get("strict-transport-security")
    if not hsts_header:
        return None

    policy = {"max_age": 0}
    for part in hsts_header.split(";"):
        part = part.strip()
        if part.startswith("max-age="):
            policy["max_age"] = int(part.split("=")[1])
        elif "includesubdomains" in part:
            policy["includesubdomains"] = True
        elif "preload" in part:
            policy["preload"] = True
    return policy


def compute_security_grade(
    protocols: List[str],
    neg_cipher: str,
    supp_ciphers: List[str],
    leaf_cert: 'Certificate | None',
    hsts: dict | None,
) -> str:
    score = 0
    if "TLS 1.3" in protocols:
        score += 20
    if "TLSv1.3" in neg_cipher:
        score += 20
    strong_ciph = any(ciph.startswith("TLS_AES_") or "CHACHA20" in ciph for ciph in supp_ciphers)
    if strong_ciph:
        score += 15
    if leaf_cert:
        if leaf_cert.key_size >= 2048 or leaf_cert.key_size >= 256:
            score += 15
        if "SHA256" in leaf_cert.sig_algo or "SHA384" in leaf_cert.sig_algo:
            score += 15
    if hsts and hsts.get("max_age", 0) > 31536000:
        score += 10
    if hsts and hsts.get("preload"):
        score += 5
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


async def _open_connection(host: str, port: int, family: int, ctx: ssl.SSLContext):
    reader, writer = await asyncio.open_connection(
        host, port, family=family, ssl=ctx, ssl_handshake_timeout=3.0
    )
    writer.close()
    await writer.wait_closed()