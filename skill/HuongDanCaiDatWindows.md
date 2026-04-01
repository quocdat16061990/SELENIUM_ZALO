# Hướng Dẫn Cài Đặt Môi Trường Và Thư Viện Trên Windows

Tài liệu này hướng dẫn cách cài đặt Python và các thư viện cần thiết để chạy dự án Selenium Zalo trên hệ điều hành Windows.

## 1. Cài Đặt Python
Nếu máy tính của bạn chưa có Python, vui lòng cài đặt theo các bước sau:

1. Truy cập trang web chính thức của Python: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Nhấn nút **Download Python** (ưu tiên tải bản 3.9, 3.10 hoặc mới hơn).
3. Mở file cài đặt (`.exe`) vừa tải về.
4. **QUAN TRỌNG:** Ở màn hình cài đặt đầu tiên, bạn **BẮT BUỘC PHẢI** tích chọn ô vuông có chữ **"Add Python to PATH"** (hoặc "Add Python to environment variables" tùy phiên bản). Điều này giúp bạn có thể chạy Python từ bất kỳ đâu trong Command Prompt.
5. Nhấn **Install Now** và đợi quá trình cài đặt hoàn tất.

## 2. Kiểm Trưởng Cài Đặt Python
1. Mở phần mềm **Command Prompt** (bạn có thể bấm phím `Windows` -> gõ `cmd` -> chọn `Command Prompt`).
2. Gõ lệnh sau để kiểm tra xem hệ thống đã nhận diện Python chưa:
   ```cmd
   python --version
   ```
   *Nếu hiển thị phiên bản (ví dụ: `Python 3.10.x`), nghĩa là bạn đã cài đặt thành công.*

3. Kiểm tra công cụ quản lý thư viện `pip`:
   ```cmd
   pip --version
   ```

## 3. Cài Đặt Các Thư Viện Cho Dự Án
Dự án yêu cầu một số thư viện bên thứ 3 để có thể chạy được (được liệt kê trong file `requirement.txt`). Để cài đặt nguyên một cụm, làm theo cách sau:

### Cách X: Cài qua file `requirement.txt` (Khuyên dùng)
1. Mở **Command Prompt** (hoặc PowerShell).
2. Dùng lệnh `cd` để di chuyển tới đường dẫn chứa dự án. Ví dụ nếu thư mục dự án của bạn nằm ở `C:\Users\QuocDat\Videos\SELENIUM_ZALO`, hãy gõ:
   ```cmd
   cd C:\Users\QuocDat\Videos\SELENIUM_ZALO
   ```
3. Chạy lệnh sau để cài đặt tất cả thư viện có trong file `requirement.txt`:
   ```cmd
   pip install -r requirement.txt
   ```
4. Đợi máy tải và cài đặt các gói (selenium, gspread, pandas, oauth2client, flask, pyinstaller) tự động.

### Cách Y: Cài đặt thủ công từng thư viện
Nếu bạn gặp vấn đề với file text, bạn có thể tự tay gõ lệnh cài đặt những gói này bằng câu lệnh:
```cmd
pip install selenium gspread pandas oauth2client flask pyinstaller
```

## 4. Xử lý lỗi phổ biến
- **Lỗi `Python was not found; run without arguments to install from the Microsoft Store...`**:
  - Máy bạn **chưa được cài đặt Python** hoặc Windows Store đang tranh quyền mở Python. 
  - **Cách sửa:** Bạn cần làm lại **Bước 1** bên trên: Tải Python về và bắt buộc tích vào ô **"Add Python to PATH"**. Cài xong, bạn hãy tắt đi và mở một cái Command Prompt MỚI rồi thử lại.
  - *(Tùy chọn cho Windows 10/11: Hoặc bạn có thể gõ lệnh `winget install -e --id Python.Python.3.11` vào Command Prompt để máy tự động cài).*
- **Lỗi `pip is not recognized as an internal or external command...`**: 
  - Nghĩa là ở Bước 1.4, bạn đã quên không tick `Add Python to PATH`. Bạn có thể mở lại file cài đặt Python, chọn "Modify" để sửa lỗi này.
- **Lỗi `Permission denied` hoặc cần quyền Admin**: 
  - Hãy bấm chuột phải vào ứng dụng **Command Prompt** và chọn **Run as Administrator** trước khi thực thi lệnh `pip install`.
- **Nâng cấp pip**: 
  - Nếu pip khuyên bạn nên cập nhật bản mới nhất, hãy dùng lệnh sau: `python -m pip install --upgrade pip`.

---
Sau khi cài đặt xong các thư viện trên, bạn có thể tiến hành chạy file code (ví dụ `python ten_file.py`) bình thường.
