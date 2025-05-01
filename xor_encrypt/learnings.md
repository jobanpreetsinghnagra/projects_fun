## First Python Project: XOR Encryption

This project involved creating an encryption tool using the XOR cipher in Python. The initial idea was inspired by a Password Generation project.

### Initial Idea

1.  Generate a secure encryption key.
2.  Perform an XOR operation between the generated key and the content of a user-provided input file.
3.  Provide the user with the encryption key and the resulting output file.

### Execution Steps

#### Key Generation

Two Python modules were considered for key generation:
1.  `random` module
2.  `secrets` module

The `secrets` module was chosen because the documentation indicated it's designed for cryptographic purposes, unlike the `random` module which is typically used for modeling and testing.

The key was generated using:
```python
secrets.token_hex(size)
Handling User InputThe open() function in Python was used to get the user's input file.A challenge arose during the XOR operation: both operands needed to be of the same data type. To address this, the content of the user file was typecasted to a string:user_file_content = u_file.read()
user_file_string = str(user_file_content)
Another issue was handling newline characters (\n) within the input file. String manipulation functions were used to remove them:# Eliminating newline characters using split and join
split_text = user_file_string.split("\n")
joined_text = "".join(split_text)
Spaces were also removed using:user_string_no_spaces = joined_text.replace(" ", "")
print(user_string_no_spaces)
XOR LogicFor the XOR operation, it was necessary to ensure both the key and the input data were in byte format and had the same length.A function was created for the XOR operation:# Function for XOR operation
def xor_data(hex_key, input_data):
    key_bytes = bytes.fromhex(hex_key) # Convert hex key to bytes

    # Handle both string and bytes input
    if isinstance(input_data, str):
        input_bytes = input_data.encode() # Encode string to bytes
    else:
        input_bytes = input_data # Assume input is already bytes

    # Repeat the key to match the length of the input data
    repeated_key = (key_bytes * ((len(input_bytes) // len(key_bytes)) + 1))[:len(input_bytes)]

    # Perform XOR operation
    xored_bytes = bytes(b ^ k for b, k in zip(input_bytes, repeated_key))
    return xored_bytes
Key Repetition Example:If input_bytes has length 11 (e.g., 'HELLO_WORLD') and key_bytes has length 3 (e.g., 'KEY'):Calculate repetitions needed: (11 // 3) + 1 = 3 + 1 = 4.Repeat the key: key_bytes * 4 = b"KEYKEYKEYKEY".Trim the repeated key to match input length: b"KEYKEYKEYKEY"[:11] = b"KEYKEYKEYKE".The repeated_key becomes b"KEYKEYKEYKE".Exporting OutputThe generated key and the XORed output were saved to separate files:# Store the Key and XORed file
encryption_key = secrets.token_hex(16) # Example key generation
xored_result = xor_data(encryption_key, user_string_no_spaces) # Example XOR call

with open("the_key.txt", "w") as f:
  f.write(encryption_key)
with open("the_output.txt", "wb") as f: # Write in binary mode
  f.write(xored_result)
(Note: Changed the output file mode to "wb" (write binary) as the XOR result is bytes)DecryptionTo decrypt the data, the same XOR function is used with the saved key and the output file:# Decrypting using the same key
with open("the_key.txt", "r") as key_file:
    the_key = key_file.read()

with open("the_output.txt", "rb") as input_file: # Open in binary read mode
    the_input_byte = input_file.read()

# The XOR function handles bytes directly
decrypted_bytes = xor_data(the_key, the_input_byte)
print("Decrypted Text:", decrypted_bytes.decode()) # Decode bytes back to string
(Note: Simplified reading and adjusted decryption logic slightly for clarity)New Functions LearnedString Functions:split("\n"): Splits a string into a list of substrings based on the newline character."".join(iterable): Concatenates all items in an iterable into a single string.replace(" ", ""): Removes all occurrences of spaces in a string.File Handling:open("file_name", "mode"): Opens a file with specified mode (e.g., 'r' for read, 'w' for write, 'rb' for read binary, 'wb' for write binary).with open(...) as f:: Ensures the file is properly closed after its suite finishes.f.write(data): Writes data to the file.f.read(): Reads the content of the file.Encoding/Decoding & Bytes:.encode(): Converts a string into bytes using a specified encoding (default is UTF-8).bytes.fromhex(): Converts a string containing hexadecimal digits into bytes