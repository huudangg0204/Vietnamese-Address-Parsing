import pandas as pd
from tranform_module import combine_address_strings, generate_tsv_column, map_row_to_output_format, AdminUnitIDMapper
import os
import json

# Bước 1: Cấu hình đường dẫn
INPUT_EXCEL_FILE = "extracted_addresses_output.xlsx"
OUTPUT_CSV_FILE = "converted_output.csv"
JSON_ADMIN_FILE = "Stage_1/full_json_generated_data_vn_units.json"  # Đường dẫn tới file JSON chứa dữ liệu hành chính

# Bước 2: Tạo danh sách địa chỉ từ file Excel
combined_addresses = combine_address_strings(INPUT_EXCEL_FILE)

# Bước 3: Đọc lại file Excel để trích xuất các cột hành chính
df = pd.read_excel(INPUT_EXCEL_FILE)

# Thêm cột "Address" từ danh sách đã kết hợp
df["Address"] = combined_addresses

# Bước 4: Tạo cột TSV bằng hàm generate_tsv_column
df["tsv"] = df["Address"].apply(lambda addr: generate_tsv_column(addr.lower()))

# Bước 5: Khởi tạo admin_mapper
admin_mapper = AdminUnitIDMapper(JSON_ADMIN_FILE)

# Bước 6: Sinh output với format yêu cầu (giống file D_data_address.csv)
output_rows = []
for idx, row in df.iterrows():
    mapped_row = map_row_to_output_format(row.to_dict(), admin_mapper, current_id=idx + 1)
    mapped_row["tsv"] = row["tsv"]
    output_rows.append(mapped_row)

# Bước 7: Ghi kết quả ra file CSV
output_df = pd.DataFrame(output_rows)

# Sắp xếp lại các cột giống D_data_address.csv (bỏ timestamp)
columns_order = ['id', 'street_id', 'ward_id', 'district_id', 'city_id', 'country_id', 'full_address', 'tsv']
output_df = output_df[columns_order]
output_df.to_csv(OUTPUT_CSV_FILE, index=False)

print(f" Đã tạo file CSV: {OUTPUT_CSV_FILE}")
