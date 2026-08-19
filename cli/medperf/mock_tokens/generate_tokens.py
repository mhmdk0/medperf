from pathlib import Path
from time import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import jwt
import json

USERS = [
    "testadmin",
    "testbo",
    "testmo",
    "testdo",
    "testdo2",
    "testao",
    "testfladmin",
    "testpo",
]


def _token_payload(user):
    return {
        "https://medperf.org/email": f"{user}@example.com",
        "iss": "https://localhost:8000/",
        "sub": user,
        "aud": "https://localhost-localdev/",
        "iat": int(time()),
        "exp": int(time()) + 10**10,
    }


def generate_tokens(private_key_pem: bytes):
    """Signs mock login JWTs for the local test users.

    Args:
        private_key_pem (bytes): PEM-encoded RSA private key. Must match the
            public key the local dev server is configured to trust (see
            AUTH_VERIFYING_KEY_FILE in server/medperf/settings.py).

    Returns:
        dict: mapping of test user email to a signed JWT.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None, backend=default_backend()
    )

    tokens = {}
    for user in USERS:
        tokens[f"{user}@example.com"] = jwt.encode(
            _token_payload(user), private_key, algorithm="RS256"
        )
    return tokens


if __name__ == "__main__":
    # Manual dev usage: regenerate tokens.json next to this script, signed with
    # whatever private_key.pem.test sits alongside it.
    key_path = Path(__file__).resolve().parent / "private_key.pem.test"
    with open(key_path, "rb") as f:
        private_key_pem = f.read()

    tokens = generate_tokens(private_key_pem)
    out_path = Path(__file__).resolve().parent / "tokens.json"
    with open(out_path, "w") as f:
        json.dump(tokens, f)
