# QuanTik — Không gian đầu tư định lượng

Dashboard React + FastAPI cho cổ phiếu Việt Nam, gồm tổng quan thị trường, bảng điện, nhóm ngành, theo dõi, workspace biểu đồ/Quant và báo cáo theo từng mã. Có chế độ sáng/tối, bố cục điện thoại và logo/favicon QuanTik. Toàn bộ chữ giao diện dùng IBM Plex Mono theo phong cách terminal; fallback monospace khi chưa tải được font.

## Chạy trên máy

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Chạy API trong terminal khác:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8000
```

Mở http://localhost:5173. Có thể dùng `npm install`/`npm run dev` thay cho pnpm. Khi API mất kết nối, giao diện giữ snapshot gần nhất hoặc mẫu tĩnh và báo trạng thái. Nút “Xem kết quả mẫu” minh họa bố cục khi API không hoạt động.

## Các chức năng đã triển khai

- Bảng điện có ba mức dư mua/dư bán, khớp lệnh, tham chiếu/trần/sàn, thống kê giao dịch và khối ngoại. Bật/tắt nhóm cột, lọc sàn/ngành, tìm kiếm và sắp xếp; bảng cuộn ngang trong vùng riêng.
- Nhóm ngành hiển thị biến động trung bình đều, độ rộng, thanh khoản và độ phủ dữ liệu. Đây là thống kê từ tập mẫu đang lọc, không phải chỉ số ngành chính thức.
- Bấm mã để mở workspace: biểu đồ bên cạnh panel phân tích có thể thu gọn và kéo thay đổi kích thước. Trên điện thoại, panel nằm phía dưới. Thu gọn panel giữ kết quả và không khởi chạy lại job.
- Bộ chọn khung nến gồm 1/3/5/15/30 phút, 1/2/4 giờ, ngày, tuần và tháng; cấu hình widget mở toolbar/chỉ báo/công cụ vẽ. Các chức năng thực tế phụ thuộc TradingView và dữ liệu từng mã. Đổi khung bằng selector QuanTik tạo lại widget; dùng toolbar TradingView khi cần giữ thao tác trong chart.
- Di chuột hoặc focus vào thuật ngữ gạch chân ngay trong báo cáo để xem ý nghĩa/công thức và cách dùng. Trên điện thoại, chạm để giữ popup; Escape hoặc chạm bên ngoài để đóng. Không có trang tra cứu công thức riêng.
- Từng mục báo cáo (hiệu suất, biến động, tín hiệu, rủi ro) mở/thu gọn độc lập theo mã đang xem. Quant giữ hàng summary và ảnh từ API như main; pipeline có thể trả `reportSections` gồm id/title/text để giữ nguyên lời phân tích và tự gạch chân các thuật ngữ đã đăng ký.
- 21 chỉ số từ `Chỉ số.xlsx` có nguồn hàng/sheet, công thức tham chiếu và ngưỡng gốc. Công thức hiển thị bằng KaTeX; chưa tính được thì giá trị là “—”. Popup giải thích thêm thuật ngữ thị trường, chỉ báo, HMM, Quant Factor và PSR/DSR.
- Theo dõi cổ phiếu, màu giao diện và kích thước panel được lưu trên trình duyệt. Ô lệnh hỗ trợ `FPT`, `FPT CHART`, `FPT Q`, `WATCH`, `MARKET`; phím `/` mở ô lệnh.
- Logo trong header và favicon đã được khai báo.

## Dữ liệu và tích hợp pipeline thật

**Bảng giá, phân ngành, điểm Quant và phân tích API hiện là mô phỏng.** Snapshot cố định trong `shared/market-demo.json` được dùng chung giữa frontend và backend, có nguồn, thời điểm, phiên bản và đơn vị. Giá API bảng điện dùng VND; khối lượng dùng cổ phiếu. Summary Quant ghi đơn vị giá nghìn VND riêng. Thiếu dữ liệu dùng `null`, không thay bằng 0.

TradingView dùng nguồn độc lập. Danh mục có `exchange` và `tvSymbol`; các mã HNX/UPCOM chưa có mapping đã xác minh hiển thị thông báo thay vì ghép thành HOSE. Mapping HOSE mẫu cũng chưa được kiểm tra khả năng tải của nhà cung cấp.

Thay các adapter `load_board`, `load_context`, `run_module`, `summarize`, `metric_results`, `render_image` trong `backend/adapters.py` bằng nguồn/pipeline thật và giữ hợp đồng dữ liệu. Định nghĩa công thức nằm trong `src/content/metrics.json`, thuật ngữ bổ sung trong `src/content/glossary.js`. Trả kèm `methodId`, tham số, trạng thái và nguồn cho kết quả thực; các phương pháp như Confidence, HMM và Entry/SL Quality cần xác nhận với pipeline.

| API | Vai trò |
| --- | --- |
| `GET /api/board?exchange=HOSE&sector=banks` | Envelope snapshot và lọc danh mục |
| `GET /api/instruments`, `GET /api/sectors` | Danh mục mã và phân ngành |
| `GET /api/sectors/summary` | Thống kê ngành từ tập dữ liệu mẫu |
| `GET /api/quant/modules` | Module phân tích |
| `POST /api/quant/jobs` | Tạo job với symbol và modules; kiểm tra đầu vào |
| `GET /api/quant/jobs/{id}` | Tiến trình, summary và metrics có cấu trúc |
| `GET /api/quant/jobs/{id}/image` | Ảnh tổng quan bổ sung |

Bảng điện polling 5 giây, hủy request khi unmount và tránh request chồng nhau. Job polling 700 ms. Cache lưu cả JSON kết quả và ảnh, khóa theo mã/module/phiên bản dữ liệu/mô hình/khung ngày; kiểm tra lại phiên bản khi thay pipeline. Job registry và khóa cache nằm trong bộ nhớ, chưa có TTL/queue phân tán/xác thực; cần hoàn thiện trước production.

## Kiểm tra

```bash
npm test
python -m unittest discover -s tests -p 'test_backend.py'
npm run build
```

Kiểm tra trình duyệt tùy chọn (cần API dependencies, hai cổng 5173/8000 trống):

```bash
npm install --no-save playwright
npx playwright install chromium
node tests/e2e.cjs
```

Suite tự khởi động frontend/backend và kiểm tra bảng điện, ngành, thuật ngữ gạch chân, báo cáo mở/thu gọn từng mục, ảnh pipeline, job API mẫu, panel, lưu lựa chọn, mobile và mất kết nối. Script TradingView bên ngoài được chặn để kiểm tra QuanTik ổn định; suite **không xác nhận** dữ liệu, toolbar/chỉ báo hay các khung nến thực tế của nhà cung cấp. Có thể đặt `QUANTIK_CHROMIUM`/`QUANTIK_PYTHON` cho executable riêng. Ảnh kiểm tra ghi vào `/tmp/quantik-qa/`.

## Build / triển khai

```bash
npm run build
npm run preview
```

Frontend build vào `dist/`. Khi triển khai riêng frontend/backend, đặt `VITE_API_BASE=https://<api-host>/api` trước build và cập nhật CORS trong `backend/server.py`. Hoặc reverse proxy `/api` cùng domain tới FastAPI. `vite.config.js` chỉ proxy khi phát triển. Backend cần cả thư mục `shared/` và `src/content/` để đọc mẫu/định nghĩa; đóng gói toàn bộ repo khi chạy bản demo.

Kế hoạch gốc: [docs/implementation-plan.md](docs/implementation-plan.md). Phạm vi đã làm và phần cần nguồn thật: [docs/implementation-status.md](docs/implementation-status.md). Chưa triển khai production.
