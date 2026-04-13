# 🤖 Prompt Blueprint: Dùng AI Để Tự Động Cấu Hình Crontab Cho Các PC/Project Khác

Thay vì tự gõ lệnh, bạn có thể biến một Bot AI khác (như ChatGPT, Gemini trên PC khác, Claude...) thành trợ lý tự động gắn crontab. 

Sau này bạn cài qua PC hay VPS khác, chỉ cần **Copy nội dung khung dưới đây** + **Kèm yêu cầu mong muốn**, con BOT đó sẽ tự viết ra 1 câu lệnh để bạn Copy-Paste vào terminal là xong, khỏi cần mở Nano luôn.

---

### 👉 HÃY COPY TOÀN BỘ PHẦN BÊN DƯỚI VÀ GỬI CHO BOT AI:

```text
Bạn là một chuyên gia Linux System Admin xuất sắc. 
Tôi vừa code xong một script Python chạy tự động browser (Selenium). Tôi cần đưa file này lên Crontab để chạy theo lịch trình.

Hãy viết cho tôi MỘT CÂU LỆNH BASH DUY NHẤT (dùng cấu trúc `echo "..." | crontab -` hoặc tương đương) để tôi dán thẳng vào Terminal là hệ thống tự thiết lập crontab xong luôn, tôi KHÔNG muốn dùng `crontab -e` kết hợp với Text Editor.

⚡ CÁC QUY TẮC BẮT BUỘC KHI TẠO LỆNH CRONTAB:
1. Đừng tự chế đường dẫn tương đối. Hãy hỏi tôi Cung cấp [Đường dẫn tuyệt đối của thư mục dự án] và [Tên file Python] trước khi bạn xuất code (Trừ khi tôi đã nhập từ trước).
2. Lệnh gọi Python phải nhắm thẳng vào Python của môi trường ảo (ví dụ: /đường_dẫn/venv/bin/python) thay vì python chung của máy.
3. Vì đây là thiết lập có UI (Selenium), bắt buộc trước khi gọi python phải có khai báo màn hình hiển thị: `export DISPLAY=:10.0` và lệnh `cd` vào thư mục dự án.
4. Lệnh phải đính kèm xuất các file Log cả stdout lẫn stderr bằng đuôi `>> /đường_dẫn_log/cron.log 2>&1`
5. Nếu trong crontab cũ của tôi đang có lệnh khác, hãy đề xuất cách append (nối thêm) an toàn, tránh xóa mất crontab cũ. Xin hãy thêm lệnh `crontab -l` ở cuối để hệ thống in ra đối chiếu sau khi cài thành công.

Tôi muốn chạy file này với lịch trình: [HÃY ĐIỀN THỜI GIAN THEO Ý MUỐN VÀ ĐƯỜNG DẪN THƯ MỤC CỦA BẠN VÀO ĐÂY]. Hãy sinh code ra cho tôi!
```
