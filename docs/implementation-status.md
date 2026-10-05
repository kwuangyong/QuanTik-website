# Tiến độ triển khai QuanTik

## Mốc 05/10/2026: quét toàn sàn và màu theo standee

Nhánh `feature/scan-activation-brand` bắt đầu từ main của fork sau khi PR #1 được merge.

- Thêm trang Quét toàn sàn với nút kích hoạt trước khi đọc/hiện kết quả. GET `/api/scan/latest` chỉ đọc JSON có sẵn; không submit job hoặc rerun engine. Giữ kết quả khi đổi trang; reload đóng lại. Có bộ lọc, sắp xếp, metadata, cảnh báo cũ, lỗi/thử lại và chọn xem mẫu rõ ràng.
- Thêm adapter `QUANTIK_SCAN_SNAPSHOT` cho file do vòng chạy Python công bố. Repo chưa có scheduler/nguồn kết quả của VPS; hướng dẫn nối và contract ở [scan-snapshot.md](scan-snapshot.md). Mẫu gồm 21 mã từ fixture, không giả lập 1.523 kết quả. Khuyến nghị, trạng thái đạt và các trường chưa có nguồn vẫn để trống.
- Đổi palette sang nền đen, các mảng xanh rừng và vệt cam; giữ IBM Plex Mono, bảng/popup nền đặc và chế độ sáng.
- Xác minh: 7 kiểm tra Node, 7 kiểm tra Python, build Vite và suite Chromium 1440/390 px đều đạt. Suite mới kiểm tra không fetch trước kích hoạt, GET-only/no job, bộ lọc, đổi trang giữ kết quả, reload về nút kích hoạt, lỗi đọc/refresh giữ bản cũ và xem mẫu theo yêu cầu. Các luồng bảng điện/chart/popup hiện có vẫn đạt. TradingView thật vẫn chưa kiểm chứng vì script bị chặn trong kiểm tra tự động.
- Nút hiện là bước mở giao diện; Premium cần xác thực/quyền gói phía backend sau này. Chưa thu phí, chưa triển khai lên VPS hoặc domain thật.

Ảnh giao diện: [trước kích hoạt](previews/scan-activation.jpg), [sau kích hoạt](previews/scan-results.jpg), [điện thoại](previews/scan-mobile.jpg).

## Mốc 04/10/2026

Ngày 04/10/2026 · Nhánh `design/quantik-dashboard` · [PR #1](https://github.com/kwuangyong/QuanTik-website/pull/1)

Đã triển khai mốc giao diện và API mô phỏng của kế hoạch. Mốc dữ liệu thật còn phụ thuộc nguồn thị trường, mapping TradingView và pipeline Quant.

| Yêu cầu | Phần đã triển khai | Giới hạn còn lại |
| --- | --- | --- |
| Biểu đồ nhiều công cụ/khung nến | Workspace đầy đủ, cấu hình toolbar/công cụ vẽ/chỉ báo; selector phút/giờ/ngày/tuần/tháng; lỗi và tải lại | Chưa kiểm chứng provider trên dữ liệu thật. Widget không nhận feed QuanTik; cần đánh giá library nếu muốn chỉ báo riêng |
| Panel kéo và ẩn/hiện | Resize bằng chuột/bàn phím, thu gọn/mở lại, lưu kích thước; mobile panel phía dưới; giữ chart/job | Thay selector khung ngoài sẽ tạo lại widget; state nội bộ iframe phụ thuộc nhà cung cấp |
| Thuật ngữ và công thức | Thuật ngữ gạch chân trong nội dung; hover/focus popup có KaTeX, tham số, cách dùng và giới hạn; chạm trên mobile để giữ popup. Bỏ trang tra cứu riêng | Giá trị 21 chỉ số chưa tính bởi pipeline; một số định nghĩa phải xác nhận phương pháp thực |
| Excel 21 chỉ số | Registry đủ 21 mục, trọng số/ngưỡng/source row và công thức gốc; chuẩn hóa công thức tham chiếu | Ngưỡng là cấu hình tài liệu, không phải chuẩn chung; Confidence/HMM/Entry cần thỏa thuận định nghĩa |
| Bảng điện | Ba mức mua/bán, khớp lệnh, thống kê và khối ngoại; lọc/sắp xếp/nhóm cột; đơn vị và missing states rõ | Snapshot demo cố định; chưa có realtime/WebSocket hoặc feed chính thức |
| Nhóm ngành | Danh mục 10 nhóm, biến động trung bình đều, độ rộng/thanh khoản/độ phủ; bấm lọc mã | Phân ngành mẫu, chưa có nguồn/ngày hiệu lực chính thức; không phải chỉ số ngành |
| API và cache | Hợp đồng snapshot; catalog/sector endpoints; kiểm tra job; cache JSON+ảnh theo phiên bản; giữ dữ liệu khi offline | Module và summary là placeholder; job/lock trong memory, chưa có TTL/auth/queue production |
| Nhận diện thương hiệu | Header logo, favicon PNG/ICO | Dùng logo đã cung cấp |

## Xác minh đã thực hiện

- Năm kiểm tra Node: đơn vị/chuẩn hóa giá, trạng thái thiếu/không có số liệu, thống kê ngành công thức KaTeX/nguồn Excel và bảo toàn văn bản khi gắn popup.
- Bốn kiểm tra Python: danh mục/bộ lọc, đầu vào job, kết quả cache khớp lần chạy đầu và vô hiệu hóa theo phiên bản mô hình.
- Build Vite thành công. KaTeX bổ sung dung lượng bundle; cần tối ưu tải/chia bundle nếu mục tiêu tốc độ production yêu cầu.
- Chromium desktop 1440 px và mobile 390 px: lọc sàn/ngành, nhóm cột, tooltip/touch/Escape, từng mục báo cáo mở/thu gọn độc lập và ảnh API, job qua API mẫu, resize/thu gọn panel không rerun job, selector khung nến, local storage và offline fallback. Không có lỗi runtime frontend trong luồng kiểm tra.
- Script TradingView được chặn trong suite tự động; phần chart hiển thị fallback tương ứng. Kiểm tra này không chứng minh các chỉ báo hoặc dữ liệu của TradingView hoạt động.

## Công việc tiếp theo để có dữ liệu thật

1. Chọn nguồn bảng điện/OHLCV và xác nhận quyền dùng, cadence, đơn vị, giờ phiên, biên độ, quy tắc ATO/ATC và điều chỉnh giá. Điền danh mục sàn/phân ngành có ngày hiệu lực.
2. Kiểm chứng `tvSymbol` và từng khung dữ liệu của các mã HOSE/HNX/UPCOM trên TradingView. Nếu widget thiếu chức năng bắt buộc, đánh giá quyền dùng Advanced Charts và xây datafeed.
3. Nối module Quant; thống nhất phương pháp, lookback, risk-free rate, annualization, tail convention, Confidence và Entry/SL Quality. Trả methodId/parameters/status/asOf cho từng metric.
4. Thay sample adapter, chạy đối chiếu dữ liệu độc lập và kiểm tra cache với dataVersion thật. Bổ sung stale/session behavior theo feed thay vì snapshot mẫu.
5. Hoàn thiện vận hành trước production: CORS domain thật, xác thực/rate limit nếu có tài khoản, TTL/cache/job queue, logging và triển khai backend. Chưa merge/deploy trong lượt sửa này.

## Điều chỉnh theo phản hồi 04/10/2026

Bỏ trang tra cứu công thức và tab tra cứu trong chart. Công thức chỉ xuất hiện khi rê vào thuật ngữ gạch chân; các mục báo cáo của mỗi mã có nút mở/thu gọn riêng. Giữ luồng Quant như main: chọn module, tiến trình, summary, chạy lại và ảnh API dưới summary. Nguồn main trong fork chỉ có adapter ảnh placeholder, chưa chứa bộ visuals thực của website trong ảnh tham chiếu; demo tĩnh chưa chạy Python nên hiển thị ghi chú thay vì dựng giả ảnh pipeline.

## Quy ước font khi merge

Toàn bộ chữ giao diện, điều hướng, bảng giá, báo cáo và popup dùng **IBM Plex Mono**, với fallback monospace. Không dùng IBM Plex Sans cho UI. Công thức giữ font toán của KaTeX để hiển thị ký hiệu đúng. Quy ước này đã được áp dụng trên nhánh test và demo trước khi merge main.
