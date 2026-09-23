from Crypto.Util import number
import math

p = number.getPrime(1024)
q = number.getPrime(1024)

n = p * q

phin = (p - 1) * (q - 1)

e = 65537

a = phin
b = e

def extended_gcd(divisor, remainder):
    if remainder == 1:
        return 1, 0, 1   

    quotient = divisor // remainder
    new_remainder = divisor % remainder

    print(f"{divisor} = {remainder}({quotient}) + {new_remainder}")

    gcd, x, y = extended_gcd(remainder, new_remainder)

    new_x = y
    new_y = x - quotient * y

    print(f"Backtracking: {gcd} = {divisor}({new_x}) + {remainder}({new_y})")

    return gcd, new_x, new_y


gcd, x, y = extended_gcd(a, b)
d = y % phin

print(f"The private exponent for {b} is {d}")
print(f"{(d * b) % phin=}")

secret = "This is a secret!"

secret_bytes = secret.encode('utf-8')

decimal_value = int.from_bytes(secret_bytes, byteorder='big')
print(decimal_value)

cipherdec = pow(int(decimal_value), b, n)
length = (cipherdec.bit_length() + 7) // 8
ciphertext = cipherdec.to_bytes(length, byteorder='big')
ciphertext = ciphertext.decode('utf-8', errors="ignore")
print(f"Encrypted = {ciphertext}")

plaintext = pow(cipherdec, d, n)
length = (plaintext.bit_length() + 7) // 8
plaintext = plaintext.to_bytes(length, byteorder='big')
plaintext = plaintext.decode('utf-8')
print(f"Decrypted = {plaintext}")