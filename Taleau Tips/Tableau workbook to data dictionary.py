#tableau workbook metadata extraction script

# pip install tableaudocumentapi # doc: https://tableau.github.io/document-api-python/

from tableaudocumentapi import Workbook
import pandas as pd
import os
import re

def replace_ids_with_names(calculation, field_id_to_name):
    """
    แทนที่ Field ID ด้วยชื่อ Field ในสตริงการคำนวณของ Tableau

    Parameters:
    calculation (str): สตริงการคำนวณที่มี Field ID
    field_id_to_name (dict): ดิกชันนารีที่มี Field ID เป็นคีย์และชื่อ Field เป็นค่า

    Returns:
    str: สตริงการคำนวณที่มีชื่อ Field แทนที่ Field ID
    """
    # ตรวจสอบว่ามีสตริงการคำนวณหรือไม่
    if calculation:
        # แสดงการคำนวณเดิม
        print("❌ การคำนวณเดิม:", calculation)
        # วนลูปเพื่อแทนที่ Field ID ด้วยชื่อ Field
        for field_id, field_name in field_id_to_name.items():
            # ตรวจสอบว่า Field ID มีอยู่ในสตริงการคำนวณหรือไม่
            if field_id in calculation:
                # ตรวจสอบว่าชื่อ Field มีวงเล็บอยู่แล้วหรือไม่
                replacement = f'[{field_name}]' if not field_name.startswith('[') else field_name
                # แสดงการแทนที่
                print(f"✔ กำลังแทนที่ {field_id} ด้วย 👉 {replacement}")
                # ทำการแทนที่ในสตริง
                calculation = calculation.replace(field_id, replacement)
        # แสดงการคำนวณหลังจากแทนที่
        print("✨ การคำนวณหลังการแทนที่:", calculation)
    return calculation

def export_enhanced_tableau_data_dictionary(tableau_workbook_path):
    """
    ส่งออก data dictionary ขั้นสูงจาก Tableau workbook ไปยังไฟล์ CSV

    Parameters:
    tableau_workbook_path (str): ที่อยู่ไฟล์ของ Tableau workbook

    Returns:
    tuple: ประกอบด้วย DataFrame ที่มีข้อมูล data dictionary และที่อยู่ไฟล์ CSV ที่ถูกส่งออก
    """
    # โหลด Workbook จากที่อยู่ไฟล์ที่ระบุ
    workbook = Workbook(tableau_workbook_path)
    # กำหนดชื่อไฟล์ CSV สำหรับส่งออก
    workbook_base_name = os.path.splitext(os.path.basename(tableau_workbook_path))[0]
    output_csv_file = os.path.join(os.path.dirname(tableau_workbook_path), workbook_base_name + '_EnhancedDataDictionary.csv')

    # สร้างลิสต์เพื่อเก็บข้อมูลของแต่ละ field
    data = []
    # วนลูปเข้าถึงแต่ละ datasource และ field ใน workbook
    for datasource in workbook.datasources:
        for field_id, field in datasource.fields.items():
            # เก็บคุณสมบัติของ field
            field_properties = {
                'Datasource Name': datasource.name,
                'Field Name': field.name,
                'Field ID': field_id,
                'Field Type': field.datatype,
                'Field Role': getattr(field, 'role', ''),
                'Field Calculation': getattr(field, 'calculation', ''),
                'Field Caption': getattr(field, 'caption', ''),
                'Field Description': getattr(field, 'description', ''),
                'Default Aggregation': getattr(field, 'default_aggregation', ''),
                'Is Quantitative': getattr(field, 'is_quantitative', ''),
                'Is Ordinal': getattr(field, 'is_ordinal', ''),
                'Is Nominal': getattr(field, 'is_nominal', '')
            }
            data.append(field_properties)

    # สร้าง DataFrame จากข้อมูลที่เก็บไว้
    df = pd.DataFrame(data)
    # สร้างดิกชันนารีเพื่อแมป Field ID ไปยังชื่อ Field
    field_id_to_name = {field['Field ID']: field['Field Name'] for field in data}
    # ปรับปรุงคอลัมน์ 'Field Calculation' โดยการเรียกใช้ฟังก์ชัน replace_ids_with_names
    df['Field Calculation Updated'] = df.apply(
        lambda row: replace_ids_with_names(row['Field Calculation'], field_id_to_name), axis=1
    )

    # ส่งออก DataFrame เป็นไฟล์ CSV
    df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
    print(f"ได้ส่งออก data dictionary ขั้นสูงไปที่ {output_csv_file}")

    return df, output_csv_file

# ตัวอย่างการใช้งาน
df_sample, output_csv_path = export_enhanced_tableau_data_dictionary(r'C:\Path\To\Your\Workbook.twbx')
