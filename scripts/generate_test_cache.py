#! /usr/bin/env python3
import struct
import os
import zlib
import io

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
    The file includes a total length and a CRC32 checksum in its header.
    All fields are written in little-endian format.

    Args:
        filename (str): The name of the output binary file.
        entries (list): A list of dictionaries, where each dictionary contains
                        'key', 'data', and 'data_type' keys.
    """
    print(f"Writing to file: {filename}")
    entry_count = len(entries)

    try:
        # Use an in-memory buffer to build the main content of the file first.
        # This allows us to calculate its size and CRC32 before writing the final file.
        with io.BytesIO() as buffer:
            # Write the entry count to the buffer first.
            buffer.write(struct.pack('<I', entry_count))

            # Now, iterate through each entry and write its data to the buffer.
            for entry in entries:
                key = entry['key'].encode('utf-8')
                data_type = entry['data_type']

                # Based on the data type, pack the data into its binary representation.
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

                # Write the entry header: key_length, data_length, and data_type.
                buffer.write(struct.pack('<I', key_length))
                buffer.write(struct.pack('<I', data_length))
                buffer.write(struct.pack('<B', data_type)) # Data type is a single byte

                # The payload is the key, a null byte, and the data bytes.
                payload = key + b'\x00' + data_bytes
                buffer.write(payload)

            # --- Finalization Step ---
            # Get the complete content from the buffer.
            main_content = buffer.getvalue()

            # Calculate the CRC32 checksum on the main content.
            crc32_checksum = zlib.crc32(main_content)

            # The "total_length" is the size of the CRC field + the size of the main content.
            total_length = 4 + len(main_content)

            # Now, write the complete file to disk.
            with open(filename, 'wb') as f:
                # Write the main file header.
                f.write(struct.pack('<I', MAGIC_VALUE))
                f.write(struct.pack('<I', total_length))
                f.write(struct.pack('<I', crc32_checksum))

                # Write the buffered content (entry count + all entries).
                f.write(main_content)

        print(f"Successfully wrote {entry_count} entries to {filename}")

    except (IOError, ValueError) as e:
        print(f"An error occurred while writing the file: {e}")


def verify_file(filename):
    """
    Reads the generated file, verifies its integrity using the length and CRC32 fields,
    and prints its contents to verify correctness.
    All fields are read in little-endian format.
    """
    print("\n--- Verifying file contents ---")
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        with open(filename, 'rb') as f:
            # Read the magic number and total length from the header.
            magic = struct.unpack('<I', f.read(4))[0]
            total_length_from_header = struct.unpack('<I', f.read(4))[0]

            print(f"Magic Number: {hex(magic)} ({repr(struct.pack('<I', magic).decode('ascii'))})")
            print(f"Expected Magic: {hex(MAGIC_VALUE)}")
            print(f"Total Length field: {total_length_from_header}")

            # Read the entire rest of the file, which should correspond to the total_length.
            remaining_data = f.read()
            if len(remaining_data) != total_length_from_header:
                print(f"Error: Length mismatch! Header says {total_length_from_header}, but actual remaining size is {len(remaining_data)}.")
                return
            else:
                print("Total length check: PASSED")

            # The remaining data contains the CRC and the main content. Let's unpack them.
            stored_crc32 = struct.unpack('<I', remaining_data[:4])[0]
            data_to_check = remaining_data[4:]

            # Verify CRC32. The checksum is calculated on the content *after* the CRC field.
            calculated_crc32 = zlib.crc32(data_to_check)
            print(f"Stored CRC32: {hex(stored_crc32)}")
            print(f"Calculated CRC32: {hex(calculated_crc32)}")
            if stored_crc32 != calculated_crc32:
                print("Error: CRC32 mismatch! File may be corrupt.")
                return
            else:
                print("CRC32 check: PASSED")

            # Use a memory buffer to read the entries from the data we already have in memory.
            with io.BytesIO(data_to_check) as buffer:
                entry_count = struct.unpack('<I', buffer.read(4))[0]
                print(f"Entry Count: {entry_count}")
                print("-" * 20)

                # Read and print each entry.
                for i in range(entry_count):
                    key_length = struct.unpack('<I', buffer.read(4))[0]
                    data_length = struct.unpack('<I', buffer.read(4))[0]
                    data_type = struct.unpack('<B', buffer.read(1))[0]

                    # The payload includes the key, a null byte, and the data.
                    payload_length = key_length + 1 + data_length
                    payload = buffer.read(payload_length)

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
        {'key': 'Bootcache Test Five', 'data': 0xC0DEBAD0, 'data_type': DATA_TYPE_U32},
        {'key': 'raid6_best_algo', 'data': 'neonx4', 'data_type': DATA_TYPE_STRING},
        {'key': 'xor_blocks_fastest', 'data': '8regs', 'data_type': DATA_TYPE_STRING}
    ]

    output_file = "cache_output.bin"

    # Run the writer function.
    write_cache_file(output_file, data_to_write)

    # Verify the contents of the generated file.
    verify_file(output_file)

