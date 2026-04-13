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
PROFILE_ROOT = os.path.join(BASE_DIR, "facebook-chrome-profile")
FB_URL = "https://www.facebook.com"

SHEET_ID = "1SFAr1CFMzMPQXFToZEAwA2U1FaHpeCQqv7CyMa-f-0w"
CREDENTIALS_FILE = os.path.join(BASE_DIR, "gen-lang-client-0450618162-54ea7d476a02.json")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

POSTS_DATA = []
WORKSHEET = None

def fetch_google_sheet():
    global WORKSHEET, POSTS_DATA
    try:
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        workbook = gc.open_by_key(SHEET_ID)
        
        try:
            WORKSHEET = workbook.worksheet("Post Bài FB")
        except:
            print("Không tìm thấy tab 'Post Bài FB', đang dùng tab đầu tiên...")
            WORKSHEET = workbook.sheet1
            
        records = WORKSHEET.get_all_records()
        headers = WORKSHEET.row_values(1)
        
        # Thêm cột Status nếu chưa có
        if 'Status' not in headers:
            status_col = len(headers) + 1
            WORKSHEET.update_cell(1, status_col, 'Status')
            headers = WORKSHEET.row_values(1)
            
        status_col_index = headers.index('Status') + 1

        for idx, row in enumerate(records):
            row_num = idx + 2
            tieu_de = str(row.get('Tiêu Đề', '')).strip()
            # Hỗ trợ lấy cột mang tên 'Nội Dung' hoặc 'Mô Tả'
            noi_dung = str(row.get('Nội Dung', row.get('Mô Tả', ''))).strip()
            status = str(row.get('Status', '')).strip()
            
            # Chỉ xử lý các bài ở trạng thái UNAPPROVED
            if status == 'UNAPPROVED' and tieu_de != 'nan' and (tieu_de or noi_dung):
                POSTS_DATA.append({
                    "title": tieu_de, 
                    "content": noi_dung if noi_dung != 'nan' else "",
                    "row_num": row_num,
                    "status_col": status_col_index
                })
        print(f"Đã tải {len(POSTS_DATA)} bài viết từ Google Sheet.")
    except Exception as e:
        print(f"Không thể đọc trực tiếp từ Google Sheet API. Vui lòng kiểm tra file JSON hoặc quyền chia sẻ: {e}")

OPEN_WAIT_SECONDS = 8
DELAY_BETWEEN_CONTACTS = 2

# =========================
# SELECTORS (Facebook)
# =========================
FB_EMAIL_INPUT = (By.NAME, "email")
FB_PASS_INPUT = (By.NAME, "pass")
FB_LOGIN_BUTTON = (By.CSS_SELECTOR, "button[name='login'], div[aria-label='Đăng nhập'], div[aria-label='Log In'], div[aria-label='Log in']")
FB_HOME_ELEMENT = (By.CSS_SELECTOR, "div[aria-label='Trang chủ'], a[aria-label='Facebook']")





# =========================
# BASIC
# =========================
def validate_environment():
    if not os.path.exists(CHROME_BINARY):
        raise FileNotFoundError(f"Không tìm thấy Chrome binary: {CHROME_BINARY}")
    if not os.path.isdir(PROFILE_ROOT):
        raise FileNotFoundError(f"Không tìm thấy Chrome profile: {PROFILE_ROOT}")


def build_driver():
    print(f"DEBUG: CHROME_BINARY = {CHROME_BINARY}")
    print(f"DEBUG: PROFILE_ROOT = {PROFILE_ROOT}")
    
    # Ép buộc thiết lập DISPLAY cho Remote Desktop
    current_display = os.environ.get("DISPLAY", "Chưa đặt")
    print(f"DEBUG: DISPLAY hiện tại = {current_display}")

    if os.path.exists("/tmp/.X11-unix/X10"):
        os.environ["DISPLAY"] = ":10.0"
        print("DEBUG: Đã ép buộc thiết lập DISPLAY=:10.0 (phát hiện X10 socket)")
    elif os.path.exists("/tmp/.X11-unix/X0"):
        os.environ["DISPLAY"] = ":0.0"
        print("DEBUG: Đã ép buộc thiết lập DISPLAY=:0.0 (phát hiện X0 socket)")

    options = Options()
    options.binary_location = CHROME_BINARY
    options.add_argument(f"--user-data-dir={PROFILE_ROOT}")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-gpu")

    options.add_experimental_option("detach", True)

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(FB_URL)
        return driver
    except Exception as e:
        print(f"DEBUG: Lỗi khi khởi tạo WebDriver: {e}")
        raise e


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)


def check_login_status(driver, wait):
    """Kiểm tra xem đã đăng nhập chưa (tìm nút Trang chủ hoặc Logo Facebook)"""
    try:
        # Đợi 5 giây xem có thấy nút Trang chủ không
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(FB_HOME_ELEMENT))
        return True
    except:
        return False


def login_facebook(driver, wait, email, password):

    try:
        print(f"Đang nhập liệu cho tài khoản: {email}")
        
        # Chờ và nhập Email
        email_field = wait.until(EC.presence_of_element_located(FB_EMAIL_INPUT))
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(1)
        
        # Chờ và nhập Password
        pass_field = wait.until(EC.presence_of_element_located(FB_PASS_INPUT))
        pass_field.clear()
        pass_field.send_keys(password)
        time.sleep(1)
        
        # Bấm Enter trực tiếp từ ô mật khẩu cho chắc chắn thay vì chỉ click nút
        pass_field.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Dự phòng: Click nút Đăng nhập nếu Enter chưa chạy
        try:
            login_btn = wait.until(EC.element_to_be_clickable(FB_LOGIN_BUTTON))
            try:
                login_btn.click()
            except:
                driver.execute_script("arguments[0].click();", login_btn)
        except:
            pass
            
        print("Đã nhấn nút đăng nhập.")
        time.sleep(5) # Chờ chuyển trang
    except Exception as e:
        print(f"Lỗi khi đăng nhập: {e}")
        driver.save_screenshot("login_error.png")



# =========================
# =========================
# ACTIONS (Post, Send msg)
# =========================
def go_to_profile(driver, wait, profile_name):
    try:
        print(f"Đang tìm và click vào trang cá nhân: {profile_name}...")
        # Tìm thẻ span chứa đúng tên của bạn
        profile_xpath = f"//span[text()='{profile_name}' or contains(text(), '{profile_name}')]"
        profile_node = wait.until(EC.presence_of_element_located((By.XPATH, profile_xpath)))
        
        # Click vào node (do trên FB bọc bằng thẻ HTML phức tạp nên ta click qua Javascript luôn cho chắc)
        driver.execute_script("arguments[0].click();", profile_node)
            
        print("Đã click chuyển sang trang cá nhân. Đang tải trang...")
        time.sleep(5) # Chờ load DOM trang cá nhân của bạn
    except Exception as e:
        print(f"Lỗi khi tìm node {profile_name}, tự động fallback qua cách gõ thẳng link URL facebook.com/me...")
        # Fallback: cách bí mật nhưng cực chuẩn của Facebook để vào trang cá nhân
        driver.get("https://www.facebook.com/me")
        time.sleep(5)


def post_facebook_status(driver, wait, content):
    try:
        print("Đang tìm nút 'Bạn đang nghĩ gì?'...")
        # 1. Click vào "Bạn đang nghĩ gì?"
        # Dùng XPath để tìm thẻ span chứa text "Bạn đang nghĩ gì"
        create_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Bạn đang nghĩ gì') or contains(text(), 'on your mind')]")))
        
        # Scroll tí cho chắc chắn nút hiển thị
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", create_btn)
        time.sleep(1)
        
        try:
            create_btn.click()
        except:
            driver.execute_script("arguments[0].click();", create_btn)
            
        print("Đã click nút mở form Tạo bài viết. Đang chờ textbox xuất hiện...")
        time.sleep(3) # chờ modal mở ra và khởi tạo animation
        
        # 2. Gõ nội dung
        # Bắt buộc tìm textbox NẰM TRONG BẢNG DIALOG (Tránh vơ nhầm hộp Comment ở dưới)
        dialog_xpath = "//div[@role='dialog']//div[@role='textbox' and @contenteditable='true']"
        textbox = wait.until(EC.visibility_of_element_located((By.XPATH, dialog_xpath)))
        
        # Focus vào textbox bằng click trước khi gõ để Lexical React Editor nhận sự kiện
        try:
            textbox.click()
        except:
            driver.execute_script("arguments[0].focus();", textbox)
        time.sleep(1)
        
        # Giải quyết lỗi BMP của ChromeDriver chứa Emoji, sử dụng Clipboard JS để dán chữ thay vì send_keys
        js_paste = """
        const text = arguments[1];
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text/plain', text);
        const event = new ClipboardEvent('paste', {
          clipboardData: dataTransfer,
          bubbles: true
        });
        arguments[0].dispatchEvent(event);
        """
        driver.execute_script(js_paste, textbox, content)
        
        print(f"Đã dán nội dung vào form Tạo Bài Viết xong.")
        time.sleep(2) # đợi React nhận diện content để gỡ bỏ thuộc tính aria-disabled của nút Đăng
        
        # 3. Bấm nút Đăng
        print("Đang bấm nút Đăng...")
        # Tìm nút có aria-label là Đăng hoặc Post
        post_btn_xpath = "//div[(contains(@aria-label, 'Đăng') or contains(@aria-label, 'Post')) and @role='button']"
        post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, post_btn_xpath)))
        
        try:
            post_btn.click()
        except:
            driver.execute_script("arguments[0].click();", post_btn)
            
        print("Đã click nút Đăng. Đợi fb xử lý bài viết...")
        time.sleep(5)
        
    except Exception as e:
        print(f"Lỗi khi đăng bài: {e}")
        driver.save_screenshot("post_error.png")
        print("Đã lưu screenshot: post_error.png")

# =========================
# MAIN
# =========================
def main():
    validate_environment()

    driver = None
    try:
        print("Mở Facebook...")
        driver = build_driver()
        wait = WebDriverWait(driver, 20)

        print("Trình duyệt đã mở Facebook.")
        
        # Kiểm tra xem có cần đăng nhập không
        if not check_login_status(driver, wait):
            print("Chưa đăng nhập. Đang tiến hành đăng nhập tự động...")
            email_fb = "quocdattranhuu19902022@gmail.com"
            pass_fb = "Quocdat2025@@@"
            login_facebook(driver, wait, email_fb, pass_fb)
        else:
            print("Đã nhận diện phiên đăng nhập cũ. Bỏ qua bước nhập mật khẩu.")
        
        time.sleep(5)

        # Tải dữ liệu từ Google Sheet
        print("Đang kết nối Google Sheet...")
        fetch_google_sheet()
        
        if POSTS_DATA:
            # -----------------------------
            # 1) VÀO TRANG CÁ NHÂN
            # -----------------------------
            go_to_profile(driver, wait, "Đạt Trần")
    
            # -----------------------------
            # 2) ĐĂNG BÀI THEO SHEET
            # -----------------------------
            print("\n--- BẮT ĐẦU ĐĂNG BÀI (Chế độ 1 bài/lần cho Cron) ---\n")
            
            # Lấy ĐÚNG 1 BÀI đầu tiên trong danh sách UNAPPROVED để đăng
            post = POSTS_DATA[0]
            print(f"-> Chuẩn bị đăng duy nhất bài viết tại dòng {post['row_num']}...")
            
            # Gộp Tiêu Đề và Nội Dung (cách nhau 2 dòng trắng)
            full_content = ""
            if post['title']:
                full_content += post['title'] + "\n\n"
            if post['content']:
                full_content += post['content']
            
            # Tiến hành nhấp form và đăng chữ
            post_facebook_status(driver, wait, full_content)
            
            # Đánh dấu APPROVED về lại Google Sheet
            try:
                WORKSHEET.update_cell(post['row_num'], post['status_col'], 'APPROVED')
                print(f"Đã cập nhật trạng thái 'APPROVED' lên Google Sheet (Dòng {post['row_num']}).")
            except Exception as e:
                print(f"Lỗi khi update status lên Sheet: {e}")
                
            print("\n--- ĐÃ ĐĂNG XONG 1 BÀI TRONG LẦN CHẠY NÀY ---")
        else:
            print("\n--- GOOGLE SHEET TRỐNG: Không có bài viết nào ở trạng thái chờ. ---")

    except Exception as exc:
        print(f"Lỗi tổng: {exc}")
        if driver is not None:
            try:
                driver.save_screenshot("fb_error.png")
                print("Đã lưu screenshot: fb_error.png")
            except Exception:
                pass
        print("Có lỗi xảy ra.")

    # Tự động đóng trình duyệt sau khi xong việc
    if driver is not None:
        print("\n" + "="*50)
        print("Đã hoàn thành tác vụ. Đang tự động đóng trình duyệt...")
        print("="*50)
        driver.quit()



if __name__ == "__main__":
    main()
