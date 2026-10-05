# Quét toàn sàn: kích hoạt kết quả đã công bố

## Hành vi

- Mở **Quét toàn sàn**: chỉ hiện lời giới thiệu và nút **Kích hoạt kết quả**. Chưa đọc API hoặc render danh sách mã.
- Kích hoạt: gọi `GET /api/scan/latest` để đọc snapshot. Không gọi `POST /api/quant/jobs`, không import hoặc chạy lại engine Python.
- Kết quả giữ nguyên khi chuyển giữa các trang trong phiên hiện tại. Reload trang sẽ trở về trạng thái chưa kích hoạt.
- **Lấy bản công bố mới** đọc lại file khi người dùng yêu cầu. Không polling hoặc bắt đầu vòng chạy mới.
- Bản công bố có timestamp, run ID, phiên, thời điểm dữ liệu, chu kỳ và phạm vi. Quá chu kỳ thì báo cũ, không thay timestamp để giả dữ liệu mới.
- Đọc thất bại: báo lỗi, cho thử lại. Khi refresh lỗi, giữ kết quả cũ. Không tự chuyển snapshot thật thành dữ liệu mẫu.
- Repo chưa có vòng chạy 2 giờ hoặc trang quét trong ảnh VPS. Trang mới có adapter đọc file để nối với pipeline đó. Mặc định dùng `shared/scan-demo.json`: 21 mã của fixture hiện tại, không giả lập 1.523 mã hoặc khuyến nghị đầu tư.

## Nối kết quả vòng chạy Python hiện tại

1. Giữ lịch chạy của pipeline hiện tại. Sau mỗi lần chạy thành công, chuyển kết quả sang JSON theo contract dưới đây.
2. Ghi file tạm cùng thư mục rồi dùng `os.replace(temp_path, snapshot_path)` để công bố nguyên tử. Không ghi đè trực tiếp file đang được API đọc; giữ bản công bố trước khi vòng chạy mới thất bại.
3. Đặt biến môi trường của dịch vụ API: `QUANTIK_SCAN_SNAPSHOT=/duong/dan/tuyet/doi/scan-latest.json`. Dịch vụ API phải đọc được file này. Cấu hình trong systemd/PM2/container đang vận hành rồi restart dịch vụ API một lần để nhận env.
4. API đọc file ở mỗi lần kích hoạt hoặc lấy bản mới; không cần restart API khi file cập nhật. Proxy `/api/scan/latest` tới cùng backend FastAPI như các API khác. Đừng cache endpoint này ở reverse proxy/CDN.

Ví dụ contract (một mã để minh họa định dạng; `null` nghĩa là chưa có kết quả):

```json
{
  "runId": "pipeline-run-id",
  "publishedAt": "2026-10-05T01:25:11Z",
  "dataAsOf": "2026-10-02",
  "session": "PRE_OPEN",
  "mode": "published",
  "source": "QuanTik scheduled pipeline",
  "cadenceMinutes": 120,
  "universeCount": 1523,
  "rows": [{
    "symbol": "FPT",
    "name": "Công nghệ FPT",
    "exchange": "HOSE",
    "sector": "Công nghệ",
    "recommendation": null,
    "passed": null,
    "explanation": null,
    "score": null,
    "rating": null,
    "holdingSessions": null,
    "indexTrend": null
  }]
}
```

`universeCount` là số mã pipeline thực sự khảo sát, `rows` là kết quả được công bố. Không tự điền điểm, khuyến nghị hoặc trạng thái đạt bộ lọc khi pipeline không cung cấp. `publishedAt` cần timezone (UTC `Z` hoặc offset), `score` trong 0–100 nếu có, mã duy nhất; `passed` chỉ nhận `true`, `false` hoặc `null`. Backend từ chối file lỗi/không tồn tại bằng 503 và không lộ đường dẫn file trong phản hồi.

Trang quét mở đánh giá theo mã bằng cửa sổ hiện tại của repo. Để xem toàn bộ báo cáo thật cho các mã ngoài catalog mẫu, cần nối catalog và báo cáo của pipeline VPS vào adapter hiện có; repo hiện chưa chứa phần đó.

## Premium sau này

Hiện tại nút là bước mở giao diện, không thu phí và không phải kiểm soát truy cập. API đọc snapshot chưa yêu cầu đăng nhập. Nếu triển khai Premium, thêm kiểm tra đăng nhập/quyền gói phía server cho endpoint này và các endpoint báo cáo chi tiết; bảo vệ cả file snapshot trên VPS. Không dùng state trong trình duyệt hoặc CSS ẩn làm cơ chế khóa trả phí.

## Thiết kế

Nền gần đen, mảng xanh rừng, vệt cam theo standee; bảng và popup giữ nền đặc để dễ đọc. Tất cả chữ giao diện vẫn dùng IBM Plex Mono; KaTeX giữ font toán. Có bản sáng, hỗ trợ giảm chuyển động, nút/nhãn bàn phím, bảng cuộn ngang và bộ lọc trên điện thoại.
