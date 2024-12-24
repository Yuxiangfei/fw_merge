
import sys
import os
import time
from intelhex import intelhex_class
import file_process



if __name__ == "__main__":

    print('hex_merge version V1.01')

    print("当前路径 —> %s" % os.getcwd())

    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    elif __file__:
        current_path = os.path.dirname(__file__)

    date = time.strftime("%Y-%m-%d", time.localtime())

    json_path = current_path + '/merge_setting.json'

    load_json = file_process.get_json_content(json_path)

    boot_path = current_path + load_json['boot_file_path']
    app_path = current_path + load_json['app_file_path']

    boot_start_address = int(load_json['boot_start_address'], 16)
    boot_size = int(load_json['boot_size'], 16)

    app_start_address = int(load_json['app_start_address'], 16)
    app_size = int(load_json['app_size'], 16)

    app_version_address = int(load_json['app_version_address'], 16)
    app_version_size = int(load_json['app_version_size'], 16)
    app_version_prefix = load_json['app_version_prefix']

    app_crc_start_address = int(load_json['app_crc_start_address'], 16)
    app_crc_size = int(load_json['app_crc_size'], 16)
    app_crc_save_address = int(load_json['app_crc_save_address'], 16)

    number_in_record = int(load_json['number_in_record'], 16)

    vendor_name = load_json['vendor_name']
    model_name = load_json['model_name']

    fw_upgrade = int(load_json['fw_upgrade'], 16)
    Hw_Rev_Min = int(load_json['Hw_Rev_Min'], 16)

    target_folder_path = current_path
    target_folder_path += '/'
    target_folder_path += date
    is_exist = os.path.exists(target_folder_path)
    if not is_exist:
        os.makedirs(target_folder_path)
        print(target_folder_path + ' create successfully')
    else:
        print(target_folder_path + ' has exist')


    #create intelhex object
    boot_hex = intelhex_class(boot_start_address, boot_size)
    app_hex = intelhex_class(app_start_address, app_size)

    print('boot hex start address is : ' + hex(boot_start_address) + ' size is : ' + hex(boot_size))
    print('app hex start address is : ' + hex(app_start_address) + ' size is : ' + hex(app_size))

    #read hex file and add crc32 in app file
    boot_hex.read_hex_file(boot_path)
    app_hex.read_hex_file(app_path)
    version_string = app_hex.get_version(app_version_address, app_version_size, 0)

    print('app version start address is : ' + hex(app_version_address) + ' size is : ' + hex(app_version_size))
    print('app version is : ' + version_string)

    app_hex.add_crc(app_crc_save_address, app_crc_start_address)
    print('app crc save address is : ' + hex(app_crc_save_address))

    target_file_path = target_folder_path
    target_file_path += '/'
    target_file_path += app_version_prefix
    target_file_path += version_string


    app_bin_path = target_file_path + '.bin'

    # output app bin file

    # pri: 1;  sec:2;  pri+sec:3
    if fw_upgrade == 2:
        sec_offset = 0x0000
    else:
        sec_offset = app_hex.get_bin_size()
    
    app_hex.add_header_info(fw_upgrade, fw_upgrade, Hw_Rev_Min, sec_offset, vendor_name, model_name)
    app_hex.write_header_in_bin(app_bin_path)
    app_hex.append_bin_file(app_bin_path)

    # output boot+app merge hex
    merge_hex_path = target_file_path + '.hex'
    print(merge_hex_path)
    boot_hex.write_hex_file_default(merge_hex_path, number_in_record, True)
    app_hex.append_hex_file_default(merge_hex_path, number_in_record, True)
    app_hex.end_hex_file(merge_hex_path)

    #input("输入任意键结束")

    # call exe program method 1
    #win32api.ShellExecute(0, 'open', exe_path, exe_parameters_string, '', 1)

    # call exe program method 2
    #if os.path.exists(exe_path):
    #    p = subprocess.Popen(exe_path + ' ' + exe_parameters_string)























