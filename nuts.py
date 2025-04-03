import binascii, sys, struct

# Define the byte sequences to search for
item_id_sequence = b'\x49\x74\x65\x6D\x49\x64'
int_property_sequence = b'\x49\x6E\x74\x50\x72\x6F\x70\x65\x72\x74\x79'
num_sequence = b'\x4E\x75\x6D'

# Function to read the hex data from a file
def read_hex_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

# Function to write the modified hex data to a new file
def write_hex_file(file_path, hex_data):
    with open(file_path, 'wb') as file:
        file.write(hex_data)

# Function to find and modify the byte sequence in the hex data
def modify_hex_data(hex_data):
    # Find all occurrences of the ItemId sequence
    item_id_offset = 0
    modifications = []

    while True:
        item_id_offset = hex_data.find(item_id_sequence, item_id_offset)
        if item_id_offset == -1:
            break

        # Skip ahead 5 bytes
        int_property_offset = item_id_offset + 6 + 5
        if hex_data[int_property_offset:int_property_offset + len(int_property_sequence)] != int_property_sequence:
            item_id_offset += 1  # Move to the next byte to continue searching
            continue

        # Skip ahead 10 bytes and check the next byte
        year_offset = int_property_offset + len(int_property_sequence) + 10
        #year_value = hex_data[year_offset]
        year_value = struct.unpack('<I', hex_data[year_offset:year_offset + 4])[0]
        if year_value < 1950 or year_value > 1979:
            item_id_offset += 1  # Move to the next byte to continue searching
            continue
        # Skip ahead 7 bytes
        num_offset = year_offset + 1 + 7
        if hex_data[num_offset:num_offset + len(num_sequence)] != num_sequence:
            item_id_offset += 1  # Move to the next byte to continue searching
            continue
        # Skip ahead 5 bytes
        int_property_offset_2 = num_offset + len(num_sequence) + 5
        if hex_data[int_property_offset_2:int_property_offset_2 + len(int_property_sequence)] != int_property_sequence:
            item_id_offset += 1  # Move to the next byte to continue searching
            continue

        # Skip ahead 10 bytes and set the next byte to 63
        target_offset = int_property_offset_2 + len(int_property_sequence) + 10
        previous_value = hex_data[target_offset]
        hex_data = hex_data[:target_offset] + b'\x63' + hex_data[target_offset + 1:]

        modifications.append((target_offset, previous_value, 0x63))

        # Move to the next byte to continue searching
        item_id_offset += 1

    return hex_data, modifications
if len(sys.argv) <= 1:
    print("Needs file path argument!")
else:
    # Example usage
    input_file_path = sys.argv[1] # Replace with the actual file path
    output_file_path = sys.argv[1] + "~"  # Replace with the desired output file path

    hex_data = read_hex_file(input_file_path)
    modified_hex_data, modifications = modify_hex_data(hex_data)
    print(f"Modification done: {len(modifications)} changes")
    if modified_hex_data:
        write_hex_file(output_file_path, modified_hex_data)
        for offset, previous_value, new_value in modifications:
            print(f"Modification successful at offset: {offset}")
            print(f"Previous value: {previous_value}")
            print(f"New value: {new_value}")
input("Press Enter to exit...")
