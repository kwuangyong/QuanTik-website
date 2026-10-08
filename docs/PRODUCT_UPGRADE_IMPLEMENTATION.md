# QuanTik — triển khai giao diện theo plan

Ngày 08/10/2026. Base: `kwuangyong/QuanTik-website:main` tại `5734a03aecd131808943bbff997ea0dcc18a7075`. Tham chiếu plan trong [PR #3](https://github.com/kwuangyong/QuanTik-website/pull/3). Đây là code tích hợp trực tiếp vào UI/UX của fork, không nhập layout/CSS/source của Site demo.

## Những thay đổi đã triển khai

| Khu vực | Hành vi |
| --- | --- |
| Quét toàn sàn | Giữ nút kích hoạt, đọc snapshot đã công bố. Hai bảng tối đa 5 nổi bật / 5 cần thận trọng; không trùng và không bù bằng mã lỗi. |
| Tỷ suất đánh giá | Bốn preset cột; mở rộng đủ 50 trường từ schema Excel. Giá thô VND chuyển nghìn VND một lần; null khác 0. Nhãn WinRate giá đổi thành tỷ lệ phiên tăng. |
| Nút Quant | Cạnh ticker trong mỗi bảng highlights; nút Chạy Quant ở toolbar ngay cạnh chart trong popup. Nút từ scan mở popup và chạy một job. Click ticker thông thường chỉ mở chart. |
| Đồng bộ job | Controller chung theo symbol trong browser session; backend tái sử dụng job queued/running cùng symbol/data/model. Đóng/thu gọn popup không enqueue lại hoặc hủy job. |
| Visual | Cone P05/P25/P50/P75/P95, histogram return, HMM probabilities + price, historical drawdown, factor radar, risk/payoff. Có bảng số để đọc qua bàn phím, chọn toàn cửa sổ hoặc 10 quan sát cuối. |
| Thuật ngữ | Hover/focus/chạm ghim thẻ gồm lý thuyết, công thức, ví dụ, ngưỡng/điều kiện, cách dùng; có biến/tham số và giới hạn. |
| Bảng điện | Mặc định mở book 3 mức, khớp lệnh, TC/trần/sàn, thống kê và khối ngoại. Tất cả listing có hàng dù chưa có quote. Không cap 500 mã hoặc dựa vào scan. Với >300 mã chỉ render cửa sổ hàng để cuộn; dữ liệu tìm/sort vẫn trên toàn listing. |

## Phạm vi dữ liệu thực và demo

Fork này chưa chứa quant core của upstream. `backend/adapters.py` vẫn là adapter mô phỏng có sẵn. PR này không chỉnh scoring hay cài một mô hình mới.

- Scan thật: cấu hình `QUANTIK_SCAN_SNAPSHOT` trỏ file công bố của pipeline hiện có. Các chỉ số được giữ nguyên từ nguồn, thiếu thì hiện `—`. `shared/scan-fields.json` liệt kê chính xác 50 field, label, đơn vị và ghi chú.
- Bảng điện thật: cấu hình `QUANTIK_MARKET_SNAPSHOT` trỏ file snapshot của collector/provider. Có `instruments` đầy đủ và `quotes` theo hợp đồng dưới đây. Nếu file cấu hình lỗi, API trả 503, không thay bằng demo. Catalog thiếu mã từ nguồn không thể được frontend tự bổ sung thành dữ liệu sàn thật.
- Quant thật: cần nối các adapter load/run/summarize/metrics/render vào quant core đang vận hành, rồi trả `research_payload` có cấu trúc. Job cho mã ngoài sample catalog hiện vẫn bị từ chối cho đến khi catalog/context thật được nối vào adapter. Không giả tạo mô hình cho mã ngoài catalog.
- Visual demo: fixture cố định `shared/research-demo.json`, ghi rõ mô phỏng. Được scale theo giá mẫu để kiểm tra đơn vị; không có mô phỏng, fitting HMM hoặc dự báo thật. Job thiếu research ở nguồn thật hiển thị panel thiếu dữ liệu, không mượn fixture.
- Ảnh pipeline thật được giữ; ảnh placeholder demo không chen vào giữa visual mới. TradingView vẫn là nguồn chart độc lập, mapping cần được xác minh tại môi trường thật.

## Quy tắc chọn 5/5

Một lượt đọc resolve một snapshot duy nhất; cả hai nhóm mang cùng `runId`/thời điểm nguồn. Bộ lọc chỉ thu hẹp tối đa 10 mã đã chọn, không xếp hạng lại universe. Context scan được giữ trong popup; job riêng không sửa snapshot scan.

Eligible: score hữu hạn trong 0–100, không DQ FAIL/FAILED/ERROR, không analysis failed/error. Nổi bật: BUY_NOW/BUY_SETUP chỉ được ưu tiên khi gate được xác nhận `true`, sau đó WATCH/nhãn chưa có; tie theo score giảm và symbol tăng. AVOID không vào nhóm nổi bật. Thận trọng: các mã còn lại, ưu tiên AVOID rồi score thấp, tie theo symbol. Khi chỉ có AVOID, nhóm nổi bật rỗng. Khi <10 eligible, hiển thị đúng số, không trùng.

Score không tạo hành động mua. BUY_NOW count cần gate thật. Hành động mua có gate thiếu được gắn thêm “gate chưa xác nhận”. Đây là highlights trong tập phân tích, không bảo đảm 5 mã đều mua được hoặc 5 mã xấu nhất thị trường.

Endpoint mới `GET /api/scan/latest/highlights` chỉ đọc và chọn, không submit job. Endpoint `/api/scan/latest` cũ vẫn giữ cho tương thích. Frontend chỉ fallback sang endpoint cũ khi backend trả 404; lỗi 503 giữ lỗi/cached snapshot, không lấy demo ngầm. Hai nhóm/detail 50 fields đi cùng một response nên không trộn run. Chưa thêm API report/OHLCV lưu trữ theo run hoặc retention lịch sử; đó là phần tiếp theo khi nối core.

## Contract bổ sung

### Scan row

Giữ các field cũ (`symbol`, `name`, `exchange`, `recommendation`, `passed`, `score`…). Bổ sung field snake_case trong `shared/scan-fields.json`. `_pct` là số phần trăm, ví dụ `5.4` là 5,4%; `_vnd` là giá trị VND. Số finite/null; không gửi `"5%"` hoặc `"16,7"`. `action` là enum/nhãn từ nguồn, `gate_pass` là boolean/null, `gate_reasons` và flags có thể là mảng chuỗi. Backend giữ extras qua Pydantic và kiểm tra các field số. Scope/model version/cửa sổ có thể giữ kèm từng row.

### Market snapshot

```json
{
  "mode": "eod",
  "source": "Tên nguồn thật",
  "asOf": "2026-10-08T08:00:00Z",
  "units": {"price": "VND", "volume": "shares", "value": "VND"},
  "classification": {"mode": "provider"},
  "sectors": [{"id": "technology", "name": "Công nghệ"}],
  "instruments": [{"symbol": "FPT", "name": "FPT", "exchange": "HOSE", "sectorId": "technology", "tvSymbol": null}],
  "quotes": [{"symbol": "FPT", "price": null, "ref": null, "vol": 0, "bids": [], "asks": []}]
}
```

`instruments` phải là full listing nguồn; quote thiếu vẫn có hàng trống. `tvSymbol` chỉ đặt khi mapping đã được xác minh. Mặc định nhãn độ trễ chưa xác nhận; chỉ giữ `mode:live` nếu có `verifiedLive:true` từ adapter chịu trách nhiệm xác minh feed. Timestamp lấy từ nguồn, không tự đổi sang giờ request. Người vận hành cần công bố coverage và bảo đảm collector ghi file nguyên tử; không cung cấp feed realtime mới trong PR này.

### Research

`job.research` dùng `schemaVersion:1`, `symbol`, `mode`, `asOf`, `source`, `units:{price:"VND",return:"pct"}`, `horizonSessions`, `simulationCount`. Sáu arrays:

| Array | Fields |
| --- | --- |
| cone | `session`, `p05`, `p25`, `p50`, `p75`, `p95` — giá VND, các phân vị có thứ tự |
| distribution | `returnPct`, `probabilityPct` — các bin và tỷ lệ % cuối kỳ |
| regime | `date`, `price`, `state`, `probabilities:{bull,bear,sideways}` — xác suất 0–1 tổng 1, nhãn đã ánh xạ |
| drawdown | `date`, `valuePct` — số âm từ −100 tới 0 |
| factors | `id`, `label`, `value`, `min`, `max` — tên và miền chuẩn hóa của từng nhân tố |
| riskMetrics | `id`, `label`, `value`, `unit` — đủ phương pháp/horizon ở metadata nguồn |

Trả aggregates trước khi loại raw paths/HMM history khỏi core report. Không gửi raw Monte Carlo paths qua browser. Data sai symbol/units không render. Giá trị thiếu không được kéo thành 0 hay chuyển nhãn factor. R:R gộp chỉ tính nếu SL<Entry<TP2; cùng đơn vị summary nghìn VND, không giả net R:R từ TP distance.

## Kiểm tra và bước review còn lại

Commands kiểm tra:

```bash
pnpm install --frozen-lockfile
pnpm test
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/api_smoke.py
pnpm build
git diff --check
```

Đã kiểm tra business rules, null/0/units, partial listing 1.700 mã và refresh hai lượt, duplicate job, fixture/source distinction, render React 10 nút và 6 visual, toàn bộ LaTeX. HTTP smoke chạy loopback để kiểm tra routing FastAPI và payload đã serialize.

Chưa xác minh qua trình duyệt 360/768/1440px, khả năng focus khi cuộn bảng ảo, tooltip trong modal hoặc TradingView ngoài môi trường triển khai. Chưa smoke test VPS/collector thật hoặc kiểm định forecast/alpha. Cần review các điểm này trước merge/deploy; đặc biệt actual coverage của provider không thể suy từ fixture. PR không tự merge hoặc deploy VPS.

## Phản biện sản phẩm cho lần review này

1. Nhóm 5 nổi bật nên giữ WATCH khi không có BUY_NOW; nếu muốn chỉ setup mua, chấp nhận bảng rỗng thay vì đổi score thành khuyến nghị.
2. Người dùng cần đọc net forecast, chi phí và drawdown cạnh score. Không đặt Meta trust/đồng thuận thành một con số “xác suất thắng” chung.
3. Visual đẹp chỉ có giá trị khi đúng snapshot và dữ liệu. Ưu tiên nối nguồn thật trước khi mở thêm AI chat hoặc Premium.
4. Bảng điện đầy đủ cần catalog/provider đủ coverage; UI không thể tạo room khối ngoại hay lịch sử HMM khi nguồn thiếu.
