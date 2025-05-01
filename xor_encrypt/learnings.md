
# 1st Project in Python  
**Encryption Using XOR**  
*Inspired by a Password Generation project.*

---

## 🧠 What Was the Initial Idea?

1. Generate an encryption key.  
2. XOR that key with a user-provided input file.  
3. Provide the user with both the key and the output file.

---

## ⚙️ How I Executed That

### 🔑 Key Generation

I found two options in Python for key generation:

1. `random` module  
2. `secrets` module  

I chose the second one because the documentation mentioned that the `random` module is intended for modeling/testing purposes, not cryptography. So, **`secrets` became the obvious choice**.

I used:

```python
secrets.token_hex(size)
```

to generate the key.

---

### 📥 Getting User Input

To read input from the user file, I used:

```python
open()
```

However, this alone wasn’t sufficient. Later, during the XOR operation, I discovered that **both operands must be of the same data type**.

To handle this, I typecast the user file content into a string:

```python
user_file = str(u_file.read())
```

---

### 🧹 Cleaning the Input

#### 1. Removing Newlines  
To handle newline (`\n`) characters in the input file, I used:

```python
# Eliminating newlines using split and join
split_text = user_file.split("\n")
join_text = "".join(split_text)
```

#### 2. Removing Spaces  
Next, to eliminate spaces:

```python
user_string = join_text.replace(" ", "")
print(user_string)
```

---

## 🔄 XOR Logic

Once the input was cleaned, I implemented the XOR logic.  
Key points to ensure:

- Both inputs must be of **equal length**.  
- Both should be in **byte format**, not hex.

### XOR Function

```python
# Function for XOR 
def xor_string(hex_key, input_data):
    key_bytes = bytes.fromhex(hex_key)  # Convert the key to bytes

    # Handle both string and byte input
    if isinstance(input_data, str):
        input_bytes = input_data.encode()
    else:
        input_bytes = input_data

    repeated_key = (key_bytes * ((len(input_bytes) // len(key_bytes)) + 1))[:len(input_bytes)]
    xored_bytes = bytes(b ^ k for b, k in zip(input_bytes, repeated_key))
    return xored_bytes
```

### 🔁 Repeating the Key

For example:

```python
len(input_bytes) = 11  # 'HELLO_WORLD' has 11 characters
len(key_bytes) = 3     # 'KEY' has 3 characters

(len(input_bytes) // len(key_bytes)) + 1 = (11 // 3) + 1 = 4

key_bytes * 4 = b"KEYKEYKEYKEY"
b"KEYKEYKEYKEY"[:11] = b"KEYKEYKEYKE"
repeated_key = b"KEYKEYKEYKE"
```

---

## 💾 Exporting Results

```python
# Store the key and XORed file
with open("the_key.txt", "w") as f:
    f.write(e_key)

with open("the_output.txt", "w") as f:
    f.write(xored_result.hex())
```

---

## 🔓 Decryption

```python
# Decrypting using the same key
the_key = open("the_key.txt", "r").read()
the_input = open("the_output.txt", "rb")  # Open in binary read mode

# Read as bytes, decode for fromhex
the_input_byte = bytes.fromhex(the_input.read().decode())
decrypted = xor_string(the_key, the_input_byte)

print("Decrypted Text:", decrypted.decode())
```

---

## 📚 Functions & Concepts Learned

### 1. **String Functions**
- `split("\n")`: Splits a string at each newline character.
- `"".join(...)`: Joins all elements of an iterable into a single string.

### 2. **File Handling**
- `open("file_name.type", "mode")`: Opens a file in the specified mode.
- `with open(...) as f:`: Context manager for safe file handling.
- `.write(...)`: Writes content to a file.
- `.encode()`: Converts a string to UTF-8 bytes.
- `bytes.fromhex()`: Converts a hex string into bytes.
