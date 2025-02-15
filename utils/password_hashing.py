import os
import hashlib
import binascii


class PasswordManager:
    def __init__(self, iterations=100_000, salt_size=16, algorithm='sha256'):
        self.iterations = iterations
        self.salt_size = salt_size
        self.algorithm = algorithm

    def hash_password(self, password: str) -> str:
        salt = os.urandom(self.salt_size)
        hash_bytes = hashlib.pbkdf2_hmac(self.algorithm, password.encode('utf-8'), salt, self.iterations)
        salt_hex = binascii.hexlify(salt).decode('utf-8')
        hash_hex = binascii.hexlify(hash_bytes).decode('utf-8')
        return f"{self.iterations}${salt_hex}${hash_hex}"

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        try:
            iterations_str, salt_hex, hash_hex = stored_password.split('$')
            iterations = int(iterations_str)
            salt = binascii.unhexlify(salt_hex)
            original_hash = binascii.unhexlify(hash_hex)
            new_hash = hashlib.pbkdf2_hmac(self.algorithm, provided_password.encode('utf-8'), salt, iterations)
            return new_hash == original_hash
        except Exception as e:
            return False
