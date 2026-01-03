from typing import List, Tuple
import x509
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from tls_inspector.models import Certificate


def analyze_cert(der_bytes: bytes) -> Certificate:
    """Analyze a single DER-encoded X.509 certificate."""
    cert = x509.load_der_x509_certificate(der_bytes)

    subject = cert.subject.rfc4514_string()
    issuer = cert.issuer.rfc4514_string()
    serial = str(cert.serial_number)
    not_before = cert.not_valid_before.isoformat()
    not_after = cert.not_valid_after.isoformat()

    san: List[str] = []
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san = [str(san_val.value) for san_val in ext.value.get_values_for_type(x509.DNSName)]
    except x509.ExtensionNotFound:
        pass

    sig_oid = cert.signature_algorithm_oid.dotted_string.replace('.', '-').upper()

    pub_key = cert.public_key()
    if isinstance(pub_key, rsa.RSAPublicKey):
        key_type = 'RSA'
        key_size = pub_key.key_size
    elif isinstance(pub_key, ec.EllipticCurvePublicKey):
        key_type = 'ECDSA'
        key_size = pub_key.curve.key_size
    else:
        key_type = 'Unknown'
        key_size = 0

    version = f'v{cert.version.value + 1}'

    return Certificate(
        subject=subject,
        issuer=issuer,
        serial=serial,
        not_before=not_before,
        not_after=not_after,
        san=san,
        key_type=key_type,
        key_size=key_size,
        sig_algo=sig_oid,
        version=version
    )


def analyze_chain(chain_der: List[bytes]) -> Tuple[List[Certificate], bool]:
    """Analyze certificate chain and validate issuer-subject links."""
    certs = [analyze_cert(der) for der in chain_der]
    valid = True
    for i in range(1, len(certs)):
        if certs[i].subject != certs[i - 1].issuer:
            valid = False
            break
    # Root self-signed check
    if certs and certs[-1].subject != certs[-1].issuer:
        valid = False
    return certs, valid