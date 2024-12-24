import os


# Normal 0x04C11DB7
def crc32_table_generate(crc_table):
    #print("this is crc normal table")
    for i in range(256):
        crc = i << 24
        for j in range(8):
            if(crc & 0x80000000):
                crc = (crc << 1) ^ 0x04C11DB7
            else:
                crc = crc << 1
        crc_table.append(crc)
        #print(hex(crc_table[i]))


# Reversed 0xEDB88320
def crc32_reversed_table_generate(crc_table):
    #print("this is crc normal table")
    for i in range(256):
        crc = i
        for j in range(8):
            if(crc & 0x00000001):
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc = crc >> 1
        crc_table.append(crc)
        #print(hex(crc_table[i]))



class crc32_class:

    def __init__(self, is_reversed = False):
        self.is_reversed = is_reversed;
        self.crc_table = []
        if self.is_reversed == True:
            crc32_reversed_table_generate(self.crc_table)
        else:
            crc32_table_generate(self.crc_table)


    def get_normal_crc(self, data, crc):
        crc = self.crc_table[data ^ (crc >> 24) & 0xFF] ^ (crc << 8)
        return crc


    def get_reversed_crc(self, data, crc):
        crc = self.crc_table[(crc ^ data) & 0xFF] ^ (crc >> 8)
        return crc


    def get_list_crc(self, data_list, size, crc = 0xFFFFFFFF):
        for index in range(size):
            if self.is_reversed == True:
                crc = self.get_reversed_crc(data_list[index] & 0xFF, crc)
            else:
                crc = self.get_normal_crc(data_list[index] & 0xFF, crc)
        
        if self.is_reversed == True:
            return crc ^ 0xFFFFFFFF
        else:
            # print(crc)
            return crc



if __name__ == "__main__":
    crc32_test = crc32_class()
    crc32_reserve_test = crc32_class(True)

    bin_data = []
    bin_data.append(0x01)
    bin_data.append(0x01)
    bin_data.append(0x01)
    bin_data.append(0x01)

    crc32 = crc32_reserve_test.get_list_crc(bin_data, 4)
    print(hex(crc32))






