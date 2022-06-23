from cryptography.fernet import Fernet


class CryptoService:
    """Simple service to encrypt and decrypt messages using 'cryptography'."""

    def __init__(self, secret: str) -> None:
        self.fernet = Fernet(secret)

    def encrypt(self, msg: bytes) -> bytes:
        """Encrypt the message using the secret key."""
        return self.fernet.encrypt(msg)

    def decrypt(self, msg: bytes) -> bytes:
        """Decrypt the message using the secret key."""
        return self.fernet.decrypt(msg)
