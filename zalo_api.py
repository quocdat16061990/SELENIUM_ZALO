import os
from flask import Flask, request, jsonify
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
from traceback import format_exc

# Import các hàm tĩnh từ file hiện tại để tái sử dụng
from OpenZaloSendContact import (
    build_driver, 
    search_contact, 
    click_contact_result, 
    send_message,
    validate_environment,
    CONTACT_SEARCH_INPUT
)
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# Biến toàn cục để giữ trình duyệt luôn mở, tránh phải load lại Zalo chậm mỗi khi có request từ n8n
browser_driver = None
browser_wait = None

def get_or_create_browser():
    global browser_driver, browser_wait
    if browser_driver is None:
        validate_environment()
        browser_driver = build_driver()
        browser_wait = WebDriverWait(browser_driver, 20)
        
        # Chờ Zalo load xong (tối đa 5 phút chờ QR)
        try:
            print("Đang khởi động trình duyệt và chờ Zalo...")
            login_wait = WebDriverWait(browser_driver, 300)
            login_wait.until(EC.presence_of_element_located(CONTACT_SEARCH_INPUT))
            print("=> Zalo đã sẵn sàng nhận lệnh từ n8n Webhook!")
            time.sleep(2)
        except TimeoutException:
            print("Quá thời gian chờ login (5 phút).")
            browser_driver.quit()
            browser_driver = None
            raise Exception("Timeout waiting for Zalo QR login")
            
    return browser_driver, browser_wait

@app.route('/send-message', methods=['POST'])
def handle_send_message():
    data = request.json
    
    if not data or 'phone' not in data or 'message' not in data:
        return jsonify({"error": "Dữ liệu không hợp lệ. Phải gửi JSON chứa 'phone' và 'message'"}), 400
        
    phone_number = str(data['phone']).strip()
    message = str(data['message']).strip()
    
    # Prefix số '0' nếu bị cắt mất
    if phone_number.isdigit() and not phone_number.startswith('0'):
        phone_number = '0' + phone_number

    try:
        driver, wait = get_or_create_browser()
        
        print(f"\n[n8n REQUEST] Yêu cầu gửi tin nhắn đến {phone_number}")
        
        # 1. Tìm thông tin liên hệ
        search_contact(driver, wait, phone_number)
        
        # 2. Click vào kết quả search được
        click_contact_result(driver, wait, phone_number)
        
        # 3. Paste và gửi nội dung
        send_message(driver, wait, message)
        
        return jsonify({
            "status": "success",
            "message": f"Sent message to {phone_number}"
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"Lỗi khi xử lý request: {error_msg}")
        # print(format_exc()) # Có thể bật lên để xem chi tiết log lỗi
        return jsonify({
            "status": "error",
            "error_detail": error_msg
        }), 500

if __name__ == '__main__':
    print("====================================")
    print("ZALO API SERVER ĐANG CHẠY")
    print("Endpoint: POST http://localhost:5000/send-message")
    print("Payload JSON mẫu từ n8n: {\"phone\": \"0912345678\", \"message\": \"Xin chào từ n8n!\"}")
    print("====================================")
    
    # Init driver 1 lần trước khi webserver start
    try:
        get_or_create_browser()
    except Exception as e:
        print("Không thể khởi động trình duyệt sẵn. API request đầu tiên từ n8n sẽ thực hiện việc này.")
        
    # port 5000 là default của Flask
    app.run(host='0.0.0.0', port=5000)
