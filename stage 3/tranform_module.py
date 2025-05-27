import pandas as pd
import json
from unidecode import unidecode
import os

class AdminUnitIDMapper:
    """
    Lớp để tải và ánh xạ tên đơn vị hành chính sang ID từ file JSON.
    ID được lấy từ trường 'Code' trong JSON.
    """
    def __init__(self, json_filepath):
        self.json_filepath = json_filepath
        self.provinces_df = pd.DataFrame()
        self.districts_df = pd.DataFrame()
        self.wards_df = pd.DataFrame()
        self._load_and_flatten_data()

    def _normalize_name(self, name_str):
        if not name_str or not isinstance(name_str, str):
            return ""
        normalized = unidecode(name_str).lower()
        prefixes = ["thanh pho ", "tp ", "tinh ", "quan ", "q ", "huyen ", "h ",
                    "phuong ", "p ", "xa ", "x ", "thi tran ", "tt "]
        for p in prefixes:
            if normalized.startswith(p):
                normalized = normalized[len(p):]
        return normalized.strip().replace('-', ' ')

    def _load_and_flatten_data(self):
        try:
            with open(self.json_filepath, 'r', encoding='utf-8') as f:
                raw_data_list = json.load(f)
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file JSON: {self.json_filepath}")
            return
        except json.JSONDecodeError:
            print(f"Lỗi: File JSON không hợp lệ: {self.json_filepath}")
            return

        provinces_list = []
        districts_list = []
        wards_list = []

        for province_data in raw_data_list:
            if province_data.get("Type") == "province":
                prov_code = province_data.get("Code")
                prov_name = province_data.get("Name")
                provinces_list.append({
                    'id': int(prov_code) if prov_code and prov_code.isdigit() else None,
                    'name': prov_name,
                    'normalized_name': self._normalize_name(prov_name)
                })

                if "District" in province_data and isinstance(province_data["District"], list):
                    for district_data in province_data["District"]:
                        dist_code = district_data.get("Code")
                        dist_name = district_data.get("Name")
                        dist_prov_code = district_data.get("ProvinceCode")
                        districts_list.append({
                            'id': int(dist_code) if dist_code and dist_code.isdigit() else None,
                            'name': dist_name,
                            'normalized_name': self._normalize_name(dist_name),
                            'province_id': int(dist_prov_code) if dist_prov_code and dist_prov_code.isdigit() else None,
                        })

                        if "Ward" in district_data and isinstance(district_data["Ward"], list):
                            for ward_data in district_data["Ward"]:
                                ward_code = ward_data.get("Code")
                                ward_name = ward_data.get("Name")
                                ward_dist_code = district_data.get("DistrictCode", dist_code) # Ưu tiên Ward.DistrictCode
                                
                                wards_list.append({
                                    'id': int(ward_code) if ward_code and ward_code.isdigit() else None,
                                    'name': ward_name,
                                    'normalized_name': self._normalize_name(ward_name),
                                    'district_id': int(ward_dist_code) if ward_dist_code and ward_dist_code.isdigit() else None,
                                })
        
        self.provinces_df = pd.DataFrame(provinces_list).drop_duplicates(subset=['id']).dropna(subset=['id'])
        self.districts_df = pd.DataFrame(districts_list).drop_duplicates(subset=['id']).dropna(subset=['id'])
        self.wards_df = pd.DataFrame(wards_list).drop_duplicates(subset=['id']).dropna(subset=['id'])

    def get_city_id(self, province_name_excel):
        if self.provinces_df.empty or pd.isna(province_name_excel) or province_name_excel == "":
            return None
        norm_name = self._normalize_name(province_name_excel)
        match = self.provinces_df[self.provinces_df['normalized_name'] == norm_name]
        return match['id'].iloc[0] if not match.empty else None

    def get_district_id(self, district_name_excel, city_id_from_json):
        if self.districts_df.empty or pd.isna(district_name_excel) or district_name_excel == "" or city_id_from_json is None:
            return None
        norm_name = self._normalize_name(district_name_excel)
        match = self.districts_df[
            (self.districts_df['normalized_name'] == norm_name) &
            (self.districts_df['province_id'] == city_id_from_json)
        ]
        return match['id'].iloc[0] if not match.empty else None

    def get_ward_id(self, ward_name_excel, district_id_from_json):
        if self.wards_df.empty or pd.isna(ward_name_excel) or ward_name_excel == "" or district_id_from_json is None:
            return None
        norm_name = self._normalize_name(ward_name_excel)
        match = self.wards_df[
            (self.wards_df['normalized_name'] == norm_name) &
            (self.wards_df['district_id'] == district_id_from_json)
        ]
        return match['id'].iloc[0] if not match.empty else None


def combine_address_strings(excel_filepath):
    """
    Đọc file Excel và tạo danh sách các chuỗi địa chỉ được kết hợp.
    Địa chỉ = duong + px_cat + px + qh_cat + qh + tinh_cat + tinh.

    Args:
        excel_filepath (str): Đường dẫn đến file extracted_addresses_output.xlsx.

    Returns:
        list: Danh sách các chuỗi địa chỉ đã được kết hợp.
              Trả về list rỗng nếu có lỗi.
    """
    if not os.path.exists(excel_filepath):
        print(f"Lỗi: File Excel '{excel_filepath}' không tìm thấy.")
        return []
    try:
        df = pd.read_excel(excel_filepath)
    except Exception as e:
        print(f"Lỗi khi đọc file Excel '{excel_filepath}': {e}")
        return []

    combined_addresses = []
    
    # Định nghĩa các cột cần thiết
    # Đảm bảo các tên cột này khớp với file Excel
    cols_for_concat = ["duong", "px_cat", "px", "qh_cat", "qh", "tinh_cat", "tinh"]
    
    for col in cols_for_concat:
        if col not in df.columns:
            print(f"Cảnh báo: Cột '{col}' không tìm thấy trong file Excel. Sẽ được bỏ qua trong việc tạo chuỗi địa chỉ.")

    for _, row in df.iterrows():
        parts = []
        for col_name in cols_for_concat:
            if col_name in row and pd.notna(row[col_name]):
                parts.append(str(row[col_name]).strip())
        
        # Chỉ thêm vào nếu có ít nhất một phần tử khác rỗng
        if any(part for part in parts):
            combined_addresses.append(" ".join(filter(None, parts)))
        else:
            combined_addresses.append("") # Thêm chuỗi rỗng nếu tất cả các phần đều rỗng/NaN
            
    return combined_addresses


def map_row_to_output_format(input_row_data, admin_mapper_instance, current_id, country_id=1):
    
    tinh_name = input_row_data.get('tinh')
    qh_name = input_row_data.get('qh')
    px_name = input_row_data.get('px')
    full_address_original = input_row_data.get('Address', "") # Lấy từ cột 'Address' gốc

    city_id = admin_mapper_instance.get_city_id(tinh_name)
    district_id = admin_mapper_instance.get_district_id(qh_name, city_id) if city_id else None
    ward_id = admin_mapper_instance.get_ward_id(px_name, district_id) if district_id else None
    
    street_id = None # không có thông tin về đường trong csdl

    return {
        'id': current_id,
        'street_id': street_id,
        'ward_id': ward_id,
        'district_id': district_id,
        'city_id': city_id,
        'country_id': country_id,
        'full_address': full_address_original
    }


def generate_tsv_column(normalized_address_string):
    """
    Tạo chuỗi TSV từ một chuỗi địa chỉ đã được chuẩn hóa.

    Args:
        normalized_address_string (str): Chuỗi địa chỉ đã được chuẩn hóa               (chữ thường, bỏ dấu phẩy/chấm, khoảng trắng đơn,
                                          đã qua add_norm).
    Returns:
        str: Chuỗi TSV.
    """
    if not normalized_address_string or not isinstance(normalized_address_string, str):
        return ""

    words = normalized_address_string.split()
    lexemes_positions = {}

    for i, word in enumerate(words):
        # Loại bỏ dấu tiếng Việt và đảm bảo chữ thường
        lexeme = unidecode(word).lower()
        
        # Bỏ qua các từ rỗng hoặc quá ngắn (có thể tùy chỉnh)
        # Ví dụ: bỏ qua từ 1 chữ cái (trừ khi nó là số)
        if not lexeme or (len(lexeme) < 2 and not lexeme.isdigit()):
            continue

        if lexeme not in lexemes_positions:
            lexemes_positions[lexeme] = []
        # Vị trí trong TSV thường bắt đầu từ 1
        lexemes_positions[lexeme].append(str(i + 1) + 'A') 

    tsv_parts = []
    # Sắp xếp các lexeme theo thứ tự bảng chữ cái để đảm bảo tính nhất quán của output
    for lexeme, positions in sorted(lexemes_positions.items()):
        tsv_parts.append(f"'{lexeme}':{','.join(positions)}")
    
    return ' '.join(tsv_parts)

