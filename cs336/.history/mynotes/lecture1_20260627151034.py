print(ord('牛'))
print(chr(29275))

teststring = "hello! こんにちは "
utf8_encoded = teststring.encode('utf-8')
print(list(utf8_encoded))

print(chr(0))


print(repr(chr(0)))

def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])

print(decode_utf8_bytes_to_str_wrong(utf8_encoded))
