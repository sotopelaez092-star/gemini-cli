# Case 04: Private method naming convention error
# Difficulty: Medium

from services.encryption import EncryptionService

def main():
    service = EncryptionService("my-secret-key")
    data = "sensitive information"

    # Error: Trying to call private method with wrong name
    # User wrote '_encrypt' but actual method is '_do_encrypt'
    encrypted = service._encrypt(data)
    print(f"Encrypted: {encrypted}")

if __name__ == "__main__":
    main()
