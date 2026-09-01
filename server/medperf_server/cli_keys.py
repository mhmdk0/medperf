"""Mock login keypair for the local-auth dev configs.

Deliberately mirrors `medperf.mock_tokens.generate_keypair` in the CLI: both
packages install independently, and whichever runs first creates the shared
keypair under ~/.medperf_dev/keys.
"""

import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS_DIR = Path.home() / ".medperf_dev" / "keys"
PRIVATE_KEY_PATH = KEYS_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "public_key.pem"


def ensure_mock_keypair() -> None:
    """Generates the mock signing keypair if it isn't there yet."""
    if PRIVATE_KEY_PATH.is_file() and PUBLIC_KEY_PATH.is_file():
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    PRIVATE_KEY_PATH.write_bytes(private_key_pem)
    os.chmod(PRIVATE_KEY_PATH, 0o600)
    PUBLIC_KEY_PATH.write_bytes(public_key_pem)
    print(f"Generated mock login keypair at {KEYS_DIR}")
