import ssl
import socket
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def get_ssl_info(domain: str, port: int = 443, timeout: float = 10.0) -> Dict[str, Any]:
    """Fetch SSL certificate info."""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # For info only

        sock = socket.create_connection((domain, port), timeout)
        ssock = context.wrap_socket(sock, server_hostname=domain)

        cert_der = ssock.getpeercert(binary_form=True)
        cert = x509.load_der_x509_certificate(cert_der, default_backend())

        data = {
            "subject_cn": cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME),
            "issuer_cn": cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME),
            "not_before": cert.not_valid_before.isoformat(),
            "not_after": cert.not_valid_after.isoformat(),
            "serial_number": str(cert.serial_number),
            "signature_algorithm": cert.signature_algorithm_oid._name,
            "key_algorithm": cert.public_key()._public_key_algorithm_oid._name if hasattr(cert.public_key(), '_public_key_algorithm_oid') else 'Unknown',
        }
        ssock.close()
        sock.close()
        return {"ssl": data}
    except Exception as e:
        return {"ssl": {"error": str(e)}}