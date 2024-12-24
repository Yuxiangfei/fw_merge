import os
import struct



def write(file_path, data_list):
    with open(file_path, 'wb') as file:
        for data in data_list:
            bin_data = struct.pack('B', data)
            file.write(bin_data)
            #print(bin_data.hex())
        file.close()

def append(file_path, data_list):
    with open(file_path, 'ab+') as file:
        for data in data_list:
            bin_data = struct.pack('B', data)
            file.write(bin_data)
            #print(bin_data.hex())
        file.close()


def read(file_path, data_list):
    with open(file_path, 'rb') as file:
        file_size = os.path.getsize(file_path)
        for i in range(file_size):
            bin_data = file.read(1)
            dec_data = struct.unpack('B', bin_data)
            data_list.append(dec_data[0])
            #print(hex(dec_data[0]))
        file.close()

