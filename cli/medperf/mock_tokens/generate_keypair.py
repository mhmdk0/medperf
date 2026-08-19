from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def generate_keypair():
    """Generates a fresh RSA keypair for signing local mock login tokens.

    Returns:
        tuple[bytes, bytes]: (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key_pem, public_key_pem


if __name__ == "__main__":
    # Manual dev usage: regenerate a keypair next to this script,
    # mirroring the previous standalone-script behavior.
    private_key_pem, public_key_pem = generate_keypair()

    with open("private_key.pem.test", "wb") as f:
        f.write(private_key_pem)

    with open("public_key.pem.test", "wb") as f:
        f.write(public_key_pem)
