from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Random import get_random_bytes
from binascii import hexlify
from Crypto.Cipher import AES

threshold = 5
total_shares = 10

secret = get_random_bytes(16)
print(f"Secret is {secret.hex()}")
cipher = AES.new(secret, AES.MODE_GCM)
secret_message = b"Hi this is a secret message"
print(secret_message)
ciphertext, auth_tag = cipher.encrypt_and_digest(secret_message)
nonce = cipher.nonce
print(ciphertext)

shares = Shamir.split(threshold, total_shares, secret)

for share_id, share_data in shares:
    print(f"Share #{share_id}: {hexlify(share_data).decode()}")

subset = shares[2:7]

reconstructed = Shamir.combine(subset)
cipher = AES.new(reconstructed, AES.MODE_GCM, nonce=nonce)
decrypted_message = cipher.decrypt_and_verify(ciphertext, auth_tag)

print(f"Reconstructed Secret: {hexlify(reconstructed).decode()}")
print(f"Decrypted Message: {decrypted_message}")