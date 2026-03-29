# Hướng Dẫn Deploy Tool Zalo Lên VPS Linux (Ubuntu)

Vì script của bạn sử dụng Google Chrome (Selenium) và yêu cầu **giao diện để quét mã QR Zalo**, việc deploy lên máy chủ Linux không có màn hình (Headless) sẽ gặp khó khăn. Cách **dễ nhất và ổn định nhất** là cài một giao diện màn hình ảo (Desktop Environment) lên VPS Linux, sau đó dùng Remote Desktop để vào quét mã QR giống hệt như đang dùng Windows.

Dưới đây là các bước chi tiết dành cho hệ điều hành **Ubuntu 20.04 / 22.04**:

---

### Bước 1: Cài đặt giao diện (Remote Desktop) trên Ubuntu VPS

Mở Terminal của VPS (thông qua SSH/PuTTY) và chạy các lệnh sau để cài đặt giao diện nhẹ **XFCE** và ứng dụng Remote Desktop **xRDP**:

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt giao diện XFCE4 (Rất nhẹ, phù hợp cho VPS)
sudo apt-get install xfce4 xfce4-goodies -y

# 3. Cài đặt xRDP để kết nối từ xa
sudo apt-get install xrdp -y

# 4. Cấu hình xRDP sử dụng giao diện XFCE
echo xfce4-session > ~/.xsession
sudo systemctl enable xrdp
sudo systemctl restart xrdp
```

### Bước 2: Kết nối VPS bằng Windows Remote Desktop
1. Trên máy vi tính của bạn, mở **Remote Desktop Connection** (có sẵn trên Windows).
2. Nhập **Địa chỉ IP** của VPS Linux vào và nhấn Connect.
3. Trong màn hình đăng nhập hiện ra, điền `username` (thường là `root` hoặc `ubuntu`) và `mật khẩu` VPS của bạn.
4. Lập tức bạn sẽ nhìn thấy một màn hình Desktop y hệt như 1 cái máy tính bình thường!

---

### Bước 3: Cài đặt Môi trường Python và Google Chrome
Trên màn hình Remote Desktop của VPS vừa vào, mở **Terminal Emulator** (như CMD ở Windows) và chạy các lệnh sau:

```bash
# 1. Tải và cài đặt Google Chrome
sudo apt --fix-broken install -y
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb


# 2. Cài đặt Python 3, Pip
sudo apt install python3 python3-pip python-is-python3 -y
```

---
uname -r
### Bước 4: Chuyển mã nguồn lên VPS và Chạy API
Bạn có thể copy trực tiếp toàn bộ thư mục `Zalo-Contact-Code` từ máy Windows lên VPS bằng cách Copy (Ctrl+C) ở máy Windows và Paste (Ctrl+V) thẳng vào màn hình VPS (nhờ tính năng của phần mềm Remote Desktop), hoặc dùng phần mềm truyền file như FileZilla.

Sau khi đã có thư mục code trên VPS, mở Terminal ở trong thư mục đó, thực hiện:

```bash
# 1. Cài đặt các thư viện cần thiết
pip install selenium gspread pandas oauth2client flask

# 2. Chạy API Server
python zalo_api.py
```

### 💡 Lưu ý cực kỳ quan trọng:
* Ở lần chạy đầu tiên trên VPS thông qua màn hình Remote Desktop, **Chrome sẽ hiện ra và yêu cầu mã QR**. Bạn mở Zalo trên điện thoại ra quét mã QR như bình thường.
* Sau khi quét mã QR thành công, session đăng nhập Zalo sẽ được lưu vào mục `zalo-chrome-profile` trong VPS. 
* Cổng API nhận lệnh trên n8n bây giờ sẽ là: `http://<IP-CỦA-VPS>:5000/send-message`

---

## (Tùy chọn) Chạy ngầm API Server vĩnh viễn (Kể cả khi tắt Remote Desktop)
Nếu bạn tắt Terminal của Remote Desktop thì Server API sẽ bị thoát theo. Để nó chạy nền 24/7 không bao giờ chết dù bị crash, bạn dùng công cụ Screen hoặc Nohup:

```bash
# Cách dùng nohup (đơn giản nhất)
nohup python zalo_api.py &
```
Lúc này bạn có thể tắt ngang cửa sổ Terminal, Server API vẫn đang chạy ngầm trên VPS và chờ n8n gọi bất kì lúc nào.
