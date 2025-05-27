import pandas as pd
import os
import re 
from address_module import load_address_dict, update_entity_address 

# --- CONFIGURATION ---
# Đường dẫn đến file Excel input
INPUT_EXCEL_FILE = "address_full_0712.xlsx"
# Tên file Excel output
OUTPUT_EXCEL_FILE = "extracted_addresses_output.xlsx" 
# Tên cột trong file Excel input chứa địa chỉ đầy đủ
ADDRESS_COLUMN_NAME = "Address" # << THAY ĐỔI NẾU CỘT ĐỊA CHỈ CỦA BẠN CÓ TÊN KHÁC

# Đường dẫn tương đối đến thư mục gốc của dự án (nơi chứa address_module.py)
PROJECT_PATH = "." 
# Tên thư mục chứa các file JSON và chuanhoa.csv
GENERATED_JSON_DIR_NAME = "Stage_1/generated_json"
# --- END CONFIGURATION ---

def main():
    # 1. Tải các từ điển địa chỉ
    print("Đang tải các từ điển địa chỉ...")
    try:
        add_dicts = load_address_dict(PROJECT_PATH, GENERATED_JSON_DIR_NAME)
        print("Đã tải xong các từ điển địa chỉ.")
    except FileNotFoundError as e:
        print(f"Lỗi không tìm thấy file khi tải từ điển: {e}")
        print(f"Hãy đảm bảo file 'chuanhoa.csv' và các file JSON cần thiết nằm trong thư mục: '{os.path.abspath(os.path.join(PROJECT_PATH, GENERATED_JSON_DIR_NAME))}'")
        return
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn khi tải từ điển: {e}")
        return

    # 2. Đọc file Excel input
    if not os.path.exists(INPUT_EXCEL_FILE):
        print(f"Lỗi: File input '{INPUT_EXCEL_FILE}' không tìm thấy tại '{os.path.abspath(INPUT_EXCEL_FILE)}'.")
        return
    
    print(f"Đang đọc file input: {INPUT_EXCEL_FILE}...")
    try:
        df_input = pd.read_excel(INPUT_EXCEL_FILE)
    except Exception as e:
        print(f"Lỗi khi đọc file Excel '{INPUT_EXCEL_FILE}': {e}")
        return

    if ADDRESS_COLUMN_NAME not in df_input.columns:
        print(f"Lỗi: Cột địa chỉ '{ADDRESS_COLUMN_NAME}' không tìm thấy trong file input.")
        print(f"Các cột hiện có trong file: {df_input.columns.tolist()}")
        print("Vui lòng kiểm tra và cập nhật biến ADDRESS_COLUMN_NAME trong script.")
        return

    # 3. Chuẩn bị danh sách để lưu kết quả
    output_data = []
    total_rows = len(df_input)
    print(f"Bắt đầu xử lý {total_rows} địa chỉ...")

    # 4. Lặp qua từng hàng (địa chỉ) trong DataFrame input
    for index, row in df_input.iterrows():
        original_address = row[ADDRESS_COLUMN_NAME]
        
        # Kiểm tra nếu địa chỉ là NaN, None hoặc chuỗi rỗng
        if pd.isna(original_address) or not isinstance(original_address, str) or not original_address.strip():
            print(f"Hàng {index + 2}: Địa chỉ rỗng hoặc không hợp lệ. Bỏ qua.")
            # Thêm một hàng với các giá trị None để giữ cấu trúc
            result_row = {'Address': original_address}
            for col in ['tinh', 'tinh_cat', 'qh', 'qh_cat', 'px', 'px_cat', 'duong', 'Address_ch']:
                result_row[col] = None
            output_data.append(result_row)
            continue

        # Tạo entity_dict đầu vào cho hàm xử lý
        entity_input = {'address': [original_address]}
        
        try:
            # Gọi hàm xử lý chính từ address_module
            processed_entity_dict, _ = update_entity_address(entity_input, add_dicts)
            
            # Trích xuất kết quả
            # Giá trị trả về từ update_entity_address là list một phần tử
            result_row = {
                'Address': original_address,
                'tinh': processed_entity_dict.get('tinh', [None])[0],
                'tinh_cat': processed_entity_dict.get('tinh_cat', [None])[0],
                'qh': processed_entity_dict.get('qh', [None])[0],
                'qh_cat': processed_entity_dict.get('qh_cat', [None])[0],
                'px': processed_entity_dict.get('px', [None])[0],
                'px_cat': processed_entity_dict.get('px_cat', [None])[0],
                'duong': processed_entity_dict.get('duong', [None])[0],
                'Address_ch': processed_entity_dict.get('Address_ch', [None])[0]
            }
            output_data.append(result_row)

        except Exception as e:
            print(f"Lỗi khi xử lý địa chỉ ở hàng {index + 2} ('{original_address}'): {e}")
            # Trong trường hợp lỗi, ghi lại địa chỉ gốc và thông báo lỗi
            result_row = {'Address': original_address, 'Error_Processing': str(e)}
            for col in ['tinh', 'tinh_cat', 'qh', 'qh_cat', 'px', 'px_cat', 'duong', 'Address_ch']:
                if col not in result_row: result_row[col] = None
            output_data.append(result_row)
        
        if (index + 1) % 100 == 0: # In tiến độ mỗi 100 dòng
            print(f"Đã xử lý {index + 1}/{total_rows} địa chỉ...")

    print(f"Hoàn tất xử lý {total_rows} địa chỉ.")

    # 5. Tạo DataFrame từ danh sách kết quả
    df_output = pd.DataFrame(output_data)
    
    # Sắp xếp lại các cột theo thứ tự mong muốn
    output_columns = ['Address', 'tinh', 'tinh_cat', 'qh', 'qh_cat', 'px', 'px_cat', 'duong', 'Address_ch', 'Error_Processing']
    # Chỉ giữ lại các cột có trong df_output để tránh lỗi nếu cột 'Error_Processing' không tồn tại
    df_output = df_output.reindex(columns=[col for col in output_columns if col in df_output.columns])

    # 6. Ghi DataFrame kết quả ra file Excel
    print(f"Đang ghi kết quả ra file: {OUTPUT_EXCEL_FILE}...")
    try:
        df_output.to_excel(OUTPUT_EXCEL_FILE, index=False)
        print(f"Đã ghi thành công file output: {os.path.abspath(OUTPUT_EXCEL_FILE)}")
    except Exception as e:
        print(f"Lỗi khi ghi file Excel '{OUTPUT_EXCEL_FILE}': {e}")

if __name__ == "__main__":
    main()
