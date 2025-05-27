import pandas as pd
import numpy as np
import csv
import json
import re
import os


class AddObj(object):
    pass


def ch_xlsx_to_csv(project_path, dir_name):
    dir_path = os.path.join(project_path, dir_name)
    ch = pd.read_excel(os.path.join(dir_path, 'chuanhoa.xlsx'))
    ch.to_csv(os.path.join(dir_path, 'chuanhoa.csv'), index=False)

# Hàm phụ để đọc file JSON với encoding UTF-8
def load_json_utf8(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_address_dict(project_path, dir_name): #dir_name: thư mục chứa địa chỉ hành chính
    # load path
    dir_path = os.path.join(project_path, dir_name)
    # create obj to store data
    add_dicts = AddObj()

    # qh_px
    add_dicts.huyen_phuong   = load_json_utf8(os.path.join(dir_path, 'px', 'huyen_phuong.json'))
    add_dicts.huyen_thitran  = load_json_utf8(os.path.join(dir_path, 'px', 'huyen_thitran.json'))
    add_dicts.huyen_xa       = load_json_utf8(os.path.join(dir_path, 'px', 'huyen_xa.json'))
    add_dicts.quan_phuong    = load_json_utf8(os.path.join(dir_path, 'px', 'quan_phuong.json'))
    add_dicts.quan_thitran   = load_json_utf8(os.path.join(dir_path, 'px', 'quan_thitran.json'))
    add_dicts.quan_xa        = load_json_utf8(os.path.join(dir_path, 'px', 'quan_xa.json'))
    add_dicts.tp_phuong      = load_json_utf8(os.path.join(dir_path, 'px', 'tp_phuong.json'))
    add_dicts.tp_thitran     = load_json_utf8(os.path.join(dir_path, 'px', 'tp_thitran.json'))
    add_dicts.tp_xa          = load_json_utf8(os.path.join(dir_path, 'px', 'tp_xa.json'))
    add_dicts.tx_phuong      = load_json_utf8(os.path.join(dir_path, 'px', 'tx_phuong.json'))
    add_dicts.tx_thitran     = load_json_utf8(os.path.join(dir_path, 'px', 'tx_thitran.json'))
    add_dicts.tx_xa          = load_json_utf8(os.path.join(dir_path, 'px', 'tx_xa.json'))

    # qh_tinh
    add_dicts.thanhpho_huyen = load_json_utf8(os.path.join(dir_path, 'qh', 'thanhpho_huyen.json'))
    add_dicts.thanhpho_quan  = load_json_utf8(os.path.join(dir_path, 'qh', 'thanhpho_quan.json'))
    add_dicts.tinh_huyen     = load_json_utf8(os.path.join(dir_path, 'qh', 'tinh_huyen.json'))
    add_dicts.tinh_quan      = load_json_utf8(os.path.join(dir_path, 'qh', 'tinh_quan.json'))
    add_dicts.tinh_tp        = load_json_utf8(os.path.join(dir_path, 'qh', 'tinh_tp.json'))
    add_dicts.tinh_tx        = load_json_utf8(os.path.join(dir_path, 'qh', 'tinh_tx.json'))

    # HCM + HN
    add_dicts.hcm_hn_huyen   = load_json_utf8(os.path.join(dir_path, 'hcmhn', 'hcm_hn_huyen.json'))
    add_dicts.hcm_hn_quan    = load_json_utf8(os.path.join(dir_path, 'hcmhn', 'hcm_hn_quan.json'))
    add_dicts.hcm_hn_tx      = load_json_utf8(os.path.join(dir_path, 'hcmhn', 'hcm_hn_tx.json'))
    add_dicts.hcm_hn_tp      = load_json_utf8(os.path.join(dir_path, 'hcmhn', 'hcm_hn_tp.json'))

    # qh_duong
    add_dicts.qh_d           = load_json_utf8(os.path.join(dir_path, 'qh_duong.json'))

    # chuan hoa
    add_dicts.chuanhoa       = pd.read_csv(os.path.join(dir_path, 'chuanhoa.csv'), header=None, encoding='utf-8')
    return add_dicts


def city_district(data, dict_data, text1, text2):
    # Tim thành phố/tỉnh - huyện/quận/thị xã/thành phố
    for key, values in dict_data.items():
        # key = key +' ' không có trường hợp bắt sai tên tỉnh vd vinhome không bắt vinh
        # kiem tra ten tinh
        if (key + ' ') in (data['Address_ch'][-16:] + ' '):
            if data['t_check'] != 1:
                data['t_check'] = 1
                data['tinh'] = key
                data['tinh_cat'] = text1
                data['Address_ch'] = data['Address_ch'].replace(text1+ ' ' + key, '')
        # kiem tra co huyen khong
        for value in values:
            # tránh trường hợp bắt sai với các quận có số
            value_search = value
            if len(value) <= 2 and text2 == 'quận': 
                value_search = "quận " + value

            if (value_search + ' ') in (data['Address_ch'][-22:] + ' '):
                if data['h_check'] != 1:
                    data['qh'] = value
                    data['qh_cat'] = text2
                    data['h_check'] = 1
                    data['Address_ch'] = data['Address_ch'].replace(value, '')
                # neu khong co tinh thi fill tinh
                if data['t_check'] != 1:
                    data['tinh'] = key
                    data['tinh_cat'] = text1
                    data['t_check'] = 1
                    data['Address_ch'] = data['Address_ch'].replace(key, '')
    return data


def district_ward(data, dict_data, text1):
    # kiem tra co phường/xã/thị trấn khong
    if data['h_check'] == 1:
        for key_1, values_1 in dict_data.items():
            if data['qh'] == key_1:
                for value_1 in values_1:
                    # tránh trường hợp bắt sai với các phường có số
                    # chỉ có phuong mới có số
                    value_1_search = value_1
                    if len(value_1) <= 2 and text1 == 'phường':
                        value_1_search = "phường " + value_1
                    if (value_1_search + ' ') in (data['Address_ch'] + ' '):
                        data['Address_ch'] = data['Address_ch'].replace(value_1_search, '')
                        data['px'] = value_1
                        data['px_cat'] = text1
    return data


def district_street(data, dict_data):
    # kiem tra co duong khong
    if data['h_check'] == 1:
        for key_2, values_2 in dict_data.items():
            if data['qh'] == key_2:
                for value_2 in values_2:
                    if (value_2 + ' ') in (data['Address_ch'] + ' '):
                        data['Address_ch'] = data['Address_ch'].replace(value_2, '')
                        data['duong'] = value_2
    return data

#chuẩn hoá bằng regex
def add_norm(data, chuanhoa):
    address = data['Address_ch']
    vietnamese_letters_only = "a-zA-Zàáãạảăắằẳẵặâấầẩẫậèéẹẽẻêếềểễệđìíỉĩịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ"
    for i in range(len(chuanhoa)): 
        abbrev = str(chuanhoa.iloc[i, 0]).strip() 
        # Lấy từ đầy đủ từ cột 1 của hàng thứ i
        full = str(chuanhoa.iloc[i, 1]).strip()   
        # Kiểm tra xem abbrev có rỗng không để tránh lỗi regex
        if not abbrev:
            continue
        # để xử lý các ký tự đặc biệt trong abbrev nếu có
        pattern_abbrev = r'\b' + re.escape(abbrev) + r'\.?(?![%s])' % vietnamese_letters_only
        address = re.sub(pattern_abbrev, full, address, flags=re.IGNORECASE)

     # tạo khonảng trắng giữa chữ và số (vd p12-> phường12 -> phường 12)
     # chữ trước số sau  
    pattern_letter_then_digit = r'([%s]+)(\d+)' % vietnamese_letters_only
    address = re.sub(pattern_letter_then_digit, r'\1 \2', address)
    #  số trước chữ sau
    pattern_digit_then_letter = r'(\d+)([%s]+)' % vietnamese_letters_only
    address = re.sub(pattern_digit_then_letter, r'\1 \2', address)
    # Xóa các ký tự không cần thiết
    address = address.replace(',', '')
    address = address.replace('.', ' ')
    # Chuẩn hóa nhiều khoảng trắng thành một khoảng trắng duy nhất
    address = re.sub(r'\s\s+', ' ', address).strip()

    data['Address_ch'] = address
    return data



def add_proc_1(data, add_dicts):
    # extract
    city_district(data, add_dicts.hcm_hn_huyen, 'thành phố', 'huyện')
    city_district(data, add_dicts.hcm_hn_quan, 'thành phố', 'quận')
    city_district(data, add_dicts.hcm_hn_tx, 'thành phố', 'thị xã')
    city_district(data, add_dicts.hcm_hn_tp, 'thành phố', 'thành phố')  # ---------------update: them
    district_ward(data, add_dicts.huyen_phuong, 'phường')
    district_ward(data, add_dicts.huyen_thitran, 'thị trấn')
    district_ward(data, add_dicts.huyen_xa, 'xã')
    district_ward(data, add_dicts.quan_phuong, 'phường')
    district_ward(data, add_dicts.quan_thitran, 'thị trấn')
    district_ward(data, add_dicts.quan_xa, 'xã')
    district_ward(data, add_dicts.tp_phuong, 'phường')
    district_ward(data, add_dicts.tp_thitran, 'thị trấn')  # ---------------update: them
    district_ward(data, add_dicts.tp_xa, 'xã')
    district_ward(data, add_dicts.tx_phuong, 'phường')
    district_ward(data, add_dicts.tx_thitran, 'thị trấn')  # ---------------update: them
    district_ward(data, add_dicts.tx_xa, 'xã')
    district_street(data, add_dicts.qh_d)
    return data


def add_proc_2(data, add_dicts):
    # TinhHuyen-----ssssssssssssssss
    if data['t_check'] != 1:
        city_district(data, add_dicts.thanhpho_huyen, 'thành phố', 'huyện')
        city_district(data, add_dicts.thanhpho_quan, 'thành phố', 'quận')
        # city_district(data,thanhpho_tx,'thành phố','thị xã')#---------------update: xoa
        city_district(data, add_dicts.tinh_huyen, 'tỉnh', 'huyện')
        city_district(data, add_dicts.tinh_quan, 'tỉnh', 'quận')
        city_district(data, add_dicts.tinh_tp, 'tỉnh', 'thành phố')
        city_district(data, add_dicts.tinh_tx, 'tỉnh', 'thị xã')
        district_ward(data, add_dicts.huyen_phuong, 'phường')
        district_ward(data, add_dicts.huyen_thitran, 'thị trấn')
        district_ward(data, add_dicts.huyen_xa, 'xã')
        district_ward(data, add_dicts.quan_phuong, 'phường')
        district_ward(data, add_dicts.quan_thitran, 'thị trấn')
        district_ward(data, add_dicts.quan_xa, 'xã')
        district_ward(data, add_dicts.tp_phuong, 'phường')
        district_ward(data, add_dicts.tp_thitran, 'thị trấn')  # ---------------update: them
        district_ward(data, add_dicts.tp_xa, 'xã')
        district_ward(data, add_dicts.tx_phuong, 'phường')
        district_ward(data, add_dicts.tx_thitran, 'thị trấn')  # ---------------update: them
        district_ward(data, add_dicts.tx_xa, 'xã')
        district_street(data, add_dicts.qh_d)
    return data


def add_proc_3(data):
    list_xuly = ['mặt đường', "đường lớn", 'thị xã', "thị trấn", 'thành phố', "đường", '-', '( )', 'tt', "trung tâm",
                 "phường", "huyện", "tỉnh", "tx", "tp", "quận", "xã", ]
    if not data['tinh'] is None:
        for j in list_xuly:
            if j in data['Address_ch']:
                data['Address_ch'] = data['Address_ch'].replace(j, "")
        data['Address_ch'] = re.sub(r"\s\s+", " ", data['Address_ch'])
    return data


def update_entity_address(entity_dict, add_dicts):
    add_name_dict_keys = ['tinh', 'tinh_cat', 'qh', 'qh_cat', 'px', 'px_cat', 'duong', 'Address_ch',
                          't_check', 'h_check']
    add_name_dict = dict.fromkeys(add_name_dict_keys)

    data = dict.fromkeys(add_name_dict_keys)
    # for ent_name in add_name_dict_keys: data[ent_name] = []
    long_add = max(entity_dict['address'], key=len)
    data['Address_ch'] = long_add.lower().replace("_", " ")

    # for i, d in enumerate(data): data['Address_ch'][i] = add_norm(data['Address_ch'][i], add_dicts.chuanhoa)

    data = add_norm(data, add_dicts.chuanhoa)
    data = add_proc_1(data, add_dicts)
    data = add_proc_2(data, add_dicts)
    data = add_proc_3(data)

    for ent_name in add_name_dict_keys: entity_dict[ent_name] = []
    for ent_name in add_name_dict_keys: entity_dict[ent_name].append(data[ent_name])

    add_name_dict['Address_ch'] = 'address (còn lại)'
    add_name_dict['tinh_cat'] = 'address (Tỉnh/Thành) prefix'
    add_name_dict['tinh'] = 'address (Tỉnh/Thành)'
    add_name_dict['qh_cat'] = 'address (Quận/Huyện) prefix'
    add_name_dict['qh'] = 'address (Quận/Huyện)'
    add_name_dict['px_cat'] = 'address (Phường/Xã) prefix'
    add_name_dict['px'] = 'address (Phường/Xã)'
    add_name_dict['duong'] = 'address (Đường)'
    return entity_dict, add_name_dict


