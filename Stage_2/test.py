import pandas as pd # address_module sử dụng pandas để đọc chuanhoa.csv
from address_module import load_address_dict, update_entity_address
import os

def main():
    # 1. Xác định đường dẫn
    # Giả sử script này nằm cùng thư mục với address_module.py và thư mục generated_json
    project_path = "." 
    dir_name = "Stage_1/generated_json" # Thư mục chứa các file JSON và chuanhoa.csv

    print(f"Đường dẫn dự án (tương đối): {project_path}")
    print(f"Thư mục dữ liệu: {dir_name}")
    print(f"Đường dẫn đầy đủ đến thư mục dữ liệu: {os.path.abspath(os.path.join(project_path, dir_name))}")

    # 2. Tải các từ điển địa chỉ
    try:
        print("Đang tải các từ điển địa chỉ...")
        add_dicts = load_address_dict(project_path, dir_name)
        print("Đã tải xong các từ điển địa chỉ.")
    except FileNotFoundError as e:
        print(f"Lỗi không tìm thấy file khi tải từ điển: {e}")
        print(f"Hãy đảm bảo file 'chuanhoa.csv' và các file JSON cần thiết nằm trong thư mục: '{os.path.abspath(os.path.join(project_path, dir_name))}'")
        return
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn khi tải từ điển: {e}")
        return

    # 3. Chuẩn bị một vài địa chỉ mẫu để kiểm tra
    sample_addresses = [
        "p110 - b1 , phố hoàng tích trí , quận đống đa , hn"

    ]

    # 4. Xử lý từng địa chỉ
    print("\nBắt đầu xử lý các địa chỉ mẫu:")
    for i, address_str in enumerate(sample_addresses):
        print(f"\n--- Địa chỉ {i+1}: \"{address_str}\" ---")
        
        # Đầu vào cho update_entity_address phải là một dictionary
        # với key 'address' và giá trị là một list các chuỗi địa chỉ.
        entity_input = {'address': [address_str]}
        
        try:
            # Gọi hàm xử lý chính
            # processed_result_dict chính là entity_input được cập nhật
            processed_result_dict, name_map_dict = update_entity_address(entity_input, add_dicts)
            
            # Hiển thị kết quả
            # Các giá trị trả về là list một phần tử, nên ta lấy phần tử đầu tiên [0]
            print(f"  Tỉnh/Thành phố: {processed_result_dict.get('tinh', [None])[0]} (Loại: {processed_result_dict.get('tinh_cat', [None])[0]})")
            print(f"  Quận/Huyện:    {processed_result_dict.get('qh', [None])[0]} (Loại: {processed_result_dict.get('qh_cat', [None])[0]})")
            print(f"  Phường/Xã:     {processed_result_dict.get('px', [None])[0]} (Loại: {processed_result_dict.get('px_cat', [None])[0]})")
            print(f"  Đường:           {processed_result_dict.get('duong', [None])[0]}")
            print(f"  Phần còn lại:  {processed_result_dict.get('Address_ch', [None])[0]}")
            
        except Exception as e:
            print(f"  Lỗi khi xử lý địa chỉ này: {e}")
            import traceback
            traceback.print_exc() # In chi tiết lỗi để debug

if __name__ == "__main__":
    main()