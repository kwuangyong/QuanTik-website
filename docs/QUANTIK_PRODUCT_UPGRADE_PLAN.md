# QuanTik — Kế hoạch nâng cấp trải nghiệm phân tích và bảng điện

**Ngày:** 07/10/2026 · **Trạng thái:** đề xuất để phản biện, chưa triển khai runtime.  
**Repo đích:** `kappyphm/quantik-react` · **Nhánh đích:** `main`.  
**Đầu ra lượt này:** plan Markdown và PR tài liệu. Người dùng đã chọn “Plan trước”; các checkbox bên dưới là công việc tương lai, không phải tính năng đã hoàn thành.

## 0. Giữ UI/UX hiện tại của repo

**Ràng buộc đã xác nhận với người dùng:** giữ UI/UX và cấu trúc thiết kế hiện tại của QuanTik trong repo. Demo tại https://quantik-product-demo.quantlong21.chatgpt.site là bản thử độc lập để review vị trí nút, popup, visual và luồng tương tác. Không đưa layout, stylesheet hay ứng dụng demo vào repo như một lần thay giao diện.

Các PR implementation sẽ bổ sung tính năng vào component và design system đang có. Màu, typography, navigation, spacing và layout theo phiên bản repo tại thời điểm triển khai; cần kiểm tra giao diện hiện tại trước khi sửa code.

## 1. Mục tiêu sản phẩm

Giúp nhà đầu tư trả lời bốn câu hỏi: thị trường đang diễn ra thế nào; mã nào đáng xem hoặc cần thận trọng; vì sao hệ thống đánh giá như vậy; điều kiện nào khiến đánh giá không còn phù hợp.

| Yêu cầu | Hành vi đích | Ưu tiên |
| --- | --- | --- |
| Visual từng mã như `quant_visuals.py`, nâng cấp tiếp | Workspace phân tích có biểu đồ tương tác, dữ liệu có nguồn và thời điểm, các khối bằng chứng dễ đọc | P0 |
| Quét toàn sàn chỉ hiện 5 tốt nhất + 5 xấu nhất; thêm tỷ suất như Excel | Hai bảng tối đa 5 mã, xếp hạng cùng một snapshot; mở chi tiết thay vì bung danh sách đầy đủ | P0 |
| Hover thuật ngữ có lý thuyết, công thức, ví dụ, ngưỡng, cách dùng | Nâng cấp glossary và `TermHint`; hỗ trợ chuột, bàn phím và chạm | P0 |
| Bảng điện đầy đủ như bảng giá chứng khoán | Toàn bộ danh mục cổ phiếu của các sàn nguồn hỗ trợ, đầy đủ nhóm cột; không bị cắt theo top 10 scan hoặc trần 500 mã | P0 |
| Brainstorm và phản biện | Nhật ký quyết định, lựa chọn có đánh đổi, backlog theo giá trị người dùng | Xuyên suốt |

Phân tích quant và bảng điện có tốc độ cập nhật khác nhau. Giá mới không tự làm dự báo cũ trở thành dự báo mới. Mỗi loại thông tin phải có thời điểm riêng.

## 2. Căn cứ đã đọc và hiện trạng thực tế

### 2.1 Nguồn tham khảo

- Repo được đọc tại commit `66f0e38903dc42b2017d66032994b1660bafd932`. Đây là mốc khảo sát, không phải xác nhận trạng thái website đang chạy trên VPS.
- File đính kèm `quant_visuals.py`: có Quant Card, Probability Cone, Return Distribution, HMM Regime, Risk Profile, Radar, Terminal Dashboard, Client Recommendation và Risk–Return Map. Không chạy file đính kèm; đọc mã để đối chiếu cách trình bày và dữ liệu.
- Bản đính kèm `LỌC CỔ PHIẾU.xlsx`: 24 tab; schema đầu có 42 cột có tên, schema phổ biến có 50 cột. Đọc bản snapshot được cung cấp; không coi đây là dữ liệu thị trường hiện thời, không sửa file Google Drive gốc.
- Tab `Summary_20261005_2338`: 67 mã; 21 “THEO DÕI”, 46 “TRÁNH”, không có dòng đạt bộ lọc mua. Ví dụ DRI và BVH có điểm 82 nhưng “THEO DÕI”; DCL điểm 82 nhưng “TRÁNH”.

### 2.2 Khoảng cách giữa code và yêu cầu

| Khu vực hiện có | Phát hiện từ code | Hướng xử lý |
| --- | --- | --- |
| `src/api.js` | `BOARD_SYMBOLS = 500`; lấy scan trước rồi mới lấy bảng điện; comment cũ nhắc 200 mã/20 mã mỗi trang nhưng code dùng 500/50 | Bỏ trần cố định và phụ thuộc scan; sửa comment theo hợp đồng mới |
| `backend/market.py` | Bảng giá độc lập scan ở backend; cache trang 60 giây, listing 6 giờ; khóa đang bao quanh cả gọi provider | Giữ độc lập đến frontend; tách thu thập quote khỏi vòng tải của từng trình duyệt khi mở rộng |
| `src/market.js` | `liveNum(null)` có thể thành 0; `normalizeLiveBoard` luôn gán `mode: 'live'`; registry chỉ đưa instrument chưa từng gặp vào snapshot mới | Bảo toàn null, metadata nguồn và danh mục đầy đủ mỗi snapshot; kiểm tra lần refresh thứ hai |
| `PriceBoard.jsx` / `PriceBoardTable.jsx` | Đã có ba mức mua/bán, giá phiên, thống kê, nước ngoài; một số nhóm bị tắt mặc định | Mặc định mở đầy đủ; xử lý chiều ngang/mobile và hiệu năng |
| `backend/quant_service.py` | Đã tạo cone, histogram, drawdown, regime từ report; có JSON biểu đồ | Tái sử dụng adapter, bổ sung factor và decision metrics |
| `src/api.js::getJob` | Chỉ đưa ảnh đầu manifest và phần metrics/summary sang UI; không truyền đầy đủ `report.charts` | Bổ sung report adapter và workspace tương tác |
| `backend/engine.py::run_scan` | Chỉ đưa ít cột vào summary; `clean(report)` bỏ các key bắt đầu `_`, gồm paths và state history | Tạo visual payload trước khi clean và lưu cùng scan; không thể dựng lại cone thật từ report đã mất paths |
| `backend/engine.py::_quant_with_frames` | Job một mã chạy pipeline riêng, có `score_comparable = False` | Giữ tách biệt điểm scan và điểm job một mã; không dùng điểm này thay top 5 toàn sàn |
| `TermHint.jsx` | Đã hover, focus, click ghim, render KaTeX; chưa render ví dụ và ngưỡng; glossary có nội dung tham chiếu | Nâng cấp thành thẻ kiến thức có đủ năm phần, khớp phương pháp thực |
| `StatEngine.returns()` | `win_rate_pct` xuất từ tỷ lệ ngày tăng; `metric_scope = DAILY_PRICE_RETURNS_NOT_TRADES` | Đổi nhãn hiển thị thành “Tỷ lệ phiên tăng (%)”; chỉ dùng “Win rate giao dịch” với dữ liệu backtest giao dịch |
| Lịch chạy | `scheduler.py` mặc định PRE_OPEN 07:00 và POST_CLOSE 16:20; scan UI ghi 2 giờ, adapter ghi 720 phút | API công bố lịch thật; không suy rằng repo đang chạy 2 giờ/lần. Nếu VPS có scheduler khác cần đối chiếu khi triển khai |

`AGENTS.md` hiện mô tả bootstrap Vnstock. PR tài liệu không cần cài môi trường, xin API key hoặc thay cấu hình VPS. Các PR code tương lai cần đọc lại hướng dẫn và baseline integrity tại đúng commit triển khai.

## 3. Các quyết định đề xuất để review

| Quyết định | Mặc định đề xuất | Lý do / lựa chọn khác |
| --- | --- | --- |
| “5 mã tốt nhất” nghĩa gì? | “5 mã nổi bật theo mô hình”: ưu tiên BUY_NOW đạt gate, sau đó WATCH/BUY_SETUP; mỗi mã giữ nhãn hành động thật | Nếu gọi cả 5 là “khuyến nghị mua” sẽ sai khi không có setup mua. Có thể chọn chế độ chỉ BUY_NOW và chấp nhận dưới 5 dòng |
| “5 mã xấu nhất” nghĩa gì? | “5 mã cần thận trọng”: ưu tiên AVOID, sau đó điểm thấp nhất trong dữ liệu hợp lệ | Là đánh giá trong tập được phân tích; không kết luận doanh nghiệp kém hoặc khuyến nghị bán khống |
| Có bắt buộc luôn đủ 5 mỗi khối? | Đủ 5 khi tập hợp lệ cho phép; thiếu thì hiển thị số thật và lý do | Không lấy mã lỗi phân tích hoặc trùng giữa hai khối để lấp chỗ |
| Chỉ hiện 10 mã có phải premium? | Hiện là lựa chọn UX | Muốn hạn chế quyền đọc phải làm ở API; ẩn hàng ở frontend không ngăn tải toàn bộ dữ liệu |
| Visual chính | JSON chart tương tác; ảnh PNG cho xuất/chia sẻ ở giai đoạn sau | Ảnh duy nhất khó đọc trên mobile và không giải thích điểm đang hover |
| Radar | Factor bars/matrix mặc định; radar tùy chọn | So sánh chiều dài rõ hơn hình diện tích; factor chỉ giải thích, không thay Quant Score |
| “Bảng điện đầy đủ” | Tất cả cổ phiếu HOSE/HNX/UPCoM theo listing provider; toàn bộ nhóm cột hiện có bật mặc định | ETF, chứng quyền, trái phiếu/phái sinh là scope khác nếu provider/listing không hỗ trợ; cần yêu cầu riêng |
| Tần suất giá | Theo khả năng nguồn, công bố rõ; bản đầu có thể là polling có độ trễ | Không gắn LIVE chỉ vì request vừa thành công |
| Theme | Giữ cam–đen–xanh hiện tại; chart dùng màu có nghĩa thống nhất | Không dùng cam thương hiệu để thay màu tham chiếu/trần/sàn vốn có ngữ nghĩa |

Các mặc định này giúp viết code nhất quán, nhưng là đề xuất sản phẩm để cùng phản biện, chưa phải quyết định đã được người dùng phê duyệt.

## 4. Luồng trải nghiệm đích

1. Người dùng vào Bảng điện: thấy toàn danh mục và các nhóm cột đầy đủ, chỉ báo độ phủ/nguồn/thời điểm.
2. Vào Quét toàn sàn: nút “Kích hoạt kết quả” mở snapshot đã công bố; GET không tạo job mới.
3. Thấy hai khối 5 mã, thời điểm phân tích, tổng số mã đủ điều kiện xếp hạng và những mã thiếu dữ liệu được đếm riêng.
4. Trong mỗi hàng kết quả scan, đặt nút **“Chạy Quant” ngay cạnh tên mã**. Bấm nút mở workspace đúng mã và bắt đầu job phân tích chi tiết; click tên mã thông thường chỉ mở chart/thông tin.
5. Trên bảng điện, bấm tên mã mở popup có chart và thông tin cổ phiếu. **Cạnh chart, trong chính popup đó, có nút “Chạy Quant”**. Người dùng xem chart trước và bấm nút khi muốn chạy phân tích chi tiết.
6. Hai nút cùng dùng một hành động chạy Quant và cùng hiển thị kết quả trong workspace của mã đó: tiến độ, báo cáo, visual, điều kiện giao dịch và rủi ro. Popup từ bảng điện không tự chạy Quant chỉ vì được mở.
7. Khi cần chạy lại, dùng “Phân tích lại” có trạng thái job; kết quả job không âm thầm ghi đè phân tích toàn sàn.

### 4.1 Hai điểm đặt nút đã được người dùng chỉ định

| Điểm vào | Vị trí nút | Khi bấm | Nơi xem kết quả |
| --- | --- | --- | --- |
| Kết quả quét toàn sàn: cả khối nổi bật và thận trọng | Cùng ô tên mã, ngay cạnh ticker | Mở popup/workspace mã và khởi động phân tích Quant chi tiết | Khu vực Quant trong chính workspace mã |
| Popup cổ phiếu mở từ bảng điện | Panel thông tin/Quant cạnh chart trên desktop | Giữ popup/chart, khởi động phân tích Quant cho mã đang mở | Panel Quant hoặc tab báo cáo trong cùng popup |

Trên mobile panel xếp dưới chart để đọc được, nhưng nút vẫn thuộc popup cổ phiếu; không đưa người dùng sang trang khác chỉ để bắt đầu chạy.

Hai vị trí là hai điểm vào của cùng tính năng, không phải hai chế độ/mô hình tính toán khác nhau. Nút mở kết quả toàn sàn đọc batch đã công bố; nút Chạy Quant từng mã là thao tác khởi động job chi tiết. Hai tác vụ giữ tên và trạng thái riêng.

Hướng nối code: `ScanPage` truyền callback mã về `App` để mở `StockModal` với ý định chạy Quant một lần; `StockModal`/`ChartWorkspace` cung cấp nút chạy bên cạnh chart gọi cùng controller/job service (`startQuant`). API backend hiện có `POST /api/v1/quant/jobs`; không tạo endpoint chạy khác chỉ vì có hai nút.

Yêu cầu trạng thái: chưa chạy → “Chạy Quant”; queued/running → tiến độ và nút disabled; succeeded → kết quả + “Phân tích lại”; failed → lý do + “Thử lại”. Đồng bộ theo owner/session và symbol: bấm nhanh hai lần hoặc từ hai điểm vào khi một job đang chạy phải gắn vào job hiện có, không enqueue hai job. Frontend controller dùng chung; kiểm tra tính idempotent/in-flight dedup ở backend, không chỉ khóa nút trong một component.

Mở từ scan giữ `reference_run_id` để truy vết batch đầu vào. Điểm scan và điểm job một mã phải giữ nhãn scope riêng. Với mã trên bảng điện chưa đủ snapshot/OHLCV để backend hiện tại chạy job, vẫn có nút và giải thích điều kiện chưa đáp ứng; cần quyết định adapter dữ liệu trong PR code, không giả vờ đã chạy thành công hoặc giấu mã khỏi bảng điện.

Khi có giá mới trong lúc mở báo cáo, hiển thị “Giá hiện tại” cạnh “Giá tại phân tích”; không di chuyển cone hoặc entry theo giá mới mà không có model run mới.

## 5. Phân tích từng mã: thiết kế visual và dữ liệu

### 5.1 Bố cục

Desktop: popup cổ phiếu có chart chính và panel thông tin/Quant cạnh chart, với nút “Chạy Quant” rõ ràng. Sau khi có kết quả: header mã/doanh nghiệp/sàn + thời điểm; hàng KPI; lưới visual hai cột; kế hoạch giao dịch và nhận định bên dưới hoặc trong tab báo cáo cùng workspace. Giữ chart truy cập được và nút mở toàn màn hình ở workspace hiện tại.

Mobile: một cột, chart rộng ngang màn hình, không co cả dashboard 16:9 thành ảnh nhỏ. Font nội dung 14–16px; số liệu chính 20–28px; mức giá không chồng lên legend. Các kích thước là mục tiêu thiết kế cần QA.

| Khối | Nội dung | Dữ liệu bắt buộc | Trạng thái thiếu |
| --- | --- | --- | --- |
| Decision header | Quant Score, hành động, thời gian nắm giữ, 2–3 reason codes | `rec`, `action`, run/model version | Không bịa score/hành động |
| Giá và cone | OHLCV, vùng P10–P90, P25–P75, P50, mốc entry/SL/TP | History, quantile paths, levels, horizon | Có lịch sử thì vẫn vẽ lịch sử; ghi rõ cone chưa có |
| Phân phối lợi nhuận | Histogram cuối horizon, trung vị, VaR/CVaR, xác suất lỗ | Histogram và terminal metrics | Không thay bằng đường chuẩn tự dựng |
| HMM | Giá theo ngày và nền trạng thái; xác suất hiện tại | State history có ngày khớp giá | Không nhân bản state hiện tại thành lịch sử |
| Hồ sơ rủi ro | Drawdown tài sản, annual vol, beta, historical VaR/CVaR | Chuỗi drawdown và stats; benchmark khi có | Nêu cửa sổ, tần suất, metric scope |
| Factor diagnostics | Trend, Momentum, Dòng tiền, Relative Strength, Risk Quality, Forecast | Key factor, giá trị chuẩn hóa, trọng số/coverage | Thiếu factor thì `—`, không dịch nhãn sang factor khác |
| Forecast audit | Directional forecast, MC median, agreement, coverage, support, active models | Các đầu ra khác nhau của `fcast` | Không dùng agreement như xác suất thắng |
| Trade payoff | Entry, SL, TP1/TP2, upside/downside %, R:R, chi phí, net forecast | Levels, costs; calibration nếu tính EV | Không hiển thị EV nếu thiếu calibrated probability phù hợp |

### 5.2 Nâng cấp so với file Python

- Giữ nội dung mô hình nhưng đổi từ tờ ảnh đặc sang giao diện có phóng to, crosshair, legend bật/tắt và giải thích tại điểm dữ liệu.
- Tooltip chart gồm ngày/phiên, đơn vị, giá trị và ý nghĩa band. P10–P90 là khoảng quantile điểm theo từng thời điểm, không phải bảo đảm toàn bộ đường giá nằm trong band với xác suất 80%.
- Cone không tự gọi API sinh thêm paths. Tính quantiles và histogram trong worker từ chính report vừa hoàn thành.
- Tách `ensemble_ret_pct` định hướng khỏi trung vị/mean Monte Carlo. Repo hiện mô tả GARCH–MC dùng cho distribution và settlement risk; không gán lại thành “mô hình dự báo hướng” trong UI.
- Tách VaR lịch sử theo ngày và VaR Monte Carlo tại cuối horizon; không đặt chung một nhãn “VaR 95%” thiếu kỳ đo.
- Drawdown của cổ phiếu không được gọi là drawdown của chiến lược backtest.
- Factor normalization có `normalization_version`, `available_inputs`, `coverage`. Không áp lại factor weights của visual để thay AdaptiveScorer. Các mức low/high trong file mẫu là scale của cách trình bày, không phải chuẩn phổ quát.
- File đính kèm gọi `terminal_research_layout` nhưng không cung cấp module đó. Repo đã có fallback riêng. Tái sử dụng/nâng cấp bản repo; không chép đè toàn bộ file đính kèm làm mất fallback hoặc gây lỗi import.
- Khi không có report/OHLCV, không gọi fallback `generate_quant_visuals` có khả năng tự fetch và chạy pipeline. API xem kết quả phải thuần đọc.

### 5.3 Hợp đồng dữ liệu đề xuất

Thêm `presentation` có version vào `detail_json` của snapshot scan và report job. Endpoint chi tiết hiện có có thể trả thêm field tương thích; dùng endpoint theo run cố định cho luồng mới.

```json
{
  "schema_version": 2,
  "run_id": "<published-run-id>",
  "symbol": "<symbol>",
  "model_version": "<model-version>",
  "data_as_of": "<ISO-date>",
  "published_at": "<ISO-timestamp>",
  "price_unit": "VND",
  "return_unit": "percentage_points",
  "horizon_sessions": 10,
  "score_scope": "cross_sectional_scan",
  "presentation": {
    "charts": {},
    "factors": [],
    "decision_metrics": {},
    "availability": {}
  }
}
```

Đây là schema minh họa, không phải response đang tồn tại. `horizon_sessions` phải lấy từ report, không cố định 10 trong code.

Hướng xử lý worker: report + OHLCV → tạo presentation → sanitize JSON → lưu summary/detail/visual cùng run → publish atomically. `clean(report)` hiện bỏ dữ liệu private nên thứ tự này bắt buộc để giữ cone và lịch sử regime.

Không gửi raw Monte Carlo matrix đến browser. Histogram có bins giới hạn (đề xuất 30–80, chọn theo dữ liệu); summary xác suất/quantiles tính trên toàn bộ paths hợp lệ, không tính trên mẫu chart đã giảm kích thước. Ghi `simulation_count`, `path_time_convention`, phương pháp và window.

Snapshot cũ không có presentation: đọc dữ liệu còn tồn tại, đánh dấu từng visual thiếu; lần scan mới mới cung cấp đủ. Không âm thầm chạy lại mô hình để backfill khi mở trang.

## 6. Quét toàn sàn: hai bảng 5 mã và cột như Excel

### 6.1 Quy tắc xếp hạng đề xuất

**Tập hợp lệ:** cùng một published run, unique symbol, `analysis_status == completed`, score hữu hạn 0–100, dữ liệu không FAIL. Mã phân tích lỗi, thiếu score hoặc dữ liệu FAIL đi vào thống kê excluded; không coi là cổ phiếu “xấu”.

**Khối nổi bật:** nhóm 1 = BUY_NOW với gate pass; nhóm 2 = BUY_SETUP/WATCH; nhóm 3 = HOLD nếu còn cần bù danh sách. Mỗi nhóm sắp score giảm dần, sau đó net forecast giảm dần nếu cùng horizon và dữ liệu hợp lệ, cuối cùng symbol tăng dần. AVOID không được đi vào khối cơ hội. Net forecast thiếu đứng sau giá trị hợp lệ khi tie; không đổi null thành 0.

**Khối thận trọng:** ưu tiên AVOID với lý do từ pipeline, sau đó các mã còn lại có score thấp nhất; tie theo net forecast tăng dần khi so sánh hợp lệ, cuối cùng symbol. Loại các mã đã chọn ở khối nổi bật. Nếu có dưới 10 mã hoặc ít mã ở một nhóm, không lấp bằng mã lỗi/trùng; hiển thị dưới 5 và lý do.

Chỉ `BUY_ACTIONS = {'BUY_NOW'}` đang được core coi là đạt gate mua. BUY_SETUP/WATCH được trình bày như cơ hội theo dõi, không đổi gate thành pass. Mọi ràng buộc thanh khoản, chi phí, timing và T-lock giữ theo core; không tạo ngưỡng mới trong frontend.

**Ca thực tế phải xử lý:** với tab mẫu 67 mã, banner ghi “Hiện chưa có mã đạt điều kiện mua”; top nổi bật có thể là WATCH, còn khối thận trọng là AVOID. Điểm 82 đi cùng TRÁNH phải nhìn thấy lý do, không bị trang trí thành tín hiệu mua.

Xếp hạng theo toàn universe của run, trước khi hiển thị. Tìm kiếm/sàn trên trang này chỉ lọc 10 dòng được chọn và phải ghi rõ phạm vi; không đổi thành top 5 mỗi sàn một cách ngầm định. Tìm mã bất kỳ để phân tích đi qua ô tìm toàn danh mục của workspace/bảng điện.

### 6.2 Các cột mặc định

Desktop mỗi khối có: Mã, Sàn, Hành động, Điểm, Forecast ròng/horizon, Sharpe, MaxDD lịch sử, Tỷ lệ phiên tăng, Agreement, Điều kiện/lý do. Mở rộng hàng để xem entry/SL/TP, payoff và các nhóm chỉ số còn lại.

Mobile hiển thị card: mã + hành động + điểm; forecast ròng và rủi ro; một lý do chính; nút chi tiết. Toàn bộ trường bổ sung vẫn truy cập được qua mở rộng, không nhồi 50 cột lên màn hình đầu.

Nút “Tùy chọn cột” có preset Tóm tắt / Hiệu suất / Dự báo / Rủi ro–thanh khoản / Kế hoạch giao dịch. Chỉ hai khối top 5; không có nút bung toàn bộ scan trong scope này. Bảng điện tiếp tục có đủ mã và dữ liệu giá.

### 6.3 Mapping đủ 50 cột trong schema Excel phổ biến

Field API dưới đây là **tên đề xuất**. Nguồn summary core đã đối chiếu trong `summary_table()`; adapter giữ số thô, không dùng chuỗi tiếng Việt để làm logic.

| Cột Excel | Field API đề xuất | Nguồn summary / lưu ý |
| --- | --- | --- |
| Mã | `symbol` | Symbol |
| Khuyến nghị | `action` | Action / final_action; lưu raw enum và nhãn riêng |
| Đạt bộ lọc | `gate_pass` | GatePass |
| Giải thích điều kiện | `gate_reasons` | GateReasons; reason codes + diễn giải |
| Điểm | `score` | Score; score_scope/model version |
| Đánh giá | `rating` | Rating; không thay action |
| Thời gian nắm giữ | `holding_sessions` | HoldPlan để hiển thị; lấy horizon số từ report |
| Xu hướng VN-Index | `index_trend` | VNI |
| Nhóm ngành | `sector` | NhomNganh |
| Xu hướng ngành | `sector_trend` | XuHuongNganh |
| Lợi nhuận ngành 20 phiên (%) | `sector_return_20d_pct` | NganhRet20D% |
| Tương quan ngành | `sector_correlation` | TuongQuanNganh; [-1,1], không tự nhân 100 |
| Mã dẫn dắt ngành | `sector_lead_lag` | MaDanDatNganh; quan hệ lead/lag, không xác nhận nhân quả |
| Sharpe | `sharpe` | Sharpe; scope giá cổ phiếu |
| Win Rate (%) | `up_day_ratio_pct` | WinRate hiện là phiên tăng; đổi nhãn UI |
| Max DD (%) | `max_drawdown_pct` | MaxDD; historical window |
| Annual Return (%) | `annual_return_pct` | AnnRet; lịch sử năm hóa |
| HMM | `hmm_regime` | HMM |
| Volatility Regime | `volatility_regime` | VolReg |
| Dự báo | `forecast_direction` | Forecast |
| Lợi nhuận dự báo (%) | `ensemble_return_pct` | EnsRet%; horizon cụ thể |
| Đồng thuận (%) | `agreement_pct` | Agreement |
| Coverage mô hình (%) | `model_coverage_pct` | Coverage% |
| Directional support (%) | `directional_support_pct` | AlphaSupport% |
| Số mô hình hoạt động | `active_model_count` | ActiveModels; integer |
| Meta-label P(win) (%) | `meta_trust_pct` | MetaTrust%; tên core là meta_trust_probability, cần kiểm chứng target và calibration trước khi gọi P(win) |
| Hurst | `hurst` | Hurst |
| Hurst regime | `hurst_regime` | HurstRegime |
| LightGBM rank (%) | `lightgbm_rank_pct` | LightGBMRank%; percentile trong tập xếp hạng |
| LightGBM alpha (%) | `lightgbm_alpha_pct` | LightGBMAlpha%; kiểm tra target/horizon/benchmark |
| Lợi nhuận gộp (%) | `gross_forecast_pct` | GrossFc% |
| Chi phí (%) | `roundtrip_cost_pct` | CostRT%; mô hình chi phí, không phải phí đã khớp |
| Lợi nhuận ròng (%) | `net_forecast_pct` | NetFc% |
| Biến động mô phỏng | `mc_volatility_source` | MCVol thực là nhãn mô hình/nguồn, không phải con số volatility |
| Sụt giảm khi chờ T+2 (%) | `lock_drawdown_pct` | LockDD%; kèm lock_sessions thật |
| Xác suất lỗ trên 3% (%) | `probability_loss_gt_3pct` | PLoss3%; phải mang horizon và sample count |
| Chất lượng dữ liệu | `data_quality_status` | DQStatus |
| Điểm dữ liệu | `data_quality_score` | DQScore |
| Cảnh báo dữ liệu | `data_quality_flags` | DQFlags; array reason codes |
| Thanh khoản | `liquidity_tier` | LiqTier |
| GTGD TB 20 phiên (tỷ) | `adv20_value_vnd` | Nguồn gốc liquidity.adv20_value_vnd; ADV20_Bn = /1e9 |
| Sức chứa tối đa (cổ phiếu) | `capacity_shares` | CapacityShares |
| Khoảng trống giá 95% (%) | `gap_abs_p95_pct` | GapP95% |
| Entry | `entry_vnd` | Entry; Excel đã chia 1000 |
| SL | `stop_loss_vnd` | SL; Excel đã chia 1000 |
| TP1 | `take_profit_1_vnd` | TP1; Excel đã chia 1000 |
| TP2 | `take_profit_2_vnd` | TP; theo fallback tp_optimal/tp2 của core, không tự chọn lại |
| Model Agreement (%) | `trade_model_agreement_pct` | ModelAgreement%; kiểm tra có trùng Agreement hay không, không hiện hai cột như hai bằng chứng độc lập |
| RiskPctNAV | `risk_pct_nav` | RiskPctNAV; cần NAV/position context, thiếu thì null |
| Nhận xét chi tiết | `commentary` | Analysis; giữ text nguồn, gắn glossary an toàn |

Không import Excel lịch sử làm nguồn production. Dùng workbook để xác định trường và đối chiếu adapter. Tab schema cũ thiếu tám trường mới phải giữ null; không gán số mặc định để trông đầy đủ.

Các trường bổ sung ngoài workbook: Sortino, annual volatility, historical VaR/CVaR, R:R gross/net, EV_R, calibrated trade P(win), simulation_count, reason codes, run/model/source version và metric_scope. Chỉ hiển thị khi đúng nguồn và đủ điều kiện.

### 6.4 Quy ước đơn vị và công thức payoff

- API giữ giá VND, volume cổ phiếu, value VND. UI bảng điện/Excel-style có thể hiển thị nghìn đồng nhưng chỉ chuyển ở formatter một lần.
- `5.31` ở field `_pct` nghĩa là 5.31%, còn xác suất nguồn 0.531 phải qua adapter để thành 53.1%. Có unit/scale trong schema, không đoán theo độ lớn.
- Null/NaN/Infinity/chuỗi trống → null và UI `—`; 0 hợp lệ vẫn hiển thị 0. Không dùng `Number(null)` để tạo chỉ số 0.
- `Net forecast (%) = Gross forecast (%) − Roundtrip cost (%)`, khi cả ba cùng horizon, cùng quy ước và khớp mô hình hiện dùng.
- `Upside TP (%) = 100 × (TP / Entry − 1)`; `Downside SL (%) = 100 × (SL / Entry − 1)`.
- Long setup hợp lệ để tính gross R:R: `SL < Entry < TP`; `R:R = (TP − Entry)/(Entry − SL)`; mẫu số ≤0 thì null và lý do invalid levels.
- TP1 và TP2 có R:R riêng; net R:R lấy từ core hoặc định nghĩa chi phí đã review, không trộn chi phí % với chênh giá VND.
- Ví dụ minh họa: Entry 100, SL 95, TP 110 → upside +10%, downside −5%, gross R:R 2. Nếu gross forecast 6% và chi phí 0.6% thì net forecast 5.4%; không thay forecast bằng khoảng cách TP.
- `P(TP trước SL)` dùng first-passage trên paths, mẫu số gồm mọi path hợp lệ; path không chạm barrier nào không tính là thắng. Khi chỉ có nến OHLC, hai barrier cùng bị chạm trong một nến cần quy tắc xử lý ambiguity; không tự suy thứ tự.

## 7. Thẻ kiến thức cho thuật ngữ quant

### 7.1 Cấu trúc bắt buộc

Mỗi term gồm tên Việt/Anh; lý thuyết ngắn; công thức và biến; ví dụ số; điều kiện/ngưỡng; cách dùng; giới hạn; nguồn/phương pháp/version. Giới hạn và nguồn hỗ trợ năm phần người dùng yêu cầu, không thay thế ví dụ hoặc điều kiện.

Mở nhanh hiển thị đủ nội dung thiết yếu trong thẻ 360–440px có scroll. Nội dung dài mở drawer “Xem đầy đủ” sau click/chạm; không nhồi giáo trình vào tooltip.

```js
{
  id: 'sharpe',
  labelVi: 'Sharpe',
  theory: '...',
  formulaLatex: '...',
  variables: [],
  example: { inputs: {}, steps: [], result: '...' },
  conditions: [],
  thresholds: { kind: 'pipeline_config', rules: [], version: '...' },
  usage: '...', limitations: '...', references: [],
  methodId: '...', metricScope: '...', definitionStatus: 'verified'
}
```

`thresholds.kind` có thể là mathematical / descriptive_reference / pipeline_config / none. Không có ngưỡng phổ quát thì ghi thẳng “Không có ngưỡng chung”; không tạo mức tốt/xấu giả để đủ trường.

### 7.2 Bộ thuật ngữ P0 và yêu cầu nội dung

| Nhóm | Thuật ngữ | Điểm phải giải thích đúng |
| --- | --- | --- |
| Hiệu suất | Sharpe, Sortino, Annual Return, MaxDD, Tỷ lệ phiên tăng | Cửa sổ, tần suất, risk-free/MAR, năm hóa, metric scope |
| Tail risk | VaR, CVaR, skewness, kurtosis, P(loss > 3%) | Sign convention, daily vs horizon, Pearson vs excess kurtosis, giả định |
| Forecast | Monte Carlo, ensemble, agreement, coverage, directional support | Simulation count không phải số chiến lược thử; đồng thuận không phải xác suất thắng |
| Regime | HMM, GARCH, volatility regime, Hurst | Xác suất trạng thái không phải xác suất giá tăng; persistence không khẳng định xu hướng |
| Factor | CMF, RSI, trend ER, relative strength, beta, LightGBM rank/alpha | Flow proxy và price momentum khác nhau; rank không phải % lợi nhuận |
| Trade | Entry, SL, TP1/TP2, R:R, cost, net forecast, T-lock, capacity, RiskPctNAV | Điều kiện hợp lệ, khả năng thực thi, NAV context |
| Validation | PSR, DSR, calibrated trade P(win), meta-label trust | Phải đủ dữ liệu/target/calibration; không tự tạo giá trị production khi chỉ có glossary |

Ví dụ nội dung Sharpe: excess return mỗi ngày trung bình 0.05%, độ lệch chuẩn 1% → Sharpe theo ngày 0.05; năm hóa theo 252 phiên cho khoảng 0.79 dưới giả định dùng hệ số căn thời gian. “>1” có thể là mốc mô tả tham khảo, không phải gate mua. Số ngày, phụ thuộc chuỗi và thử nhiều cấu hình làm thay đổi cách đánh giá.

Ví dụ nội dung MaxDD: giá 100 → 120 → 90 → 110; drawdown sâu nhất là 90/120 − 1 = −25%. Thông số thuộc đường giá này, không phải mức lỗ tối đa chắc chắn trong tương lai.

Ví dụ nội dung Agreement: các mô hình cùng chiều có thể cùng sai; công thức/weights thật phải lấy từ `AgreementEngine`, không tự hiển thị công thức đếm 3/4 nếu core dùng cơ chế khác. Mốc 60% trong visual mẫu không tự trở thành config gate.

PSR/DSR chỉ có phần học ở P0 nếu backend chưa xuất đủ đầu vào. DSR liên quan selection bias khi thử nhiều chiến lược và phân phối lợi suất; không dùng số đường Monte Carlo làm số thử nghiệm chiến lược.

### 7.3 Tương tác và accessibility

- Hover khoảng 250ms hoặc keyboard focus mở; di chuyển con trỏ từ term vào thẻ vẫn đọc được.
- Escape đóng thẻ trước, không đóng StockModal cha; đóng trả focus về trigger khi mở bằng click.
- Thẻ hover không chứa control focusable dùng tooltip; thẻ ghim có link/button/tab phải dùng semantics popover/non-modal dialog phù hợp. Không gán role tooltip cho cửa sổ tương tác dài.
- Chạm trên mobile mở drawer; có đóng rõ ràng, không phụ thuộc hover.
- Portal tránh bị cắt bởi overflow bảng; reposition khi resize/scroll, không chạy ra khỏi viewport.
- Không tạo button lồng trong sort button hoặc link mã. Cần tách trigger giải thích và trigger sort.
- Render text thường; KaTeX `trust: false`; term id ổn định, alias rõ, không replace HTML/commentary bằng regex nguy hiểm.
- Ví dụ phải ghi “minh họa”; số của mã đang xem chỉ đi vào mục “Giá trị hiện tại”, không trộn thành ví dụ giả.

## 8. Bảng điện đầy đủ

### 8.1 Phạm vi hiển thị

Mặc định: toàn bộ danh mục cổ phiếu nguồn hỗ trợ; giá TC/trần/sàn; dư mua 3 mức; khớp lệnh giá/KL/% thay đổi; dư bán 3 mức; tổng KL/GTGD/mở/cao/thấp; nước ngoài mua/bán/room. Điểm Quant là cột bổ sung và có thể `—`.

Không giới hạn listing theo scan, scan gate, top 10 hoặc `BOARD_SYMBOLS`. Mã chưa phân tích vẫn xuất hiện. Provider thiếu quote thì hàng vẫn tồn tại với null và trạng thái, không tự tạo giá để giống “thật”.

Các nhóm cột bật mặc định cả desktop và mobile; mobile dùng scroll ngang, sticky mã/header, nút fullscreen. Người dùng có thể lưu preset thu gọn sau đó. Toàn bộ danh mục được truy cập liên tục; không cần render mọi hàng vào DOM cùng lúc.

### 8.2 Kiến trúc và tải dữ liệu

1. API listing trả symbol/name/exchange/sector/status độc lập scan, có version/updated_at.
2. API quote trả total/loaded/available/missing, source timestamp nếu provider có, fetched_at riêng, latency/delay disclosure và source mode.
3. Frontend tải listing trước, quote tăng dần hoặc đọc một cached snapshot; scan enrichment là best-effort, lỗi scan không làm bảng giá biến thành demo.
4. Bỏ 500; phân trang theo total thật, kiểm soát batch/concurrency theo rate limit đã đo. Không tải quote cho tất cả mã từ provider trên mỗi client polling.
5. Giai đoạn đầu có thể dùng backend cached pages; khi đo thấy latency/rate limit không đáp ứng, chuyển collector background tạo board snapshot rồi web chỉ đọc cache. Không cam kết thời gian thực bằng thay đổi frontend.
6. Collector kiểm soát một lần fetch cho cùng page/key; timeout và partial failure theo batch; không giữ khóa toàn cục xuyên mọi network call.
7. Refresh giữ hàng/giá gần nhất khi batch lỗi, ghi timestamp/stale theo hàng hoặc batch; không dùng timestamp trang mới nhất đại diện cho tất cả các trang.
8. Virtualization giữ các hàng ngoài viewport trong data model; search/sort/filter trên toàn danh mục đã tải, hiển thị tiến độ khi còn partial. Keyboard navigation và screen reader cần QA riêng.
9. Map instrument theo symbol O(1); trả đủ metadata trong mỗi snapshot, sửa lỗi mất registry metadata ở refresh thứ hai.

### 8.3 Tính trung thực của bảng giá

- `source_timestamp` khác `fetched_at`: request vừa chạy không chứng minh quote vừa khớp.
- Không biết độ trễ → nhãn “Snapshot từ nguồn · độ trễ chưa công bố”, không “LIVE”. Có nguồn được xác nhận live thì mới dùng nhãn đó.
- TC/trần/sàn lấy từ provider; không suy từ giới hạn biên độ chung. Biên độ, bước giá, lịch và instrument type có thể khác nhau.
- ATO/ATC giữ typed quote; không ép string thành 0. Khối lượng lần khớp không lấy từ total accumulated volume.
- GTGD không suy bằng giá cuối × tổng KL. Field unavailable để `—`.
- Giá 0/âm bất hợp lệ là null; khối lượng 0 hợp lệ giữ 0.
- Thị trường đóng cửa là trạng thái riêng, không mặc định “mất kết nối” do quote không thay đổi.
- Bảng thống kê tăng/giảm/GTGD phải kèm coverage: giá hợp lệ N/tổng M. Chưa tải đủ không gọi là độ rộng toàn thị trường.

## 9. Hợp đồng API và tính nhất quán snapshot

Các route mới dưới đây là **đề xuất**, chưa tồn tại trong repo:

| Route | Trách nhiệm |
| --- | --- |
| `GET /api/v1/scans/latest/highlights` | Resolve latest một lần và trả top/bottom + run_id + counts + rule_version |
| `GET /api/v1/scans/{run_id}/results/{symbol}` | Chi tiết theo run cố định, kèm presentation |
| `GET /api/v1/scans/{run_id}/results/{symbol}/ohlcv` | OHLCV cùng run với report |
| `GET /api/v1/market/instruments` | Toàn listing độc lập scan |
| Endpoint market overview hiện có hoặc snapshot mới | Quote + metadata độ phủ/trễ; giữ client cũ tương thích |

Highlights response gồm `opportunities`, `cautions`, `universe_count`, `analyzed_count`, `eligible_count`, `excluded_counts`, `buy_now_count`, `selection_rule_version`, horizon/method scope và publication schedule. Mỗi mã có reason codes và dữ liệu cho cột mặc định; chỉ tải chi tiết khi mở.

Phân trang qua `/latest` hiện có có nguy cơ trộn hai run nếu latest đổi giữa các request. Với top 10, API chọn từ cùng run ở server. Với report/ohlcv, pin run_id; nếu run bị xóa trả “Snapshot không còn”, không thay bằng latest khác. Lưu chính sách retention đủ cho tab đang mở và deep link.

Publication schedule lấy từ scheduler/config thật; bao gồm `schedule_kind`, `timezone`, lịch/expected next publication khi tính được. Stale của quote, scan và model report có tiêu chí riêng; kiểm thử cả ngày nghỉ và ngoài giờ.

## 10. Kế hoạch PR và file dự kiến thay đổi

| PR | Phạm vi | File trọng tâm | Điều kiện xong |
| --- | --- | --- | --- |
| PR-0 — tài liệu | Plan này, quyết định còn mở | `docs/QUANTIK_PRODUCT_UPGRADE_PLAN.md` | Reviewer hiểu scope; không đổi runtime |
| PR-1 — adapter + snapshot | 50 fields, null/units, presentation lúc scan, metadata, pin run | `backend/engine.py`, `quant_service.py`, `server.py`, `store.py` nếu cần, `src/api.js`, `scan.js` | Contract tests và snapshot cũ tương thích |
| PR-2 — top 5 / bottom 5 | Endpoint highlights, selection rule và scan UI | Backend selection module mới; `ScanPage.jsx`, styles | Hai khối đúng nhãn, cùng run, không chạy model khi kích hoạt |
| PR-3 — visual workspace | Hai điểm đặt nút chạy cùng controller/job; chart JSON, factor matrix, decision/payoff/audit | `App.jsx`, `ScanPage.jsx`, `StockModal.jsx`, `QuantPanel.jsx`, `AnalysisReport.jsx`, `ChartWorkspace.jsx`, visual components mới | Nút cạnh mã scan và nút cạnh chart popup chạy đúng mã; job không trùng; visual và empty state đúng |
| PR-4 — glossary | Schema nội dung và term interaction | `content/metrics.json`, `glossary.js`, `TermHint.jsx`, `AnnotatedText.jsx`, styles | Ví dụ/ngưỡng đầy đủ, keyboard/mobile đúng |
| PR-5 — bảng điện | Full listing, đủ cột, independence, loading/cache/virtualization | `market.py`, `server.py`, `api.js`, `market.js`, `useMarket.js`, `PriceBoard*.jsx` | Không cắt 500; lần refresh thứ hai đúng; scan lỗi không chặn quote |

PR-2/3 cần PR-1; PR-4 có thể làm độc lập; PR-5 có thể làm độc lập nhưng chốt listing/quote contract trước. Có thể ưu tiên PR-5 trước visual nếu mục tiêu là sửa thiếu mã ngay.

Không chỉnh quant core/scoring chỉ để phục vụ UI. Nếu phải sửa core, tách PR riêng với lý do, baseline diff và kiểm tra `test_quant_core_integrity.py`; không cập nhật hash để che thay đổi không chủ đích.

### 10.1 Checklist implementation

- [ ] Chốt định nghĩa top/bottom, thiếu 5 dòng, phạm vi cổ phiếu và lịch công bố.
- [ ] Kiểm tra provider listing/quote coverage, latency, rate limit và field timestamps trong môi trường triển khai.
- [ ] Viết adapters từ report/raw summary; không parse chuỗi Excel cho logic production.
- [ ] Tạo và lưu visual aggregates trước `clean`; có schema_version và availability.
- [ ] Pin run_id cho highlights/detail/OHLCV; test latest đổi giữa lượt đọc.
- [ ] Mở cột scan/preset theo mapping; tooltip đúng unit và scope.
- [ ] Dựng workspace chart responsive, factor names cố định, empty states.
- [ ] Đặt “Chạy Quant” cạnh tên mã ở cả hai khối scan và trong panel cạnh chart của popup bảng điện; dùng cùng action/controller.
- [ ] Mở popup từ bảng điện chỉ tải chart/thông tin; bấm Quant từ scan khởi động đúng một job và mở vùng báo cáo trong workspace đó.
- [ ] Bổ sung glossary examples/conditions, phân biệt reference với pipeline config.
- [ ] Tách bảng điện khỏi scan; bỏ trần 500; partial load và stale rõ.
- [ ] Kiểm tra hiệu năng và accessibility với danh mục đủ lớn.
- [ ] Chạy checks cần thiết, review diff, mở PR code về `kappyphm/quantik-react:main`.
- [ ] Sau merge/deploy, smoke test trên môi trường thật và rollback nếu lỗi nguồn/độ phủ.

### 10.2 Ước lượng phục vụ lập kế hoạch

Đề xuất khoảng 12–20 ngày công kỹ thuật + review cho toàn scope nếu dữ liệu provider sẵn có và không đổi core; không phải cam kết thời gian. PR-1/2 khoảng 3–5, visual 3–5, glossary 2–3, bảng điện 3–5, tích hợp/QA 1–2 ngày công. Collector mới hoặc feed thiếu trường có thể làm tăng đáng kể.

Với nguồn lực người dùng dưới 15 giờ/tuần, nên review từng PR nhỏ; không yêu cầu bạn tự xây lại cả quant pipeline để chốt giao diện. Đo và chốt nguồn dữ liệu bảng điện là đường găng lớn nhất.

## 11. Tiêu chí nghiệm thu và kiểm thử có ý nghĩa

| Nhóm | Ca kiểm thử bắt buộc | Kết quả mong đợi |
| --- | --- | --- |
| Xếp hạng | Nhiều mã, tie score, net null, đủ 10 eligible | Tối đa 5/5; ổn định; không trùng; cùng run |
| Điểm vào Quant | Nút cạnh mã scan và nút trong popup chart | Cùng action/service, đúng symbol; mở từ scan chạy một lần, mở chart thông thường không tự chạy |
| Job trùng | Double click và bấm hai điểm vào khi đang chạy | Cùng owner/symbol gắn vào job đang chạy, không tạo hai job |
| Khuyến nghị | Điểm 82 + AVOID; tất cả mã gate fail | Không hiện BUY; banner chưa có setup mua; giữ lý do |
| Dữ liệu lỗi | Failed analysis, DQ FAIL, score null/NaN | Excluded đúng; không lọt bottom vì dữ liệu thiếu |
| Ít dữ liệu | 0, 3, 7 mã; tất cả AVOID | Dòng thật, empty state từng khối, không bịa cơ hội |
| Đơn vị | Entry raw 16,700 VND vs Excel 16.7; pct 5.31 vs prob 0.531 | UI đúng nghìn đồng/%; không chia/nhân hai lần |
| Adapter | Null và 0, qty zero, missing TP, SL >= Entry | Null giữ null; 0 giữ 0; R:R invalid không tính |
| Visual | Paths biết trước, histogram/quantile/first-passage | Aggregate khớp fixture độc lập; không gửi raw paths |
| Regime | Missing dates/state, ngày lệch, factor thiếu ở giữa | Không kéo state giả; không đổi nhãn factor |
| Scope | Daily price WinRate vs trade WinRate; job score khác scan | Nhãn và score_scope đúng, top không thay bởi job |
| Snapshot | latest đổi khi đọc metadata/detail/OHLCV | Pin run không trộn; báo run expired đúng |
| Bảng điện | Listing >500, mã không có scan, provider thiếu quote | Tất cả listing có hàng, coverage thật, không demo ngầm |
| Refresh | Lượt hai; một batch lỗi; scan endpoint 404 | Tên/sàn/ngành vẫn đủ; snapshot gần nhất giữ; quote không bị scan chặn |
| Tooltip | Hover sang card, focus, Escape, mobile, trong modal | Đọc được; không out-of-viewport; focus và đóng đúng |
| Hiệu năng | Fixture 1,500–2,000 mã, sort/filter/scroll/refresh | Không đứng UI; đánh giá profiler trước chọn virtualization |

Mục tiêu hiệu năng cần đo trên baseline xác định: highlights JSON đề xuất <100KB gzip; detail visual <250KB gzip; mở dữ liệu cache p95 <1 giây; tương tác lọc/sort p95 <200ms trên máy desktop QA. Nếu không đạt phải ghi kết quả và điều chỉnh thiết kế; đây không phải số đo hiện tại. Không đặt SLA feed real-time trước khi đo nguồn.

Checks cho PR code theo CI hiện có: `pnpm install --frozen-lockfile`, `pnpm build`, backend `python -m unittest discover -s tests -v`; kiểm tra compose/build khi sửa deployment. Thêm tests chọn lọc cho business rules, contract và regressions nêu trên. PR tài liệu chỉ kiểm tra nội dung, mapping, links và diff; không tuyên bố đã chạy test runtime.

Visual QA ở 360px, 768px, 1440px: đọc được legend/công thức; toàn bộ cột truy cập được; contrast đúng; không tràn ngoài container; chart loading/error/missing không che toàn workspace.

## 12. Brainstorm và phản biện sản phẩm

| Ý tưởng | Giá trị | Phản biện | Đề xuất |
| --- | --- | --- | --- |
| “Vì sao điểm cao mà vẫn TRÁNH?” | Giải quyết mâu thuẫn người dùng thấy ngay | Giải thích dài có thể làm bảng rối | P0: 2 reason codes + drawer timeline gate |
| “Điều gì làm tín hiệu mất hiệu lực?” | Biến kết quả thành điều kiện dễ kiểm tra | Không được suy điều kiện tùy ý từ narrative | P0 khi core có threshold/reason có cấu trúc; thiếu thì ghi chưa có |
| Card “Tình trạng mua hôm nay” | Nêu số BUY_NOW trong universe, không ép đủ 5 lệnh mua | Số 0 có thể bị coi là sản phẩm không hoạt động | Giải thích 0 là kết quả mô hình, kèm WATCH rõ nhãn |
| Lịch sử thay đổi đánh giá | Hiểu mã mới vào/rời top, điểm/action thay đổi | Snapshot và model version khác nhau không so trực tiếp được | P1: so hai run tương thích, lưu reason và phương pháp |
| So sánh hai mã | Giúp chọn giữa hai cơ hội | Khác ngành/horizon dễ tạo so sánh sai | P1: khóa window/horizon, kèm benchmark |
| Risk–Return Map | Xem vị trí các mã trên mặt phẳng rủi ro/lợi nhuận | Có thể vô tình bung toàn scan trái scope 10 mã | P1: chỉ 10 mã đang hiển thị, hoặc role được quyền riêng |
| Sector flow heatmap | Phù hợp trụ cột “dòng tiền đi đâu” của QuanTik | GTGD/cổ phiếu tăng không chứng minh tiền ròng vào ngành | P1: gọi đúng activity/relative flow proxy và công bố coverage |
| Watchlist cảnh báo đổi action | Tăng nhu cầu quay lại sản phẩm | Alert liên tục/khác model version dễ gây nhiễu | P1: alert khi published run đổi action, giải thích lý do; không bật gửi tự động trong plan |
| Xuất research brief | Dùng cho trao đổi với khách hàng môi giới | Screenshot thiếu timestamp dễ trở thành thông tin cũ | P1: có run/model/date/units, export từ dữ liệu đang xem |
| “Confidence 90%” nổi bật | Có vẻ dễ bán | Trộn trust/agreement/coverage/P(win) làm hiểu sai | Không làm; dùng nhãn riêng và tooltip |
| Cá nhân hóa theo NAV | RiskPctNAV/position phù hợp người dùng | Chưa có NAV, holdings, mục tiêu hoặc constraints | P2 opt-in; không hiện sizing cá nhân giả ở P0 |
| AI chat phân tích mã | Hỏi thêm thuận tiện | Có thể bịa số hoặc diễn giải sai core; phí và độ trễ | P2 sau schema + evidence; câu trả lời phải đọc snapshot và dẫn trường |
| Premium scanner | Có thể tạo doanh thu | Nút kích hoạt/ẩn DOM không bảo vệ dữ liệu, định giá khi chưa biết nhu cầu dễ sai | Phỏng vấn người dùng trước; entitlement ở API khi thật sự triển khai |

### 12.1 Câu hỏi để chúng ta phản biện tiếp

1. Khi không có mã đạt gate mua, bạn muốn top nổi bật là WATCH hay chỉ hiện thông báo chưa có cơ hội mua? Mặc định đề xuất là WATCH có nhãn rõ.
2. “Xấu nhất” muốn hiểu theo score thấp, forecast ròng thấp hay hành động AVOID? Mặc định đề xuất ưu tiên AVOID rồi score; tránh tạo một score rủi ro mới chưa kiểm định.
3. Với người dùng đầu tiên, ai là persona chính: người mới, trader ngắn hạn hay khách môi giới cần đọc báo cáo? Quyết định này đổi độ sâu màn hình đầu, không đổi dữ liệu.
4. Bảng điện cần toàn cổ phiếu hay thêm ETF/chứng quyền? Đừng gọi “toàn bộ sản phẩm sàn” khi listing chỉ có cổ phiếu.
5. VPS đang có nguồn/lịch chạy nào ngoài scheduler trong repo? Có output artifacts hoặc report JSON đã cache để tái sử dụng không?
6. Tính năng trả phí sau này bán sự tiết kiệm thời gian, chiều sâu nghiên cứu, theo dõi rủi ro hay toàn bộ scan? Chọn giá trị trước khi tạo paywall.

### 12.2 Cách kiểm chứng ý tưởng

Thử với 5–8 người thuộc một persona, giao tác vụ: chọn một mã để xem; giải thích vì sao hệ thống WATCH/TRÁNH; đọc net forecast và downside; phân biệt agreement với xác suất thắng; tìm một mã ngoài top 10 trên bảng điện.

Theo dõi task completion, thời gian tìm lý do, sai cách hiểu chỉ số, click từ highlights sang detail và tỷ lệ quay lại. Tooltip mở nhiều chưa chứng minh hữu ích; phải kiểm tra người dùng hiểu đúng. Không dùng click khuyến nghị làm bằng chứng mô hình có alpha. Alpha cần đánh giá OOS/backtest/live riêng với phí, leakage và multiple testing.

## 13. Rủi ro triển khai và rollback

- Giữ publish nguyên tử: run mới chưa đủ hợp đồng tối thiểu thì không thay pointer latest; failed batch có status/count rõ.
- Bật theo feature flags đề xuất `highlights_v2`, `research_visuals_v2`, `term_cards_v2`, `full_market_board`; các flags là thiết kế tương lai, chưa có sẵn.
- Adapter đọc cả schema cũ và mới. Không xóa lịch sử hoặc đổi schema phá client trong cùng PR UI.
- Theo dõi lỗi API, quote coverage, duration collector, missing chart count, highlight eligible/excluded count và nguyên nhân gate.
- Rollback UI flag khi có regression; giữ snapshot/report cũ nguyên vẹn. Nếu schema có migration, cần forward-compatible đọc/ghi trước rollout.
- Không deploy/merge tự động trong lượt plan. Khi triển khai code, PR phải ghi rõ gì đã test local/CI, gì còn phụ thuộc nguồn thật và smoke test cần làm sau deploy.

## 14. Nguồn kỹ thuật và trạng thái xác minh

Nguồn code: [repo tại commit khảo sát](https://github.com/kappyphm/quantik-react/tree/66f0e38903dc42b2017d66032994b1660bafd932). Các kết luận về field/scoring/adapter ở trên dựa vào file đã đọc, chưa chạy pipeline hoặc kiểm thử VPS.

Nguồn gốc chỉ số/xếp hạng: `backend/quant_engine/quant.py` — `summary_table`, `_simplify_user_summary`, `StatEngine.returns`, `BUY_ACTIONS`, `AgreementEngine`. Nguồn presentation: `backend/quant_service.py::present_report`, `backend/engine.py`. UI/transport: `src/api.js`, `scan.js`, `market.js`, `hooks/useMarket.js`, `components/ScanPage.jsx`, `PriceBoard*.jsx`, `QuantPanel.jsx`, `AnalysisReport.jsx`, `TermHint.jsx`, `content/glossary.js`. Lịch/giá: `backend/scheduler.py`, `market.py`, `server.py`.

Tham khảo phương pháp và accessibility đã tra cứu ngày 07/10/2026:

- Bailey, D.H. and López de Prado, M. (2014), *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality*. [Bản tác giả](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf). Dùng cho nội dung PSR/DSR; không bổ sung giá trị chỉ số vào sản phẩm nếu thiếu dữ liệu.
- W3C WAI, *ARIA Authoring Practices Guide — Tooltip Pattern*. [Hướng dẫn gốc](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/). Phân biệt tooltip thông tin với hover chứa thành phần tương tác; xử lý Escape/focus.

**Trạng thái hoàn thành của tài liệu:** đã đọc repo và hai file mẫu; đối chiếu đủ 50 cột schema phổ biến; nêu khoảng cách, phương án dữ liệu/UX, PR sequencing, nghiệm thu và phản biện. Tính năng runtime vẫn là backlog chờ bước triển khai sau review plan.
