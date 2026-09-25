file = input("Enter file path")

def gen_ecc(file):
    with open(file, 'rb') as f:
        data = f.read()

        total_bits = len(data * 8)
        total_ones = int.from_bytes(data, 'big').bit_count()
        total_zeros = total_bits - total_ones

        print(total_ones)
        
        if total_ones % 2 == 0:
            parity_bit = 1
        else:
            parity_bit = 0

        return parity_bit

parity_bit = gen_ecc(file)

print(parity_bit)

print("Simulating bit flip")

with open(file, 'r+b') as f:
    f.seek(1)
    byte_value = ord(f.read(1))
    mask = 1 << 2
    new_byte_value = byte_value ^ mask
    f.seek(1)
    f.write(bytes([new_byte_value]))

parity_bit2 = gen_ecc(file)
print(parity_bit2)


if parity_bit2 != parity_bit:
    print("Corruption detected!")
