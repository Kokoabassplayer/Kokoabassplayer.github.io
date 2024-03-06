#tableau workbook metadata extraction script

# pip install tableaudocumentapi # doc: https://tableau.github.io/document-api-python/

import openai
import pandas as pd
from tableaudocumentapi import Workbook
import os
import xml.etree.ElementTree as ET

# ฟังก์ชันสำหรับแทนที่ ID ด้วยชื่อฟิลด์
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


# ฟังก์ชันสำหรับใช้ AI ในการอนุมานคำอธิบาย จากคอลั่มอื่นๆ
def get_ai_description(row, api_key, model="gpt-3.5-turbo"): # เลือกได้ระหว่าง "gpt-3.5-turbo" ธรรมดา ไม่แพง ช้า, "gpt-4 turbo" ดี แพง ช้ามากๆๆ
    """
    สร้างคำอธิบายจาก AI สำหรับฟิลด์ใน Tableau โดยใช้ OpenAI

    Parameters:
    row (pd.Series): แถวใน DataFrame ที่มีข้อมูลฟิลด์
    api_key (str): API key สำหรับ OpenAI
    model (str): ชื่อโมเดล AI ที่ใช้ (เช่น "gpt-3.5-turbo")

    Returns:
    str: คำอธิบายที่สร้างโดย AI
    """
    try:
        openai.api_key = api_key
        #prompt = f"Please provide a brief description and confidence level  for the following Tableau field:\n- Field Name: {row['Field Name']}\n- Field Type: {row['Field Type']}\n- Field Role: {row['Field Role']}\n- Field Calculation: {row['Field Calculation']}\n\nDescription:"
        #prompt = f"Please provide a brief description and confidence level  for the following Tableau field:\n- Field Name: {row['Field Name']}\n- Field Type: {row['Field Type']}\n- Field Role: {row['Field Role']}\n- Field Calculation: {row['Field Calculation Updated']}\n- Field Description: {row['Field Description']}\n- Default Aggregation: {row['Default Aggregation']}\n- Is Quantitative: {row['Is Quantitative']}\n- Is Ordinal: {row['Is Ordinal']}\n- Is Nominal: {row['Is Nominal']}\n\nDescription:"
        prompt = f"Please provide a concise Thai description and confidence level for the following Tableau field:\n- Field Name: {row['Field Name']}\n- Field Type: {row['Field Type']}\n- Field Role: {row['Field Role']}\n- Field Calculation: {row['Field Calculation Updated']}\n- Field Description: {row['Field Description']}\n- Default Aggregation: {row['Default Aggregation']}\n- Is Quantitative: {row['Is Quantitative']}\n- Is Ordinal: {row['Is Ordinal']}\n- Is Nominal: {row['Is Nominal']}\n\nDescription:"
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating description: {e}"    



def export_enhanced_tableau_data_dictionary(tableau_workbook_path, api_key=None, model="gpt-3.5-turbo", include_ai_description=False):
    """
    ส่งออก data dictionary ขั้นสูงจาก Tableau workbook ไปยังไฟล์ CSV พร้อมทางเลือกในการใช้ AI สำหรับคำอธิบาย

    Parameters:
    tableau_workbook_path (str): ที่อยู่ไฟล์ของ Tableau workbook
    api_key (str): API key สำหรับ OpenAI (ถ้าต้องการใช้ AI)
    model (str): ชื่อโมเดล AI ที่ใช้ (เช่น "gpt-3.5-turbo" หรือ "gpt-4 turbo")
    include_ai_description (bool): ตัวเลือกในการเพิ่มคำอธิบายจาก AI

    Returns:
    tuple: DataFrame ที่มีข้อมูล data dictionary และที่อยู่ไฟล์ CSV ที่ถูกส่งออก
    """
    # โหลด Workbook และประมวลผลข้อมูล
    workbook = Workbook(tableau_workbook_path)

    # กำหนดชื่อไฟล์ CSV สำหรับส่งออก
    workbook_base_name = os.path.splitext(os.path.basename(tableau_workbook_path))[0]
    output_csv_file = os.path.join(os.path.dirname(tableau_workbook_path), workbook_base_name + '_EnhancedDataDictionary.csv')

    # สร้างลิสต์เพื่อเก็บข้อมูลของแต่ละ field
    data = []
    # วนลูปเข้าถึงแต่ละ datasource และ field ใน workbook
    for datasource in workbook.datasources:
        for field_id, field in datasource.fields.items():
            field_description_xml = getattr(field, 'description', None)
            field_description = ''
            # แก้ไขให้ field_description แสดงแต่คำอธิบาย
            if field_description_xml is not None:
                try:
                    root = ET.fromstring(field_description_xml)
                    extracted_text = ''.join(root.itertext())
                    field_description = ' '.join(extracted_text.split())
                except ET.ParseError:
                    field_description = field_description_xml
    
            # เก็บคุณสมบัติของ field
            field_properties = {
                'Datasource Name': datasource.name,
                'Field Name': field.name,
                'Field ID': field_id,
                'Field Type': field.datatype,
                'Field Role': getattr(field, 'role', ''),
                'Field Calculation': getattr(field, 'calculation', ''),
                'Field Caption': getattr(field, 'caption', ''),
                'Field Description': field_description,
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

    # ถ้าเลือกใช้ AI ในการสร้างคำอธิบาย
    if include_ai_description and api_key:
        df['AI Description'] = df.apply(lambda row: get_ai_description(row, api_key, model), axis=1)

    # ส่งออก DataFrame เป็นไฟล์ CSV
    df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
    print(f"ได้ส่งออก data dictionary ขั้นสูงไปที่ {output_csv_file}")

    return df, output_csv_file


# ตัวอย่างการใช้งาน
api_key = "your-openai-api-key"  # ใส่ API key ของ OpenAI แทนที่ "your-openai-api-key" ซื้อ key ของคุณเองได้ที่: https://openai.com/product
model="gpt-3.5-turbo"  # เลือกใช้ระหว่าง "gpt-3.5-turbo" ถูก เร็ว(เมื่อเทียบกับโมเดลอื่นๆ), "gpt-4-0125-preview" ดีกว่า แพงกว่า 10 เท่า ช้ามาก

df_sample, output_csv_path = export_enhanced_tableau_data_dictionary(
    r'C:\Path\to\your\workbook.twb', # ชี้ path ไปที่ tableau workbook ที่เราต้องการ
    api_key=api_key,
    model=model,
    include_ai_description=True # เปิดหรือปิด AI ด้วยการกำหนดค่า True หรือ False
)

