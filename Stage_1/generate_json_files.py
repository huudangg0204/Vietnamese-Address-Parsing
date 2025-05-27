#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import logging
import shutil
from collections import defaultdict
from typing import Dict, List, Any, Set
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("json_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("json_generator")

# Constants
INPUT_FILE = "Stage_1/full_json_generated_data_vn_units.json"
OUTPUT_DIR = "Stage_1/generated_json"
SPECIAL_CITIES = {"Hà Nội", "Hồ Chí Minh"}  # Cities treated specially in HCMHN folder


def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def load_master_json(filepath: str) -> List[Dict[str, Any]]:
    """Load and parse the master JSON file."""
    try:
        logger.info(f"Loading master JSON from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded master JSON with {len(data)} provinces")
        return data
    except Exception as e:
        logger.error(f"Failed to load master JSON: {e}")
        raise


def extract_administrative_units(data: List[Dict[str, Any]]) -> Dict:
    """
    Extract and organize administrative units from the master JSON.
    
    Returns:
        Dict containing various mappings required for address_module.py
    """
    logger.info("Extracting administrative units from master JSON")
    
    # Initialize result dictionaries
    result = {
        # District to Ward relationships (px folder)
        'huyen_phuong': defaultdict(list),  # huyện -> phường
        'huyen_thitran': defaultdict(list),  # huyện -> thị trấn
        'huyen_xa': defaultdict(list),       # huyện -> xã
        'quan_phuong': defaultdict(list),    # quận -> phường
        'quan_thitran': defaultdict(list),   # quận -> thị trấn
        'quan_xa': defaultdict(list),        # quận -> xã
        'tp_phuong': defaultdict(list),      # thành phố -> phường
        'tp_thitran': defaultdict(list),     # thành phố -> thị trấn
        'tp_xa': defaultdict(list),          # thành phố -> xã
        'tx_phuong': defaultdict(list),      # thị xã -> phường
        'tx_thitran': defaultdict(list),     # thị xã -> thị trấn
        'tx_xa': defaultdict(list),          # thị xã -> xã
        
        # Province to District relationships (qh folder)
        'thanhpho_huyen': defaultdict(list), # thành phố -> huyện
        'thanhpho_quan': defaultdict(list),  # thành phố -> quận
        'tinh_huyen': defaultdict(list),     # tỉnh -> huyện
        'tinh_quan': defaultdict(list),      # tỉnh -> quận
        'tinh_tp': defaultdict(list),        # tỉnh -> thành phố
        'tinh_tx': defaultdict(list),        # tỉnh -> thị xã
        
        # Special relationships for Hanoi and Ho Chi Minh (hcmhn folder)
        'hcm_hn_huyen': defaultdict(list),   # HN/HCM -> huyện
        'hcm_hn_quan': defaultdict(list),    # HN/HCM -> quận
        'hcm_hn_tx': defaultdict(list),      # HN/HCM -> thị xã
        'hcm_hn_tp': defaultdict(list),      # HN/HCM -> thành phố
        
        # Street information
        'qh_d': defaultdict(list),           # quận/huyện -> đường
    }
    
    # Process each province
    for province in data:
        # Skip invalid entries
        if "Name" not in province or "AdministrativeUnitShortName" not in province:
            logger.warning(f"Skipping province with missing required fields: {province.get('Code', 'Unknown')}")
            continue
            
        province_name = province["Name"]
        province_type = province["AdministrativeUnitShortName"]
        
        # Process districts in this province
        if "District" in province and province["District"] is not None:
            for district in province["District"]:
                # Skip invalid entries
                if "Name" not in district or "AdministrativeUnitShortName" not in district:
                    logger.warning(f"Skipping district with missing required fields in province {province_name}")
                    continue
                    
                district_name = district["Name"]
                district_type = district["AdministrativeUnitShortName"]
                
                # Map province to district based on their types
                if province_name in SPECIAL_CITIES:
                    # Special mapping for Hanoi and Ho Chi Minh
                    if district_type == "Quận":
                        result['hcm_hn_quan'][province_name].append(district_name)
                    elif district_type == "Huyện":
                        result['hcm_hn_huyen'][province_name].append(district_name)
                    elif district_type == "Thị xã":
                        result['hcm_hn_tx'][province_name].append(district_name)
                    elif district_type == "Thành phố":
                        result['hcm_hn_tp'][province_name].append(district_name)
                elif province_type == "Thành phố":
                    if district_type == "Quận":
                        result['thanhpho_quan'][province_name].append(district_name)
                    elif district_type == "Huyện":
                        result['thanhpho_huyen'][province_name].append(district_name)
                elif province_type == "Tỉnh":
                    if district_type == "Quận":
                        result['tinh_quan'][province_name].append(district_name)
                    elif district_type == "Huyện":
                        result['tinh_huyen'][province_name].append(district_name)
                    elif district_type == "Thị xã":
                        result['tinh_tx'][province_name].append(district_name)
                    elif district_type == "Thành phố":
                        result['tinh_tp'][province_name].append(district_name)
                
                # Process wards in this district
                if "Ward" in district and district["Ward"] is not None:
                    for ward in district["Ward"]:
                        # Skip invalid entries
                        if "Name" not in ward or "AdministrativeUnitShortName" not in ward:
                            logger.warning(f"Skipping ward with missing required fields in district {district_name}")
                            continue
                            
                        ward_name = ward["Name"]
                        ward_type = ward["AdministrativeUnitShortName"]
                        
                        # Map district to ward based on their types
                        if district_type == "Huyện":
                            if ward_type == "Phường":
                                result['huyen_phuong'][district_name].append(ward_name)
                            elif ward_type == "Thị trấn":
                                result['huyen_thitran'][district_name].append(ward_name)
                            elif ward_type == "Xã":
                                result['huyen_xa'][district_name].append(ward_name)
                        elif district_type == "Quận":
                            if ward_type == "Phường":
                                result['quan_phuong'][district_name].append(ward_name)
                            elif ward_type == "Thị trấn":
                                result['quan_thitran'][district_name].append(ward_name)
                            elif ward_type == "Xã":
                                result['quan_xa'][district_name].append(ward_name)
                        elif district_type == "Thành phố":
                            if ward_type == "Phường":
                                result['tp_phuong'][district_name].append(ward_name)
                            elif ward_type == "Thị trấn":
                                result['tp_thitran'][district_name].append(ward_name)
                            elif ward_type == "Xã":
                                result['tp_xa'][district_name].append(ward_name)
                        elif district_type == "Thị xã":
                            if ward_type == "Phường":
                                result['tx_phuong'][district_name].append(ward_name)
                            elif ward_type == "Thị trấn":
                                result['tx_thitran'][district_name].append(ward_name)
                            elif ward_type == "Xã":
                                result['tx_xa'][district_name].append(ward_name)
    
    # Convert defaultdicts to regular dicts for JSON serialization
    for key in result:
        result[key] = dict(result[key])
    
    # Count total mappings for logging
    total_mappings = sum(len(values) for mapping in result.values() for values in mapping.values())
    logger.info(f"Extracted {total_mappings} total mappings across all relationship types")
    
    return result


def save_json_files(data: Dict, output_dir: str) -> None:
    """Save the extracted data to separate JSON files."""
    logger.info(f"Saving extracted data to JSON files in {output_dir}")
    
    # Create main directories
    ensure_directory_exists(output_dir)
    ensure_directory_exists(os.path.join(output_dir, "px"))
    ensure_directory_exists(os.path.join(output_dir, "qh"))
    ensure_directory_exists(os.path.join(output_dir, "hcmhn"))
    
    # Save px (district to ward) relationships
    px_keys = [
        'huyen_phuong', 'huyen_thitran', 'huyen_xa',
        'quan_phuong', 'quan_thitran', 'quan_xa',
        'tp_phuong', 'tp_thitran', 'tp_xa',
        'tx_phuong', 'tx_thitran', 'tx_xa'
    ]
    for key in px_keys:
        filepath = os.path.join(output_dir, "px", f"{key}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data[key], f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {key}.json with {len(data[key])} districts")
    
    # Save qh (province to district) relationships
    qh_keys = [
        'thanhpho_huyen', 'thanhpho_quan',
        'tinh_huyen', 'tinh_quan', 'tinh_tp', 'tinh_tx'
    ]
    for key in qh_keys:
        filepath = os.path.join(output_dir, "qh", f"{key}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data[key], f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {key}.json with {len(data[key])} provinces")
      # Save hcmhn (Hanoi and Ho Chi Minh) relationships
    hcmhn_keys = ['hcm_hn_huyen', 'hcm_hn_quan', 'hcm_hn_tx', 'hcm_hn_tp']
    for key in hcmhn_keys:
        # Đảm bảo tên file chính xác cho address_module.py
        actual_filename = key
        filename_for_address_module = key.replace('hcm_hn_', 'hcmhn_')
        
        filepath = os.path.join(output_dir, "hcmhn", f"{actual_filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data[key], f, ensure_ascii=False, indent=2)
            
        # Tạo bản sao với tên cũ cho tương thích
        filepath_compat = os.path.join(output_dir, "hcmhn", f"{filename_for_address_module}.json")
        with open(filepath_compat, 'w', encoding='utf-8') as f:
            json.dump(data[key], f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {key}.json with {len(data[key])} cities")
    
    # Save main qh_duong.json (initially empty as we don't have street data)
    filepath = os.path.join(output_dir, "qh_duong.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data['qh_d'], f, ensure_ascii=False, indent=2)
    logger.info(f"Saved qh_duong.json (initially empty)")
    
    # Create a basic chuanhoa.csv for standardization
    filepath = os.path.join(output_dir, "chuanhoa.csv")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("tp,thành phố\n")
        f.write("tx,thị xã\n")
        f.write("tt,thị trấn\n")
        f.write("q,quận\n")
        f.write("h,huyện\n")
        f.write("p,phường\n")
        f.write("x,xã\n")
        f.write("đ,đường\n")
        f.write("hcm,hồ chí minh\n")
        f.write("hn,hà nội\n")
    logger.info(f"Created basic chuanhoa.csv")


def validate_generated_files(output_dir: str) -> bool:
    """Validate that all expected files exist and are properly formatted."""
    logger.info("Validating generated JSON files")
    
    # Expected file paths
    expected_files = [
        # px folder
        os.path.join(output_dir, "px", "huyen_phuong.json"),
        os.path.join(output_dir, "px", "huyen_thitran.json"),
        os.path.join(output_dir, "px", "huyen_xa.json"),
        os.path.join(output_dir, "px", "quan_phuong.json"),
        os.path.join(output_dir, "px", "quan_thitran.json"),
        os.path.join(output_dir, "px", "quan_xa.json"),
        os.path.join(output_dir, "px", "tp_phuong.json"),
        os.path.join(output_dir, "px", "tp_thitran.json"),
        os.path.join(output_dir, "px", "tp_xa.json"),
        os.path.join(output_dir, "px", "tx_phuong.json"),
        os.path.join(output_dir, "px", "tx_thitran.json"),
        os.path.join(output_dir, "px", "tx_xa.json"),
        
        # qh folder
        os.path.join(output_dir, "qh", "thanhpho_huyen.json"),
        os.path.join(output_dir, "qh", "thanhpho_quan.json"),
        os.path.join(output_dir, "qh", "tinh_huyen.json"),
        os.path.join(output_dir, "qh", "tinh_quan.json"),
        os.path.join(output_dir, "qh", "tinh_tp.json"),
        os.path.join(output_dir, "qh", "tinh_tx.json"),
        
        # hcmhn folder
        os.path.join(output_dir, "hcmhn", "hcm_hn_huyen.json"),
        os.path.join(output_dir, "hcmhn", "hcm_hn_quan.json"),
        os.path.join(output_dir, "hcmhn", "hcm_hn_tx.json"),
        os.path.join(output_dir, "hcmhn", "hcm_hn_tp.json"),
        
        # Root files
        os.path.join(output_dir, "qh_duong.json"),
        os.path.join(output_dir, "chuanhoa.csv")
    ]
    
    # Check each file
    all_valid = True
    for filepath in expected_files:
        if not os.path.exists(filepath):
            logger.error(f"Missing file: {filepath}")
            all_valid = False
            continue
        
        # For JSON files, check they're valid JSON
        if filepath.endswith(".json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format in: {filepath}")
                all_valid = False
    
    if all_valid:
        logger.info("All files successfully validated")
    else:
        logger.warning("Validation failed for some files")
    
    return all_valid


def fix_address_module_encoding():
    """Sửa các vấn đề mã hóa trong address_module.py"""
    try:
        address_file = 'address_module.py'
        logger.info(f"Fixing encoding in {address_file}")
        
        # Đọc nội dung file
        with open(address_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thay thế các đường dẫn file để phù hợp với tên file đã tạo
        content = content.replace('hcmhn/hcmhn_huyen.json', 'hcmhn/hcm_hn_huyen.json')
        content = content.replace('hcmhn/hcmhn_quan.json', 'hcmhn/hcm_hn_quan.json')
        content = content.replace('hcmhn/hcmhn_tx.json', 'hcmhn/hcm_hn_tx.json')
        content = content.replace('hcmhn/hcmhn_tp.json', 'hcmhn/hcm_hn_tp.json')
        
        # Ghi lại file
        with open(address_file + '.bak', 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Created backup {address_file}.bak with encoding fixes")
    except Exception as e:
        logger.warning(f"Could not fix encoding in address_module.py: {e}")
        # Không dừng chương trình nếu không sửa được file


def main():
    """Main function to execute the JSON generation process."""
    logger.info("Starting JSON generation process")
    
    try:
        # Load master JSON
        data = load_master_json(INPUT_FILE)
        
        # Extract administrative units
        extracted_data = extract_administrative_units(data)
        
        # Save to JSON files
        save_json_files(extracted_data, OUTPUT_DIR)
        
        # Validate generated files
        is_valid = validate_generated_files(OUTPUT_DIR)
        

    except Exception as e:
        logger.error(f"Error during JSON generation: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
