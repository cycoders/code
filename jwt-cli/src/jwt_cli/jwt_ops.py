from typing import Dict, Any, Tuple, List, Optional
import jwt
from jwt import PyJWTError, ExpiredSignatureError, ImmatureSignatureError, InvalidSignatureError, InvalidIssuerError, InvalidAudienceError, DecodeError, InvalidAlgorithmError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def decode_token(token: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """Decode unverified JWT parts."""
    try:
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        parts = token.rsplit('.', maxsplit=2)
        if len(parts) != 3:
            raise DecodeError("Invalid segment count")
        sig_b64 = parts[2]
        return header, payload, sig_b64
    except PyJWTError as e:
        raise ValueError(f"Decode error: {e}") from e

def load_key(key_data: bytes, alg: str, private: bool = False) -> Any:
    """Load signing/verification key."""
    if alg.startswith("HS"):
        return key_data
    try:
        if private:
            return serialization.load_pem_private_key(key_data, password=None, backend=default_backend())
        else:
            return serialization.load_pem_public_key(key_data, backend=default_backend())
    except Exception as e:
        loader = "private" if private else "public"
        raise ValueError(f"Failed to load {loader} key: {e}") from e

def sign_token(payload: Dict[str, Any], key_input: bytes | str, alg: str, headers: Optional[Dict[str, Any]] = None) -> str:
    """Sign payload to JWT."""
    if headers is None:
        headers = {}
    key_data = key_input.encode("utf-8") if isinstance(key_input, str) else key_input
    key = load_key(key_data, alg, private=True)
    return jwt.encode(payload, key, algorithm=alg, headers=headers)

def validate_token(
    token: str,
    key_input: bytes | str,
    alg: Optional[str] = None,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
    leeway: int = 0,
) -> Tuple[bool, List[str]]:
    """Full JWT validation."""
    try:
        header = jwt.get_unverified_header(token)
        alg = alg or header["alg"]
        key_data = key_input.encode("utf-8") if isinstance(key_input, str) else key_input
        key = load_key(key_data, alg, private=False)
        jwt.decode(
            token,
            key,
            algorithms=[alg],
            issuer=issuer,
            audience=audience,
            leeway=leeway,
        )
        return True, []
    except ExpiredSignatureError:
        return False, ["Token expired"]
    except ImmatureSignatureError:
        return False, ["Token not active (nbf/iat too early)"]
    except InvalidSignatureError:
        return False, ["Invalid signature"]
    except InvalidIssuerError as e:
        return False, [f"Invalid issuer (exp: {issuer}): {e}"]
    except InvalidAudienceError as e:
        return False, [f"Invalid audience (exp: {audience}): {e}"]
    except InvalidAlgorithmError:
        return False, ["Algorithm mismatch"]
    except DecodeError:
        return False, ["Malformed token"]
    except PyJWTError as e:
        return False, [f"JWT error: {e}"]
    except Exception as e:
        return False, [f"Unexpected: {e}"]