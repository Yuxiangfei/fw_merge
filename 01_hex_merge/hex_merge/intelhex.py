
import os
import binfile
from crc32 import crc32_class



class intelhex_class:

    def __init__(self, start_address = 0x08004000, address_size = 0xE000, byte_num_per_address = 1, blank_char = 0xFF):
        self.start_address = start_address
        self.address_size = address_size
        self.byte_num_per_address = byte_num_per_address
        self.hex_high_address = (self.start_address >> 16) & 0xFFFF
        self.hex_low_address = self.start_address & 0xFFFF
        self.hex_crc = crc32_class(True)

        # used_address is out range of used address
        self.used_address = self.start_address
        self.bin_data = []
        self.blank_char = blank_char
        self.crc = 0x00
        for i in range(self.address_size * self.byte_num_per_address):
            self.bin_data.append(self.blank_char)
        #print('hex bin data buffer is ' + hex(i + 1))

        # write size must be a multiple of 1k (0x400)
        self.bin_multiple_min = 0x400
        self.header_data = []
        for j in range(self.bin_multiple_min):
            self.header_data.append(0x00)



    #create a record string by a hex record
    def record_hex2str(self, record):
        record_str = ':'
        #print(record)
        for hex_num in record:
            record_str += ''.join('%02X' % hex_num)
        record_str += '\n'
        return record_str


    def record_str2hex(self, record_str):
        record_hex = []
        record_len = len(record_str.rstrip())
        for i in range(1, record_len, 2):
            hex_digit = '0x' + record_str[i: i+2]
            record_hex.append(int(hex_digit, 16))
        #print(record_hex)
        return record_hex


    #calculate checksum for a hex record
    def record_checksum(self, record):
        hex_sum = 0
        for hex_num in record:
            hex_sum += hex_num
        checksum = 256 - (hex_sum % 256)
        return ((checksum % 256) & 0xFF)               #return value must be a byte


    #parse record string and save into bin data
    def parse_record(self, record_str, start_address, end_address):
        if record_str[0] != ':':
            return False

        #parse record string to hex record
        record_hex = self.record_str2hex(record_str)
        length = len(record_hex)

        #parse record
        if record_hex[3] == 0x04:
            self.hex_high_address = 256 * record_hex[4] + record_hex[5]
            #print("this record is a Extended Linear Address Record( the 16 bits higher in 32bit address)")
        elif record_hex[3] == 0x00:
            self.hex_low_address = 256 * record_hex[1] + record_hex[2]
            absolute_address = (self.hex_high_address << 16) + self.hex_low_address
            #print(hex(absolute_addrss))

            for i in range(4, length - 1, self.byte_num_per_address):
                if start_address <= absolute_address <= end_address:
                    bin_data_offset = self.byte_num_per_address * (absolute_address - self.start_address)
                    if self.byte_num_per_address == 2:
                        self.bin_data[bin_data_offset] = record_hex[i] & 0xFF
                        self.bin_data[bin_data_offset + 1] = record_hex[i + 1] & 0xFF

                        if((self.bin_data[bin_data_offset] == 0xFF) and (self.bin_data[bin_data_offset + 1] == 0xFF)):
                            is_0xFF = True
                        else:
                            is_0xFF = False
                        # print(self.bin_data[bin_data_offset])
                        # print(self.bin_data[bin_data_offset + 1])
                    else:
                        self.bin_data[bin_data_offset] = record_hex[i] & 0xFF
                        if(self.bin_data[bin_data_offset - 1] == 0xFF):
                            is_0xFF = True
                        else:
                            is_0xFF = False
                        # print(self.bin_data[bin_data_offset])
                absolute_address += 1

                if(is_0xFF == False):
                    self.used_address = absolute_address
                #print("this record is a Data Record")
        #else:
            #print("this record is a not parse Record : " + record_str)

        return True


    #create hex record according bin data corresponding to address
    def create_record(self, start_address, end_address, number_in_record, record_address, is_lite = True):
        hex_str = ''
        address_high = record_address // 65536
        address_low = record_address % 65536

        # for Extended Linear Address Record
        if (record_address == start_address) or (address_low == 0):
            address_record = [0x02, 0x00, 0x00, 0x04]
            address_record.append(address_high // 256)
            address_record.append(address_high % 256)
            address_record.append(self.record_checksum(address_record))
            hex_str += self.record_hex2str(address_record)

        #for Data Record
        data_record = []
        data_0xff_counter = 0
        data_num = min(number_in_record, self.byte_num_per_address * (end_address + 1 - record_address))
        data_record.append(data_num)
        data_record.append(address_low // 256)
        data_record.append(address_low % 256)
        data_record.append(0x00)
        bin_data_offset = self.byte_num_per_address * (record_address - self.start_address)
        for i in range(data_num):
            data_record.append(self.bin_data[bin_data_offset + i])
            if(self.bin_data[bin_data_offset + i] == 0xFF):
                data_0xff_counter += 1
            else:
                data_0xff_counter = 0

        data_record.append(self.record_checksum(data_record))
        hex_str += self.record_hex2str(data_record)

        # print(hex_str)
        if((is_lite) and (data_0xff_counter == data_num)):
            hex_str = ''
            # print(‘data is full 0xFF, need not write in hex file’)

        #print(hex_str)
        return hex_str

    def read_hex_file(self, file_path):
        start_address = self.start_address
        end_address = self.start_address + self.address_size - 1
        with open(file_path, 'r') as file:
            for record_str in file.readlines():
                self.parse_record(record_str, start_address, end_address)
            file.close()

        # write size must be a multiple of 1k (0x400)
        self.used_address += (self.bin_multiple_min //self.byte_num_per_address - self.used_address % (self.bin_multiple_min //self.byte_num_per_address))

        #print(self.bin_data)

    def write_bin_file(self, file_path, is_lite = True):
        start_address = self.start_address
        end_address = self.used_address

        print("the bin file data is in range [" + hex(start_address) + "," + hex(end_address - 1) + "] size is:" + hex(end_address - start_address))

        if(is_lite == True):
            write_bin = self.bin_data[(start_address - self.start_address):(end_address - self.start_address)]
            binfile.write(file_path, write_bin)
        else:
            write_bin = self.bin_data[(start_address - self.start_address):]
            binfile.write(file_path, write_bin)

    def append_bin_file(self, file_path, is_lite = True):
        start_address = self.start_address
        end_address = self.used_address

        print("the bin file data is in range [" + hex(start_address) + "," + hex(end_address - 1) + "] size is:" + hex(end_address - start_address))

        if(is_lite == True):
            write_bin = self.bin_data[(start_address - self.start_address):(end_address - self.start_address)]
            binfile.append(file_path, write_bin)
        else:
            write_bin = self.bin_data[(start_address - self.start_address):]
            binfile.append(file_path, write_bin)

    def write_hex_file_default(self, file_path, number_in_record, is_lite = True):
        start_address = self.start_address
        end_address = self.start_address + self.address_size - 1
        self.write_hex_file(file_path, start_address, end_address, number_in_record, is_lite)


    def append_hex_file_default(self, file_path, number_in_record, is_lite = True):
        start_address = self.start_address
        end_address = self.used_address + (number_in_record - self.used_address % number_in_record)
        self.append_hex_file(file_path, start_address, end_address, number_in_record, is_lite)


    def write_hex_file(self, file_path, start_address, end_address, number_in_record, is_lite = True):
        hex_str = ''
        #create hex record according bin data corresponding to address
        address_number_in_record = number_in_record // self.byte_num_per_address
        for record_address in range(start_address, end_address, address_number_in_record):
            hex_str += self.create_record(start_address, end_address, number_in_record, record_address, is_lite)

        #write hex_str into file
        with open(file_path, 'w') as file:
            file.write(hex_str)
            file.close()

    def append_hex_file(self, file_path, start_address, end_address, number_in_record, is_lite = True):
        hex_str = ''
        #create hex record according bin data corresponding to address
        address_number_in_record = number_in_record // self.byte_num_per_address
        for record_address in range(start_address, end_address, address_number_in_record):
            hex_str += self.create_record(start_address, end_address, number_in_record, record_address, is_lite)

        #append hex_str into file
        with open(file_path, 'a+') as file:
            file.write(hex_str)
            file.close()


    def add_crc(self, write_address, start_address):
        
        end_address = self.used_address
        
        # end_address is out range of array
        bin_size = self.byte_num_per_address * (end_address - start_address)
        
        start_index = (start_address - self.start_address) * self.byte_num_per_address
        end_index = bin_size + start_index
        
        print("start_index is" + hex(start_index))
        print("end_index is" + hex(end_index))

        crc_save_offset = self.byte_num_per_address * (write_address - self.start_address)
        self.bin_data[crc_save_offset + 4] = bin_size & 0xFF
        self.bin_data[crc_save_offset + 5] = (bin_size >> 8) & 0xFF
        self.bin_data[crc_save_offset + 6] = (bin_size >> 16) & 0xFF
        self.bin_data[crc_save_offset + 7] = (bin_size >> 24) & 0xFF

        self.crc = self.hex_crc.get_list_crc(self.bin_data[start_index : end_index], bin_size)

        self.bin_data[crc_save_offset] = self.crc & 0xFF
        self.bin_data[crc_save_offset + 1] = (self.crc >> 8) & 0xFF
        self.bin_data[crc_save_offset + 2] = (self.crc >> 16) & 0xFF
        self.bin_data[crc_save_offset + 3] = (self.crc >> 24) & 0xFF

        print("the crc of bin data in range [" + hex(start_address) + "," + hex(self.used_address) + "] is: " \
              + hex(self.crc) + ", the crc size is:" + hex(bin_size))
        # Note: this crc size is not make sense, just cater to real boot rule

    def end_hex_file(self, file_path):
        end_str = ':00000001FF'
        with open(file_path, 'a+') as file:
            file.write(end_str)
            file.close()


    def get_version(self, version_address, string_size, number_size):
        version_string = ''
        version_size = string_size + number_size
        version_offset = version_address - self.start_address
        for data in self.bin_data[version_offset : version_offset + string_size]:
            version_string += chr(data)

        for data in self.bin_data[version_offset + string_size : version_offset + version_size]:
            #version_string += hex(data).join('%02X'%data)[2::].upper()
            version_string += ''.join('%02X' % data).upper()

        #print(version_string)
        return version_string

    def get_bin_size(self):
        return (self.byte_num_per_address * (self.used_address - self.start_address))

    def add_header_info(self, image_Fw, updated_Fw, Hw_Rev, sec_offset, vendor_name = '', model_name = ''):

        self.header_data[0] = image_Fw
        self.header_data[1] = updated_Fw
        self.header_data[6] = Hw_Rev << 2

        #print(vendor_name)
        for i in range(len(vendor_name)):
            self.header_data[9 + i] = ord(vendor_name[i])

        offset_zoom = (sec_offset // self.bin_multiple_min)
        
        # self.used_address is out range of array
        bin_size_1k = (self.byte_num_per_address * (self.used_address - self.start_address)) // self.bin_multiple_min

        self.header_data[17] =  (bin_size_1k % 256) & 0xFF
        self.header_data[18] =  (bin_size_1k // 256) & 0xFF
        
        self.header_data[19] = (offset_zoom % 256) & 0xFF
        self.header_data[20] =  (offset_zoom // 256) & 0xFF

        #print(model_name)
        for i in range(len(model_name)):
            self.header_data[21 + i] = ord(model_name[i])

        #print(self.header_data[0 : 33])

        for j in range(self.bin_multiple_min - 32):
            self.header_data[32 + j] = 0xFF

    def write_header_in_bin(self, file_path):
        binfile.write(file_path, self.header_data)


if __name__ == "__main__":
     print("当前路径 —> %s" % os.getcwd())
    # current_path = os.path.dirname(__file__)
    # boot_path = current_path + '/test_folder/SP600_BOOT.hex'
    # app_path = current_path + '/test_folder/SP600_APP.hex'
    # merge_path = current_path + '/test_folder/SP600_BOOT_APP.hex'
    #
    # boot_hex = intelhex_class(0x08000000, 0x2000)
    # app_hex = intelhex_class(0x08002000, 0x7000)
    #
    # boot_hex.read_hex_file(boot_hex)
    # boot_hex.write_hex_file(merge_path, 0x10)
    #
    # app_hex.read_hex_file(app_path)
    # app_hex.add_crc(0x08008FFC)
    # app_hex.get_version(0x08008FE0, 16)
    # app_hex.write_hex_file(merge_path, 0x10, True)
    # app_hex.end_hex_file(merge_path)


