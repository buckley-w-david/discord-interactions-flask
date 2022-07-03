from functools import wraps

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


def verify_key(
    raw_body: bytes, signature: str, timestamp: str, client_public_key: str
) -> bool:
    message = timestamp.encode() + raw_body
    try:
        vk = VerifyKey(bytes.fromhex(client_public_key))
        vk.verify(message, bytes.fromhex(signature))
        return True
    except BadSignatureError:
        return False


def verify_key_decorator(client_public_key):
    from flask import request

    def _decorator(f):
        @wraps(f)
        def __decorator(*args, **kwargs):
            # Verify request
            signature = request.headers.get("X-Signature-Ed25519")
            timestamp = request.headers.get("X-Signature-Timestamp")
            if (
                signature is None
                or timestamp is None
                or not verify_key(request.data, signature, timestamp, client_public_key)
            ):
                return "Bad request signature", 401

            # Pass through
            return f(*args, **kwargs)

        return __decorator

    return _decorator
