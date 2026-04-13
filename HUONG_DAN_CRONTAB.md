# 📓 Cẩm Nang: Lưu ý sống còn khi đưa script Python Lên Crontab

Khi cấu hình cho một đoạn script Python tự động chạy trên máy chủ (qua tiện ích `crontab`), môi trường hệ thống sẽ **rất khác** so với khi bạn tự tay gõ lệnh chạy trên Terminal. 

Do đó, để đảm bảo code hoạt động trơn tru sau khi lên crontab, dưới đây là các yếu tố BẮT BUỘC phải lưu ý.

---

## 1. Không Bao Giờ Tin Vào "Thư Mục Hiện Tại" (Đường dẫn tuyệt đối)
Khi `crontab` chạy, nó diễn ra hoàn toàn "ngầm". Trạng thái con trỏ của hệ thống thường ở thư mục gốc (home của hệ thống), nó **sẽ không tự động biết thư mục dự án của bạn nằm ở đâu**.
*   ❌ **Sai:** Đọc file cấu hình kiểu `config = open("config.json")`
*   ✅ **Đúng:** `config = open("/home/ubuntu/SELENIUM_ZALO/config.json")`
*   ✅ **Cách khắc phục nhanh:** Hoặc là trong lệnh crontab, hãy yêu cầu hệ thống `cd` vào thư mục dự án trước khi gọi Python:
    ```bash
    * * * * * cd /home/ubuntu/SELENIUM_ZALO && python abc.py
    ```

## 2. Vấn Đề Về Môi Trường Ảo (Virtual Environment - Venv)
Nếu bạn có cài đặt các thư viện trong một môi trường ảo (`venv`), `crontab` mặc định sẽ không biết điều đó. Nó sẽ dùng phiên bản Python gốc của máy (ví dụ Python 3.10) và báo lỗi "ModuleNotFoundError".
*   ❌ **Sai:** `* * * * * python script.py`
*   ✅ **Đúng:** Phải trỏ thẳng đường dẫn tới file chạy Python của venv:
    ```bash
    * * * * * /home/ubuntu/SELENIUM_ZALO/venv/bin/python script.py
    ```

## 3. Biến Môi Trường Và Trình Duyệt UI (Dành riêng cho Selenium)
Khi bạn làm tự động hoá tương tác lướt web (như Facebook/Zalo) bằng chuột và bàn phím, trình duyệt bắt buộc **phải có màn hình** (Display) để hiện lên. Nhưng mặc định Cron không có màn hình. Script sẽ tự chết ngay từ những dòng đầu tiên do "Chrome failed to start - No display".
*   **Cách 1:** Cấu hình Chrome trong Python chạy dưới chế độ ảo: `options.add_argument('--headless')`
*   **Cách 2:** Nhúng biến trình giả lập màn hình ảo (`Xvfb`, `X11`) trực tiếp vào crontab:
    ```bash
    * * * * * export DISPLAY=:10.0 && /path/to/python /path/to/script.py
    ```

## 4. Báo Cáo Kết Quả Và Lưu Log Lại
Khi bạn tự gõ lệnh, lỗi sẽ hiện ra bảng đen (terminal). Nhưng ở Cron thì không, bất kỳ dòng `print()` hay kể cả lúc Crash (sập), lỗi sẽ "rơi vào hư không". Bạn sẽ không thể biết tại sao nó không chạy lại.
*   **Giải pháp:** Phải yêu cầu Cron viết tất cả mọi kết quả ra một file log. 
    ```bash
    * * * * * ...python script.py >> /home/ubuntu/.../cron.log 2>&1
    ```
    *(Ghi chú thuật ngữ: `>>` là ghi đè nối tiếp, `2>&1` là hãy viết cả Log Bình Thường và Log Lỗi Error vào cùng một chỗ).*

## 5. Script Bị Treo Hoặc Chạy Đè Nhau
Nếu script cũ của bạn chạy mất 2 tiếng mới xong, nhưng bạn lại hẹn giờ `crontab` chạy 1 tiếng 1 lần -> Sẽ có hiện tượng cả 2-3 kịch bản cùng tự động mở lên, đá nhau và lật máy chủ.
*   **Giải pháp:** Sử dụng code cơ bản để chặn nếu trình đang chạy sẵn (như file `.lock`), hoặc cấu hình cron ở giãn khoảng cách rộng hơn thời gian tối đa chạy kịch bản đó.

---

### TÓM TẮT MẪU 1 LỆNH CRONTAB HOÀN HẢO CHO AUTOMATION / SELENIUM:

```bash
0 */8 * * * export DISPLAY=:10.0 && cd /home/ubuntu/SELENIUM_ZALO && /home/ubuntu/SELENIUM_ZALO/venv/bin/python /home/ubuntu/SELENIUM_ZALO/OpenFBV2POST.py >> /home/ubuntu/SELENIUM_ZALO/cron_fb.log 2>&1
```

> **Giải nghĩa:**
> 1. `0 */8 * * *`: Chạy chương trình mỗi 8 tiếng.
> 2. `export DISPLAY=:10.0`: Cung cấp màn hình giả lập cho Selenium tránh sập.
> 3. `cd /home/ubuntu/SELENIUM_ZALO`: Cố định con trỏ đường dẫn tại thẳng thư mục dự án để đọc file linh tinh (config/excel) không bị lỗi.
> 4. `.../venv/bin/python`: Đảm bảo dùng Python bên trong môi trường ảo đầy đủ module.
> 5. `.../OpenFBV2POST.py`: Chạy file script.
> 6. `>> .../cron_fb.log 2>&1`: Ném lại tất cả nhật ký lỗi hoặc `print` vào file log để dễ debug.
