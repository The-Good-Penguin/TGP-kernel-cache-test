#! /usr/bin/env python3
import struct
import os
import zlib
import io
import shutil
import argparse

# --- CONSTANTS ---
MAGIC_VALUE = int.from_bytes(b'EHCB', 'little')

DATA_TYPE_STRING = 0
DATA_TYPE_U32 = 1
DATA_TYPE_U16 = 2
DATA_TYPE_U8 = 3

# Base directory for simulation (the 'parent' of storage)
SYSFS_DIR_SIM_BASE = "bootcache_sysfs_sim_base"

DEFAULT_OUTPUT_FILE = "cache_from_sysfs_output.bin"

# --- HELPER FUNCTIONS ---

def hex_dump(key, data, assumed_type_id):
    """
    Prints data in a hex/ASCII format (xxd-like), assuming a fixed type for the header.
    """
    print(f"\n--- Key: '{key}' (Size: {len(data)} bytes) ---")
    
    data_type_str = "u8 / Raw Byte Stream"
    if len(data) == 1:
        try:
            data_value = struct.unpack('<B', data)[0]
            data_type_str = f"u8 (Value: {data_value})"
        except struct.error:
            pass

    print(f"  Assumed Type ID: {assumed_type_id} ({data_type_str})")
    
    # Hex dump formatting
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        if len(chunk) < 16:
            hex_str += '   ' * (16 - len(chunk))
        
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        
        print(f"{i:08x}: {hex_str:<48}  {ascii_str}")
    print("-" * 60)


def simulate_sysfs_directory(base_dir):
    """
    Creates the simulated structure: base_dir/count and base_dir/storage/*
    """
    print(f"\n--- Setting up SIMULATION in: {base_dir} ---")
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    storage_dir = os.path.join(base_dir, "storage")
    os.makedirs(storage_dir, exist_ok=True)

    sample_data = [
        {'key': 'string_key', 'raw': 'This is some string.'.encode('utf-8')},
        {'key': 'u32_key', 'raw': struct.pack('<I', 0xDEADBEEF)},
        {'key': 'u16_key', 'raw': struct.pack('<H', 0xC0DE)},
        {'key': 'u8_key', 'raw': struct.pack('<B', 0xFF)},
        {'key': 'raid6_best_algo', 'raw': 'neonx4'.encode('utf-8')},
        {'key': 'null_byte_string', 'raw': 'A\x00B'.encode('utf-8')},
    ]

    # Write the 'count' file in the base_dir
    with open(os.path.join(base_dir, 'count'), 'w') as f:
        f.write(str(len(sample_data)))

    # Write the key files inside the storage_dir
    for entry in sample_data:
        filename = os.path.join(storage_dir, entry['key'])
        with open(filename, 'wb') as f:
            f.write(entry['raw'])
    
    print(f"Simulated {len(sample_data)} entries created.")
    return storage_dir # Return the path to the storage directory


def write_final_cache_file(filename, entries, entry_count):
    """
    Assembles the final binary file with Magic, Total Length, and CRC32,
    and DUMPS the final header information for debugging.
    """
    
    try:
        with io.BytesIO() as buffer:
            # Main Content Start: Entry Count
            buffer.write(struct.pack('<I', entry_count))

            for entry in entries:
                key = entry['key'].encode('utf-8')
                data_bytes = entry['data_bytes']
                data_type = entry['data_type']
                data_length = entry['data_length']

                key_length = len(key)

                # Write Entry Header: key_length, data_length, data_type
                buffer.write(struct.pack('<I', key_length))
                buffer.write(struct.pack('<I', data_length))
                buffer.write(struct.pack('<B', data_type)) 

                # Write Payload: Key + Null Byte Separator + Data
                payload = key + b'\x00' + data_bytes
                buffer.write(payload)

            # Finalization Step
            main_content = buffer.getvalue()
            crc32_checksum = zlib.crc32(main_content)
            total_length = 4 + len(main_content) 

            # Write file to disk
            with open(filename, 'wb') as f:
                f.write(struct.pack('<I', MAGIC_VALUE))
                f.write(struct.pack('<I', total_length))
                f.write(struct.pack('<I', crc32_checksum))
                f.write(main_content)

        # --- FINAL HEADER DEBUGGING OUTPUT ---
        magic_value_int = MAGIC_VALUE
        magic_bytes = struct.pack('<I', magic_value_int).decode('ascii')
        
        print(f"\n--- Writing final cache file: {filename} ---")
        print(f"Successfully wrote {entry_count} entries to {filename}.")
        print("\n### FINAL FILE HEADER DUMP (Little Endian) ###")
        
        print(f"* Magic Value:     {magic_value_int:<10} (0x{magic_value_int:08x} | {magic_bytes})")
        print(f"* Total Length:    {total_length} bytes (0x{total_length:08x})")
        print(f"* CRC32 Checksum:  {crc32_checksum:<10} (0x{crc32_checksum:08x} Calculated over main content)")
        print("-" * 40)

    except (IOError, ValueError, struct.error) as e:
        print(f"An error occurred while writing the file: {e}")


# --- CORE LOGIC ---

def generate_cache_from_sysfs(source_dir, output_filename):
    """
    Scans the storage directory (key files), reads count from its parent, 
    and generates the final binary cache file.
    """
    print(f"\n--- Starting Cache Generation from {source_dir} (All Data Assumed U8) ---")
    
    # The 'count' file lives in the base directory
    count_dir = source_dir
    storage_dir = os.path.join(source_dir, 'storage')
    
    entries = []
    
    # 1. Read the entry count from the parent directory
    count_file = os.path.join(count_dir, 'count')
    try:
        with open(count_file, 'r') as f:
            expected_count = int(f.read().strip())
    except Exception as e:
        print(f"Error reading or parsing entry count from '{count_file}': {e}")
        return

    # 2. Iterate over key files in the storage_dir
    all_files = os.listdir(storage_dir)
    key_files = sorted([f for f in all_files if f != 'count' and os.path.isfile(os.path.join(storage_dir, f))])

    if len(key_files) != expected_count:
        print(f"Warning: Expected {expected_count} entries (from '{count_file}'), but found {len(key_files)} data files.")

    for filename in key_files:
        key = filename
        filepath = os.path.join(storage_dir, filename)
        
        with open(filepath, 'rb') as f:
            data_bytes = f.read()

        data_length = len(data_bytes)
        data_type = DATA_TYPE_U8 # Fixed assumption

        hex_dump(key, data_bytes, data_type)
        
        entries.append({
            'key': key,
            'data_bytes': data_bytes,
            'data_type': data_type,
            'data_length': data_length
        })

    # 3. Generate the final binary file
    write_final_cache_file(output_filename, entries, expected_count)


# --- ARGUMENT PARSING AND EXECUTION ---

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Generate bootcache binary file from a /sysfs directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--source-dir',
        type=str,
        default=SYSFS_DIR_SIM_BASE,
        help=(
            "The directory containing the key/data files (e.g., the '/sys/kernel/bootcache' directory).\n"
            f"Defaults to the simulated path: '{SYSFS_DIR_SIM_BASE}'."
        )
    )

    parser.add_argument(
        '--output-file',
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=(
            "The name/path of the final output binary cache file.\n"
            f"Defaults to: '{DEFAULT_OUTPUT_FILE}'."
        )
    )
    
    args = parser.parse_args()
    source_dir = args.source_dir
    output_file = args.output_file
    is_simulation = source_dir == SYSFS_DIR_SIM_BASE
    
    # 1. Conditional Simulation/Setup
    if is_simulation:
        # We need to run the simulation against the base directory, 
        # but tell the parser to look at the nested 'storage' directory.
        simulate_sysfs_directory(SYSFS_DIR_SIM_BASE)
        print("Running in SIMULATION MODE.")
    else:
        # Live mode: Check for existence and validity
        # Check if the count file exists in the inferred parent directory
        count_file_path = os.path.join(source_dir, 'count')
        
        if not os.path.isdir(source_dir):
            print(f"Error: Source directory '{source_dir}' not found or is not a directory.")
            exit(1)
        if not os.path.exists(count_file_path):
            print(f"Error: Required 'count' file not found: '{count_file_path}'.")
            exit(1)
        print(f"Running in LIVE MODE, reading from storage: {source_dir}")

    # 2. Generate the cache from the chosen source directory
    generate_cache_from_sysfs(source_dir, output_file)

    # 3. Clean up the simulated directory only
    if is_simulation and os.path.exists(SYSFS_DIR_SIM_BASE):
        shutil.rmtree(SYSFS_DIR_SIM_BASE)