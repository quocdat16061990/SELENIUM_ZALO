# 🚀 Hướng Dẫn Nhanh: 3 Bước Đưa Python Lên Crontab

Bản hướng dẫn "mì ăn liền" này dành cho các bạn chỉ muốn cấu hình nhanh gọn lẹ ngay sau khi code xong. Không cần biết nhiều lý thuyết, chỉ cần làm đúng 3 bước là xong!

---

## Bước 1: Thu thập công thức đường dẫn
Trước khi gõ lệnh, bạn tuyệt đối không dùng đường dẫn tương đối (như `python code.py`). Hãy thay bằng thông số **đường dẫn tuyệt đối**. Hãy kết hợp 2 thông tin sau lại với nhau:
1. Đường dẫn chứa Python (trong venv của bạn): `/home/ubuntu/SELENIUM_ZALO/venv/bin/python`
2. Đường dẫn chứa file Code (.py): `/home/ubuntu/SELENIUM_ZALO/ten_file_cua_ban.py`

## Bước 2: Thiết lập cấu hình hệ thống
Mở cửa sổ dòng lệnh Terminal lên và gõ lệnh sau để gọi bảng điều khiển:
```bash
crontab -e
```
*(Nếu hệ thống hiện thông báo hỏi "Select an editor", hãy gõ phím **1** và bấm **Enter** để mở bằng giao diện Nano).*

## Bước 3: Đặt lịch và Lưu lại
Dùng phím mũi tên ⬇️ lướt chuột dời xuống dòng cuối cùng của màn hình. Dán 1 trong các ví dụ mẫu sau vào (chọn cái phù hợp với ý đồ của bạn):

**🎯 Mẫu 1: Chạy mỗi 8 tiếng 1 lần** (cho các script như đăng bài FB)
```bash
0 */8 * * * export DISPLAY=:10.0 && /home/ubuntu/SELENIUM_ZALO/venv/bin/python /home/ubuntu/SELENIUM_ZALO/ten_file_cua_ban.py >> /home/ubuntu/SELENIUM_ZALO/nhat_ky.log 2>&1
```

**🎯 Mẫu 2: Chạy đúng 1 lúc nào đó (Ví dụ 8:30 sáng hằng ngày)**
```bash
30 8 * * * export DISPLAY=:10.0 && /home/ubuntu/SELENIUM_ZALO/venv/bin/python /home/ubuntu/SELENIUM_ZALO/ten_file_cua_ban.py >> /home/ubuntu/SELENIUM_ZALO/nhat_ky.log 2>&1
```

**Cách lưu cấu hình (Nếu ở trong giao diện Nano):**
1. Bấm tổ hợp **Ctrl + O** (chữ o).
2. Nhấn phím **Enter** để lưu file.
3. Bấm tổ hợp **Ctrl + X** để thoát.

Nếu bạn thấy màn hình hiện chữ `crontab: installing new crontab` là thành công rồi nhé. Giờ là lúc tắt máy và để server kiếm tiền cho bạn!
