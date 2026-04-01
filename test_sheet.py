import gspread, os, json, sys
from google.oauth2.service_account import Credentials
import traceback

BASE_DIR = r'c:\Users\QuocDat\Videos\SELENIUM_ZALO'
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'gen-lang-client-0450618162-54ea7d476a02.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

try:
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key('1SFAr1CFMzMPQXFToZEAwA2U1FaHpeCQqv7CyMa-f-0w')
    worksheet = workbook.worksheet('Danh Sách Khách Hàng')
    
    headers = worksheet.row_values(1)
    
    with open('test_sheet_output.txt', 'w', encoding='utf-8') as f:
        f.write("Headers: " + json.dumps(headers, ensure_ascii=False) + "\n")
        records = worksheet.get_all_records()
        if records:
            f.write("Row 1: " + json.dumps(records[0], ensure_ascii=False) + "\n")
except Exception as e:
    with open('test_sheet_error.txt', 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
