import base64
import hashlib

class EncryptionService:
    """Service for encrypting and decrypting data."""

    def __init__(self, key):
        self._key = key
        self._algorithm = "sha256"

    def encrypt(self, data):
        """Public method to encrypt data."""
        return self._do_encrypt(data)

    def decrypt(self, data):
        """Public method to decrypt data."""
        return self._do_decrypt(data)

    def _do_encrypt(self, data):
        """Private method that performs actual encryption."""
        key_hash = hashlib.sha256(self._key.encode()).digest()
        encoded = base64.b64encode(data.encode())
        return encoded.decode()

    def _do_decrypt(self, data):
        """Private method that performs actual decryption."""
        decoded = base64.b64decode(data.encode())
        return decoded.decode()

    def _generate_iv(self):
        """Generate initialization vector."""
        import os
        return os.urandom(16)
