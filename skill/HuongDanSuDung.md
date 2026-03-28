# HƯỚNG DẪN SỬ DỤNG TOOL AUTO GỬI TIN NHẮN ZALO

Tài liệu này hướng dẫn cách cấu hình và chạy File `.exe` trên một thiết bị máy tính thông thường chạy hệ điều hành Windows.

## 1. Chuẩn Bị
Bạn hãy đảm bảo để đúng **2 file** này nằm chung trong 1 thư mục (Ví dụ: Desktop \ ToolZalo):
- `OpenZaloSendContact.exe` (Phần mềm gửi Zalo)
- `gen-lang-client-0450618162-54ea7d476a02.json` (File khóa bảo mật để kết nối Google Sheet)

**Yêu cầu cơ bản:**
- Máy tính phải được cài sẵn Google Chrome.
- **TUYỆT ĐỐI KHÔNG COPY** thư mục `zalo-chrome-profile` từ máy khác mang qua, vì máy người nào dùng sẽ tự động phát sinh bộ nhớ cho tài khoản Zalo của người đó ở các thế hệ chạy sau này.

---

## 2. Cách Chỉnh Sửa Nội Dung Gửi
1. Mở file Google Sheet (bạn đã được cấp quyền truy cập qua trình duyệt web).
2. Tại cột **Phone**, ghi chính xác số điện thoại Zalo của khách hàng (hoặc tên Nhóm/Tài khoản đã lưu) *kể cả viết hoa viết thường*. Dữ liệu có thể có hoặc không có số 0 ở đầu đều được, tool sẽ tự động tối ưu.
3. Tại cột **Message**, ghi nội dung bạn muốn Tool tự động đánh chữ.
4. Nếu bạn để trống cột **Message**, Tool sẽ chỉ bỏ qua người đó hoặc báo lỗi nhưng vẫn mở Tab người đó lên.
5. Cột **Status**: Tool sẽ tự động điền chữ `APPROVED` vào nếu tin nhắn đã gửi thành công. Nếu bạn muốn gửi lại cho một người, hãy xóa chữ `APPROVED` ở người đó đi. (Hệ thống Google Sheet sẽ tự động lưu lại mà không cần bấm Save).

---

## 3. Cách Vận Hành Tool Lần Đầu Tiên (QUAN TRỌNG)

1. Click Đúp vào file `OpenZaloSendContact.exe`. Một cửa sổ Console lệnh màu đen xuất hiện và sẽ tự bật trình duyệt Chrome lên website zalo (nếu Chrome nhấp nháy, hãy chuyển sang nó).
2. **Trong lần cấu hình này**, Tool sẽ tự động phát hiện phiên bản trình duyệt Zalo Web hoàn toàn trống (do máy mới chưa có dữ liệu).
3. Tool sẽ chờ và cho phép bạn **tối đa 5 phút** để lấy điện thoại của bạn ra quét mã **QR Đăng Nhập Zalo Web**.
4. **Ngay sau khi đăng nhập xong**, dữ liệu sẽ tự động được tải. Tool sẽ tự động đọc dữ liệu từ Google Sheet để lấy danh sách số điện thoại hỗ trợ gửi tin nhắn, và bắt đầu công việc.
5. Lúc này, trên máy của bạn sẽ tự động **xuất hiện thêm một folder ẩn** tên là `zalo-chrome-profile`. Nó ghi nhận bộ nhớ máy tính Zalo của bạn.

> 💡 **Từ những lần chạy thứ 2 trở đi**: Bạn chỉ cần bấm file `.exe`, bạn không hề cần cầm điện thoại quét lại mã Zalo QR Code nữa! Tool sẽ tự động bỏ qua giai đoạn Đăng nhập và đi gửi luôn.

---

## 4. Xử Lý Các Trường Hợp Lỗi (Rất Hay Xảy Ra)

### ❌ Lỗi: "session not created: DevToolsActivePort file doesn't exist"
**Hiện tượng:** Vừa click đúp vào file exe, màn hình đen chớp lỗi đỏ rực và đóng sập. Văng lỗi như trên.
**Lý do:** Đang có một tiến trình Chrome bị treo ẩn / ngầm ở dưới máy tính đang khóa chặt thư mục gốc từ lần tắt trước, hoặc do chính bạn bực tức tắt ngang file `.exe` bằng dấu X mà chưa chờ nó thoát.
**Cách fix 100%:** 
- Bấm tổ hợp phím **Ctrl + Shift + Esc** trên bàn phím để mở hệ thống **Task Manager**.
- Kéo xuống tìm bất kể cái gì có dòng chữ mang tên **Google Chrome**. Bấm chuột phải lên nó chọn **End Task**. Sau đó chạy lại.

### ❌ Lỗi: Chạy Tool quá thời gian 5 phút
**Nguyên nhân:** Tool chờ bạn cầm điện thoại ra quét QR nhưng bạn không kịp làm trong hạn định 300 giây. Tool tự động tắt ngầm để tránh ngốn RAM. Hãy click mở lại lần nữa thao tác lẹ hơn!

### ❌ Mẹo: Xóa Tài khoản Zalo để dùng nick khác
Bạn chỉ cần click chuột trái chọn folder tên là `zalo-chrome-profile` và nhấn nút **Delete**. Lần chạy `.exe` ngay tiếp theo giao diện Quét QR sẽ tự xuất hiện lại bình thường.
