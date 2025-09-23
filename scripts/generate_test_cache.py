#! /usr/bin/env python3
import struct
import os

# Define the magic number as per the C preprocessor definition, but in little-endian.
# 'E' 'H' 'C' 'B'
MAGIC_VALUE = int.from_bytes(b'EHCB', 'little')

# Constants to represent data types, which will be written to the file
# as an 8-bit unsigned integer.
DATA_TYPE_STRING = 0
DATA_TYPE_U32 = 1
DATA_TYPE_U16 = 2
DATA_TYPE_U8 = 3

def write_cache_file(filename, entries):
    """
    Writes a binary file containing a series of cache entries with a variable-length key
    and variable-type data, formatted to be compatible with the C structs.
    All fields are now written in little-endian format.

    Args:
        filename (str): The name of the output binary file.
        entries (list): A list of dictionaries, where each dictionary contains
                        'key', 'data', and 'data_type' keys.
    """
    print(f"Writing to file: {filename}")
    entry_count = len(entries)

    try:
        with open(filename, 'wb') as f:
            # Write the main cache header: magic number and entry count (little-endian).
            f.write(struct.pack('<I', MAGIC_VALUE))
            f.write(struct.pack('<I', entry_count))

            # Now, iterate through each entry and write its data.
            for entry in entries:
                key = entry['key'].encode('utf-8')
                data_type = entry['data_type']
                
                # Based on the data type, pack the data into its binary representation.
                # The data itself is already in little-endian format.
                if data_type == DATA_TYPE_STRING:
                    data_bytes = entry['data'].encode('utf-8')
                elif data_type == DATA_TYPE_U32:
                    data_bytes = struct.pack('<I', entry['data'])
                elif data_type == DATA_TYPE_U16:
                    data_bytes = struct.pack('<H', entry['data'])
                elif data_type == DATA_TYPE_U8:
                    data_bytes = struct.pack('<B', entry['data'])
                else:
                    raise ValueError(f"Unknown data type: {data_type}")

                key_length = len(key)
                data_length = len(data_bytes)

                # Write the key_length, data_length, and data_type (all little-endian).
                f.write(struct.pack('<I', key_length))
                f.write(struct.pack('<I', data_length))
                f.write(struct.pack('<B', data_type)) # Data type is a single byte

                # The payload is the key, a null byte, and the data bytes.
                payload = key + b'\x00' + data_bytes
                f.write(payload)

        print(f"Successfully wrote {entry_count} entries to {filename}")

    except IOError as e:
        print(f"An error occurred while writing the file: {e}")

def verify_file(filename):
    """
    Reads the generated file and prints its contents to verify correctness.
    All fields are now read in little-endian format.
    """
    print("\n--- Verifying file contents ---")
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        with open(filename, 'rb') as f:
            # Read the main header first.
            magic = struct.unpack('<I', f.read(4))[0]
            entry_count = struct.unpack('<I', f.read(4))[0]

            print(f"Magic Number: {hex(magic)} ({repr(struct.pack('<I', magic).decode('ascii'))})")
            print(f"Expected Magic: {hex(MAGIC_VALUE)}")
            print(f"Entry Count: {entry_count}")
            print("-" * 20)

            # Read and print each entry.
            for i in range(entry_count):
                key_length = struct.unpack('<I', f.read(4))[0]
                data_length = struct.unpack('<I', f.read(4))[0]
                data_type = struct.unpack('<B', f.read(1))[0]
                
                # Calculate the total payload size and read it.
                payload_length = key_length + 1 + data_length
                payload = f.read(payload_length)

                # Split the payload into the key and data.
                key = payload[:key_length].decode('utf-8')
                data_bytes = payload[key_length + 1:]

                print(f"Entry {i + 1}:")
                print(f"  Key: '{key}'")
                print(f"  Key Length: {key_length}")
                print(f"  Data Type: {data_type}")

                # Unpack the data bytes based on the type.
                if data_type == DATA_TYPE_STRING:
                    data = data_bytes.decode('utf-8')
                    print(f"  Data: '{data}'")
                elif data_type == DATA_TYPE_U32:
                    data = struct.unpack('<I', data_bytes)[0]
                    print(f"  Data (u32): {data}")
                elif data_type == DATA_TYPE_U16:
                    data = struct.unpack('<H', data_bytes)[0]
                    print(f"  Data (u16): {data}")
                elif data_type == DATA_TYPE_U8:
                    data = struct.unpack('<B', data_bytes)[0]
                    print(f"  Data (u8): {data}")
                
                print(f"  Data Length: {data_length}")
                print("-" * 20)

    except (IOError, struct.error) as e:
        print(f"An error occurred while reading the file: {e}")

if __name__ == "__main__":
    # Sample data demonstrating the different types.
    data_to_write = [
        {'key': 'string_key', 'data': 'This is some sample string data.', 'data_type': DATA_TYPE_STRING},
        {'key': 'u32_key', 'data': 4294967295, 'data_type': DATA_TYPE_U32}, # Max value for u32
        {'key': 'u16_key', 'data': 65535, 'data_type': DATA_TYPE_U16},     # Max value for u16
        {'key': 'u8_key', 'data': 255, 'data_type': DATA_TYPE_U8},         # Max value for u8
        {'key': 'another_string', 'data': 'Another piece of data.', 'data_type': DATA_TYPE_STRING},
        {'key': 'a_long_key', 'data': 12345, 'data_type': DATA_TYPE_U32},
        {'key': 'Bootcache Test One', 'data': 1234, 'data_type': DATA_TYPE_U32},
        {'key': 'Bootcache Test Two', 'data': 5678, 'data_type': DATA_TYPE_U32},
        {'key': 'Bootcache Test Three', 'data': 9012, 'data_type': DATA_TYPE_U32},
        {'key': 'Bootcache Test Four', 'data': 0xDEADBEEF, 'data_type': DATA_TYPE_U32},
        {'key': 'Bootcache Test Five', 'data': 0xC0DEBAD0, 'data_type': DATA_TYPE_U32}
    ]

    output_file = "cache_output.bin"
    
    # Run the writer function.
    write_cache_file(output_file, data_to_write)

    # Verify the contents of the generated file.
    verify_file(output_file)

