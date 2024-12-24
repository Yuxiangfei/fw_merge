import sys
import os
import time
import binfile


def get_files_by_type(path, extension):
    """
    获取指定路径下所有具有指定扩展名的文件。

    :param path: 文件夹路径
    :param extension: 文件扩展名，例如 '.txt', '.py'
    :return: 文件列表
    """
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(extension)]


if __name__ == "__main__":

    print('hex_merge version V1.01')

    print("当前路径 —> %s" % os.getcwd())

    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    elif __file__:
        current_path = os.path.dirname(__file__)

    files = get_files_by_type(current_path, '.bin')
    #print(files)

    if (2 == len(files)):

        file1name = os.path.splitext(os.path.basename(files[0]))[0]
        file2name = os.path.splitext(os.path.basename(files[1]))[0]

        #print(file1name)
        #print(file2name)

        fileD2Aname = ""
        fileD2Dname = ""

        index = file1name.find("D2A")   # 如果找到子串，返回开始的索引；如果没有找到，返回-1
        if index != -1:
            fileD2Aname = file1name
            fileD2Apath = files[0]
            index = file2name.find("D2D")
            if index != -1:
                fileD2Dname = file2name
                fileD2Dpath = files[1]
        else:
            index = file2name.find("D2A")
            if index != -1:
                fileD2Aname = file2name
                fileD2Apath = files[1]
                index = file1name.find("D2D")
                if index != -1:
                    fileD2Dname = file1name
                    fileD2Dpath = files[0]

        if (len(fileD2Aname) > 0) and (len(fileD2Dname) > 0):
            pass
        else:
            print("file is error")

        target_file_path = current_path
        target_file_path += '/'
        target_file_path += fileD2Aname[0:len(fileD2Aname) - 12]
        target_file_path += "MERGE_"
        target_file_path += fileD2Aname[-8:]
        target_file_path += "_"
        target_file_path += fileD2Dname[-8:]
        target_file_path += ".bin"
        #print(target_file_path)

        D2A_bin_list = []
        D2D_bin_list = []
        binfile.read(fileD2Apath, D2A_bin_list)
        binfile.read(fileD2Dpath, D2D_bin_list)

        print(D2A_bin_list[0:31])
        print(D2D_bin_list[0:31])

        D2A_bin_list[0] = 3
        D2A_bin_list[1] = 3

        #d2a_size_kbyte = (D2A_bin_list[17] + D2A_bin_list[18] * 256) - 1
        d2d_size_kbyte = (D2D_bin_list[17] + D2D_bin_list[18] * 256)

        D2A_bin_list[17] += d2d_size_kbyte & 0x00FF
        D2A_bin_list[18] += (d2d_size_kbyte >> 8) & 0x00FF
        #D2A_bin_list[19] = d2d_size_kbyte & 0x00FF
        #D2A_bin_list[20] = (d2d_size_kbyte >> 8) & 0x00FF

        binfile.write(target_file_path, D2A_bin_list)
        binfile.append(target_file_path, D2D_bin_list[1024:])

        print(D2A_bin_list[0:31])
        print(d2d_size_kbyte)

    else:
        print("bin file number is error")










