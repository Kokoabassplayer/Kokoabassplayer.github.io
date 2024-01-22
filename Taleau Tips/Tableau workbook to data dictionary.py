#tableau workbook metadata extraction script

# pip install tableaudocumentapi # doc: https://tableau.github.io/document-api-python/

def export_tableau_data_dictionary(tableau_workbook_path):
    """
    ส่งออก data dictionary จาก Tableau workbook ไปยังไฟล์ CSV

    Parameters:
    tableau_workbook_path (str): ที่อยู่ไฟล์ของ Tableau workbook

    Returns:
    str: ที่อยู่ไฟล์ของ CSV ที่ถูกส่งออก ไฟล์ output จะอยู่ในโฟล์เดอร์เดียวกันกับไฟล์ Tableau workbook
    """
    # นำเข้า libraries ที่จำเป็น
    from tableaudocumentapi import Workbook
    import pandas as pd
    import os
    import xml.etree.ElementTree as ET

    # โหลด Tableau workbook
    workbook = Workbook(tableau_workbook_path)

    # กำหนดชื่อไฟล์ CSV สำหรับการส่งออก
    workbook_base_name = os.path.splitext(os.path.basename(tableau_workbook_path))[0]
    output_csv_file = os.path.join(os.path.dirname(tableau_workbook_path), workbook_base_name + '_DataDictionary.csv') # ที่อยู่ไฟล์ของ CSV ที่ถูกส่งออก จะอยู่ในโฟล์เดอร์เดียวกันกับไฟล์ Tableau workbook
    # เตรียมข้อมูลสำหรับ DataFrame
    data = []
    for datasource in workbook.datasources:
        for field in datasource.fields.values():
            # ดึงข้อมูลเพิ่มเติมของ field
            field_role = getattr(field, 'role', '')
            field_calculation = getattr(field, 'calculation', '')
            field_caption = getattr(field, 'caption', '')
            field_description_xml = getattr(field, 'description', None)

            # ตรวจสอบและแปลงข้อมูล XML ของ field description เป็น text
            field_description = ''
            if field_description_xml is not None:
                try:
                    root = ET.fromstring(field_description_xml)
                    extracted_text = ''.join(root.itertext())
                    # ลบช่องว่างที่ไม่จำเป็น
                    field_description = ' '.join(extracted_text.split())
                except ET.ParseError:
                    # ใช้ข้อมูล XML ต้นฉบับหากพบข้อผิดพลาดในการแปลง
                    field_description = field_description_xml

            # เพิ่มข้อมูลลงใน list
            data.append([
                datasource.name, 
                field.name, 
                field.datatype, 
                field_role, 
                field_calculation,
                field_caption,
                field_description
            ])

    # สร้าง DataFrame พร้อมคอลัมน์ที่ชัดเจน
    df = pd.DataFrame(data, columns=[
        'Datasource Name', 
        'Field Name', 
        'Field Type', 
        'Field Role', 
        'Field Calculation',
        'Field Caption',
        'Field Description'
    ])

    # ส่งออกข้อมูลเป็นไฟล์ CSV
    df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
    print(f"Data dictionary exported to {output_csv_file}")
    
    return output_csv_file

# ตัวอย่างการใช้งาน:
output_file = export_tableau_data_dictionary(r'D:\your folder\your tableau workbook.twb') # ระบุที่อยู่ไฟล์ของ Tableau workbook ที่ต้องการสร้าง data dictionary