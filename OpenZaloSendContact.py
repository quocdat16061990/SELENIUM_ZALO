import os
import sys
import time
from pathlib import Path
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

# Lấy thư mục gốc (áp dụng cho cả file .py và khi build ra file .exe)
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

# Tự động tìm Chrome tương thích đa nền tảng (Windows, Linux, MacOS)
def find_chrome_binary():
    import platform
    system = platform.system()
    possible_paths = []
    
    if system == "Windows":
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe")
        ]
    elif system == "Linux":
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    elif system == "Darwin": # Mac OS
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
        
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    raise FileNotFoundError(f"Không thể tìm thấy Google Chrome cho hệ điều hành {system}!")

CHROME_BINARY = find_chrome_binary()

# Đường dẫn tự động nhận dạng cho từng máy
PROFILE_ROOT = os.path.join(BASE_DIR, "zalo-chrome-profile")
ZALO_URL = "https://chat.zalo.me"

SHEET_ID = "1SFAr1CFMzMPQXFToZEAwA2U1FaHpeCQqv7CyMa-f-0w"
CREDENTIALS_FILE = os.path.join(BASE_DIR, "gen-lang-client-0450618162-54ea7d476a02.json")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

CONTACTS_DATA = []
WORKSHEET = None

try:
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(SHEET_ID)
    WORKSHEET = workbook.sheet1
    
    records = WORKSHEET.get_all_records()
    headers = WORKSHEET.row_values(1)
    
    if 'Status' not in headers:
        status_col = len(headers) + 1
        WORKSHEET.update_cell(1, status_col, 'Status')
        headers = WORKSHEET.row_values(1)
        
    status_col_index = headers.index('Status') + 1

    for idx, row in enumerate(records):
        row_num = idx + 2
        p_name = str(row.get('Phone', row.get('Group Name', ''))).strip()  # Tương thích cột Phone mới và Group Name cũ
        
        # Thêm số 0 vào đầu nếu Google Sheet tự động xóa số 0 của số điện thoại
        if p_name and p_name.isdigit() and not p_name.startswith('0'):
            p_name = '0' + p_name
            
        msg = str(row.get('Message', '')).strip()
        status = str(row.get('Status', '')).strip()
        
        # Chỉ xử lý các dòng có Status là 'UNAPPROVED'
        if p_name and p_name != 'nan' and status == 'UNAPPROVED':
            CONTACTS_DATA.append({
                "phone_number": p_name, 
                "message": msg if msg != 'nan' else "",
                "row_num": row_num,
                "status_col": status_col_index
            })
except Exception as e:
    print(f"Không thể đọc trực tiếp từ Google Sheet API. Vui lòng kiểm tra file JSON hoặc quyền chia sẻ: {e}")

OPEN_WAIT_SECONDS = 8
DELAY_BETWEEN_CONTACTS = 2

# =========================
# SELECTORS
# =========================
CONTACT_SEARCH_INPUT = (By.ID, "contact-search-input")

CHAT_WRAPPER = (By.ID, "chat-input-container-id")
CHAT_EDITOR = (By.ID, "richInput")


# =========================
# BASIC
# =========================
def validate_environment():
    if not os.path.exists(CHROME_BINARY):
        raise FileNotFoundError(f"Không tìm thấy Chrome binary: {CHROME_BINARY}")
    if not os.path.isdir(PROFILE_ROOT):
        raise FileNotFoundError(f"Không tìm thấy Chrome profile: {PROFILE_ROOT}")


def build_driver():
    options = Options()
    options.binary_location = CHROME_BINARY
    options.add_argument(f"--user-data-dir={PROFILE_ROOT}")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    driver.get(ZALO_URL)
    driver.maximize_window()
    return driver


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)


# =========================
# FLOW STEP 1
# Search contact
# =========================
def get_search_input(driver, wait):
    search_input = wait.until(EC.presence_of_element_located(CONTACT_SEARCH_INPUT))
    driver.execute_script("""
        arguments[0].removeAttribute('tabindex');
        arguments[0].focus();
    """, search_input)
    return search_input


def clear_search_input(search_input):
    search_input.click()
    time.sleep(0.2)
    search_input.send_keys(Keys.CONTROL, "a")
    search_input.send_keys(Keys.BACKSPACE)
    time.sleep(0.2)


def search_contact(driver, wait, phone_number):
    search_input = get_search_input(driver, wait)
    clear_search_input(search_input)
    search_input.send_keys(phone_number)
    time.sleep(1.5)
    print(f"Đã nhập tìm kiếm số điện thoại: {phone_number}")


# =========================
# FLOW STEP 2
# Click search result
# =========================
def click_contact_result(driver, wait, phone_number):
    xpath_exact = f"//div[contains(@id, 'friend-item-') and .//*[contains(text(), '{phone_number}')]]"
    xpath_first = "//div[contains(@id, 'friend-item-')]"

    result_item = None
    
    short_wait = WebDriverWait(driver, 3)

    try:
        # Ưu tiên tìm chính xác kết quả chứa số điện thoại
        result_item = short_wait.until(
            EC.presence_of_element_located((By.XPATH, xpath_exact))
        )
    except TimeoutException:
        try:
            # Nếu không tìm thấy chính xác, thử tìm kết quả liên hệ đầu tiên trả về
            quick_wait = WebDriverWait(driver, 1)
            result_item = quick_wait.until(
                EC.presence_of_element_located((By.XPATH, xpath_first))
            )
        except TimeoutException:
            raise RuntimeError(f"Không thấy kết quả liên hệ cho số điện thoại: {phone_number}")

    scroll_into_view(driver, result_item)
    time.sleep(0.3)

    try:
        result_item.click()
    except Exception:
        js_click(driver, result_item)

    time.sleep(1)
    print(f"Đã click vào liên hệ: {phone_number}")


# =========================
# FLOW STEP 3
# Focus chat + send
# =========================
def focus_chat(driver, wait):
    wrapper = wait.until(EC.presence_of_element_located(CHAT_WRAPPER))
    editor = wait.until(EC.presence_of_element_located(CHAT_EDITOR))

    scroll_into_view(driver, wrapper)

    try:
        wrapper.click()
    except Exception:
        js_click(driver, wrapper)

    time.sleep(0.2)

    try:
        editor.click()
    except Exception:
        js_click(driver, editor)

    driver.execute_script("""
        arguments[0].focus();
    """, editor)

    time.sleep(0.3)
    return editor


def send_message(driver, wait, message, max_attempts=5):
    last_exc = None

    for attempt in range(max_attempts):
        try:
            editor = focus_chat(driver, wait)

            # Dùng JavaScript execCommand để chèn văn bản (Hỗ trợ Emoji, khắc phục lỗi ChromeDriver BMP)
            driver.execute_script("arguments[0].focus();", editor)
            time.sleep(0.1)
            driver.execute_script("document.execCommand('insertText', false, arguments[0]);", message)
            time.sleep(0.5) # Chờ Zalo cập nhật giao diện
            
            # Lấy lại element ngay trước khi gửi Enter để phòng tránh lỗi StaleElementReferenceException do Zalo render lại DOM
            fresh_editor = wait.until(EC.presence_of_element_located(CHAT_EDITOR))
            fresh_editor.send_keys(Keys.ENTER)
            print("Đã nhập và gửi tin nhắn (hỗ trợ hiển thị Emoji).")
            return True

        except (StaleElementReferenceException, NoSuchElementException, Exception) as exc:
            last_exc = exc
            print(f"Lần gửi {attempt + 1} lỗi: {exc}")
            time.sleep(0.8)

    raise RuntimeError(f"Gửi tin nhắn thất bại: {last_exc}")


# =========================
# MAIN
# =========================
def main():
    validate_environment()

    driver = None
    try:
        print("Mở Zalo...")
        driver = build_driver()
        wait = WebDriverWait(driver, 20)

        # Chờ người dùng quét mã QR đăng nhập (tối đa 5 phút)
        try:
            print("Đang chờ tải Zalo... Vui lòng quét mã QR nếu có yêu cầu (thời gian chờ tối đa 5 phút)")
            login_wait = WebDriverWait(driver, 300)
            login_wait.until(EC.presence_of_element_located(CONTACT_SEARCH_INPUT))
            print("Zalo đã sẵn sàng, chuẩn bị gửi tin nhắn!")
        except TimeoutException:
            print("Hết thời gian chờ đăng nhập (5 phút). Dừng chương trình...")
            driver.quit()
            return

        time.sleep(2)  # Nghỉ một chút cho giao diện tải hoàn tất

        success = []
        failed = []

        if not CONTACTS_DATA:
            print("Không có số điện thoại nào từ file GG SHEET có trạng thái UNAPPROVED để chạy!")
            return

        for idx, item in enumerate(CONTACTS_DATA, start=1):
            phone_number = item['phone_number']
            message = item['message']
            row_num = item['row_num']
            status_col = item['status_col']
            print(f"\n[{idx}/{len(CONTACTS_DATA)}] Đang xử lý: {phone_number}")

            try:
                search_contact(driver, wait, phone_number)
                click_contact_result(driver, wait, phone_number)
                
                if message:
                    send_message(driver, wait, message)
                    print(f"OK -> {phone_number}")
                else:
                    print(f"OK -> {phone_number} (Bỏ qua vì cột Message trống)")
                
                # Đánh dấu đã gửi thành công
                if WORKSHEET is not None:
                    try:
                        WORKSHEET.update_cell(row_num, status_col, 'APPROVED')
                        print("=> Đã cập nhật Status = APPROVED trên Google Sheet")
                    except Exception as sheet_err:
                        print(f"=> Lỗi khi cập nhật Google Sheet: {sheet_err}")
                
                success.append(phone_number)
            except Exception as exc:
                failed.append((phone_number, str(exc)))
                print(f"FAIL -> {phone_number} | {exc}")

                # Cập nhật trạng thái lỗi lên Google Sheet
                if WORKSHEET is not None:
                    try:
                        if "Không thấy kết quả liên hệ" in str(exc):
                            WORKSHEET.update_cell(row_num, status_col, 'NOT_FOUND')
                            print("=> Đã cập nhật Status = NOT_FOUND trên Google Sheet")
                        else:
                            WORKSHEET.update_cell(row_num, status_col, 'FAILED')
                            print("=> Đã cập nhật Status = FAILED trên Google Sheet")
                    except Exception as sheet_err:
                        print(f"=> Lỗi khi cập nhật Google Sheet: {sheet_err}")

            time.sleep(DELAY_BETWEEN_CONTACTS)

        print("\n===== TỔNG KẾT =====")
        print("Thành công:")
        for p in success:
            print(f" - {p}")

        print("Thất bại:")
        for p, reason in failed:
            print(f" - {p}: {reason}")

        print("\nHoàn tất. Tự động đóng trình duyệt và thoát chương trình...")

    except Exception as exc:
        print(f"Lỗi tổng: {exc}")
        if driver is not None:
            try:
                driver.save_screenshot("zalo_error.png")
                print("Đã lưu screenshot: zalo_error.png")
            except Exception:
                pass
        print("Có lỗi. Tự động đóng trình duyệt và kết thúc...")
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    main()
