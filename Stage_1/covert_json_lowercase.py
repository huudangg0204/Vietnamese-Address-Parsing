import os
import json

def convert_json_to_lowercase_recursive(data):
    """
    Hàm đệ quy để chuyển đổi tất cả các chuỗi trong cấu trúc JSON (dict, list)
    thành chữ thường. Áp dụng cho cả keys (nếu là chuỗi) và values (nếu là chuỗi).
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = key.lower() if isinstance(key, str) else key
            new_dict[new_key] = convert_json_to_lowercase_recursive(value)
        return new_dict
    elif isinstance(data, list):
        return [convert_json_to_lowercase_recursive(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        # Giữ nguyên các kiểu dữ liệu khác (số, boolean, None)
        return data

def process_json_files_in_directory(directory_path):
    """
    Duyệt qua tất cả các file .json trong thư mục và các thư mục con,
    chuyển đổi nội dung của chúng thành chữ thường và ghi đè lại.
    """
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                print(f"Đang xử lý file: {filepath}")
                try:
                    # Đọc file JSON
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    # Chuyển đổi nội dung sang chữ thường
                    converted_content = convert_json_to_lowercase_recursive(content)
                    
                    # Ghi lại nội dung đã chuyển đổi vào file gốc
                    # indent=2 (hoặc 4) để file JSON vẫn dễ đọc
                    # ensure_ascii=False để giữ lại các ký tự tiếng Việt
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(converted_content, f, ensure_ascii=False, indent=2)
                    print(f"Đã chuyển đổi và ghi đè thành công: {filepath}")

                except json.JSONDecodeError:
                    print(f"LỖI: Không thể giải mã JSON trong file: {filepath}. Bỏ qua file này.")
                except Exception as e:
                    print(f"LỖI: Đã xảy ra lỗi không mong muốn khi xử lý file {filepath}: {e}. Bỏ qua file này.")

if __name__ == "__main__":
    # Đường dẫn đến thư mục chứa các file JSON của bạn
    # Thay đổi đường dẫn này nếu cầny
    target_directory = r"c:\Users\Windows\Desktop\DS108\Lab\Lab 5\generated_json"
    
    if not os.path.isdir(target_directory):
        print(f"LỖI: Thư mục '{target_directory}' không tồn tại.")
    else:
        print(f"Bắt đầu quá trình chuyển đổi file JSON trong thư mục: {target_directory}")
        # Xác nhận trước khi chạy để tránh ghi đè không mong muốn
        confirm = input(f"CẢNH BÁO: Script này sẽ ghi đè lên các file JSON trong '{target_directory}'.\nBạn có chắc chắn muốn tiếp tục không? (yes/no): ")
        if confirm.lower() == 'yes':
            process_json_files_in_directory(target_directory)
            print("Hoàn tất quá trình chuyển đổi.")
        else:
            print("Quá trình chuyển đổi đã bị hủy.")