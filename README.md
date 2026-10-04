# QuanTik — Không gian đầu tư định lượng

Dashboard React + Python cho cổ phiếu Việt Nam. Giao diện gồm Thị trường, Theo dõi, Phân tích Quant và Hướng dẫn; hỗ trợ chế độ sáng/tối và điện thoại.

## Chạy trên máy

```bash
npm install
npm run dev
```

Chạy API trong terminal khác:

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

Mở http://localhost:5173. Khi API không hoạt động, bảng giá dùng mẫu tĩnh và hiển thị thông báo. Phân tích Quant cần API hoạt động.

## Thao tác

- Lọc mã hoặc doanh nghiệp; bấm tiêu đề cột để sắp xếp bằng chuột hoặc bàn phím.
- Bấm ngôi sao để lưu cổ phiếu vào Theo dõi; danh sách và chế độ màu lưu trên trình duyệt.
- Chọn dòng để xem chi tiết; bấm đúp hoặc Enter để mở tổng quan.
- Tra cứu nhanh: `FPT`, `FPT CHART`, `FPT Q`, `WATCH`, `MARKET`. Phím `/` tập trung vào ô lệnh; Escape đóng cửa sổ chi tiết.
- Trang Phân tích Quant cho phép chọn cổ phiếu và module, xem tiến trình, kết quả và chạy lại.
- Biểu đồ TradingView cần Internet và hiển thị trạng thái lỗi/tải lại khi script không tải được.
- Mobile giữ các cột bảng giá với cuộn ngang bên trong bảng; điều hướng nằm phía dưới.

## Tích hợp pipeline thật

`backend/adapters.py` đang mô phỏng bảng giá và các module. Thay thân hàm `load_board`, `load_context`, `run_module`, `summarize`, `render_image` bằng pipeline thật, giữ định dạng trả về.

Luồng Quant: `POST /api/quant/jobs` → hỏi `GET /api/quant/jobs/{id}` mỗi 700 ms → hiển thị summary và ảnh `GET /api/quant/jobs/{id}/image`. Bảng giá cập nhật mỗi 5 giây.

**Giá, điểm Quant và kết quả phân tích hiện là mô phỏng.** Biểu đồ TradingView có nguồn độc lập. Nhóm VN30 hiện là tập con minh họa, không phải danh sách thành phần được cập nhật chính thức.

## Build / triển khai

```bash
npm run build
npm run preview
```

Frontend build vào `dist/`. Khi triển khai riêng frontend và backend, đặt `VITE_API_BASE=https://<api-host>/api` **trước khi build**; cập nhật CORS trong `backend/server.py` cho domain frontend. Hoặc cấu hình reverse proxy `/api` trên cùng domain tới FastAPI. `vite.config.js` chỉ proxy API trong môi trường phát triển.

Backend hiện là bản thử nghiệm: job/cache trong tiến trình, chưa có đăng nhập hoặc quản lý người dùng. Việc thiết kế giao diện chưa tích hợp pipeline thật hay triển khai production.
