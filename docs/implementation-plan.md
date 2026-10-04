# Kế hoạch hoàn thiện website QuanTik

**Phiên bản:** 1.1 — 04/10/2026  
**Repository:** [kwuangyong/QuanTik-website](https://github.com/kwuangyong/QuanTik-website)  
**Bản giao diện nền:** [Pull request #1](https://github.com/kwuangyong/QuanTik-website/pull/1)  
**Trạng thái tài liệu:** Kế hoạch tham chiếu gốc. Tiến độ triển khai ngày 04/10/2026 được cập nhật riêng trong [implementation-status.md](implementation-status.md); các checklist bên dưới giữ nguyên để đối chiếu yêu cầu.

## 1. Mục tiêu và phạm vi

Hoàn thiện QuanTik thành một không gian phân tích cổ phiếu Việt Nam, kết hợp trải nghiệm bảng điện quen thuộc với công cụ định lượng và phần giải thích dễ tiếp cận.

| Hạng mục | Kết quả cần đạt |
| --- | --- |
| Biểu đồ TradingView | Có thanh công cụ, bộ chọn chỉ báo, công cụ vẽ và các khung phút/giờ/ngày mà nguồn dữ liệu hỗ trợ |
| Panel phân tích | Mở bên cạnh biểu đồ; kéo thay đổi kích thước, thu gọn, mở lại; không làm mất kết quả đang xem |
| Giải thích thuật ngữ | Rê chuột hoặc focus để đọc ý nghĩa và công thức; bấm để mở thẻ có biến số, cách dùng, ví dụ và giới hạn |
| Bảng điện truyền thống | Có nhóm cột giá trần/sàn/tham chiếu, dư mua, khớp lệnh, dư bán, thanh khoản và các trường bổ sung theo khả năng nguồn dữ liệu |
| Nhóm ngành | Lọc cổ phiếu theo ngành, xem tổng quan ngành và danh sách mã; nguồn phân ngành và cách tính được công bố rõ |

**Quy ước thiết kế:** “Thanh kéo thả” được triển khai thành panel trượt có tay nắm thay đổi kích thước. Sắp xếp lại vị trí các thẻ bằng kéo thả là phần mở rộng, không bắt buộc cho bản đầu tiên.

**Phân biệt hai mốc hoàn thành:**

- **Mốc giao diện:** Các thao tác chạy được với fixture/mẫu được gắn nhãn rõ.
- **Mốc dữ liệu thật:** Các chức năng đã nối nguồn dữ liệu và pipeline, được kiểm tra trên dữ liệu thật. Đạt mốc giao diện chưa có nghĩa là đạt mốc dữ liệu thật.

## 2. Hiện trạng và các điểm phải sửa

| Thành phần hiện tại | Điểm còn thiếu | Cách xử lý |
| --- | --- | --- |
| `TVWidget.jsx` dùng Advanced Chart widget | Khung mặc định ngày; biểu đồ compact ẩn toolbar; chỉ đặt sẵn SMA/RSI/MACD | Tách chế độ xem nhanh và workspace đầy đủ; mở toolbar; kiểm tra selector chỉ báo và khung thời gian |
| `tvSymbol(sym)` luôn ghép `HOSE:` | Chưa nhận biết sàn và mã định danh của nhà cung cấp | Dùng hồ sơ mã gồm `exchange`, `tvSymbol`, khả năng hỗ trợ biểu đồ |
| `StockModal.jsx` chia chart/Quant thành tab | Không xem biểu đồ và kết quả Quant cạnh nhau | Tạo workspace chung và panel phân tích có thể co giãn |
| `QuantPanel.jsx` trả summary và ảnh | Thuật ngữ chưa có nội dung giải thích; ảnh không có cấu trúc tương tác | Bổ sung glossary và kết quả có cấu trúc; giữ ảnh như bản tổng quan phụ |
| `PriceBoard.jsx` là bảng giá đơn giản | Chưa có 3 mức dư mua/dư bán và phân ngành | Giữ bảng hiện có làm chế độ tổng quan; thêm chế độ bảng điện chi tiết |
| `demo.js`, `backend/adapters.py` | Dữ liệu mẫu; `name`, `sector` backend còn trống | Chuẩn hóa danh mục mã và hợp đồng dữ liệu trước khi nối nguồn thật |
| VN30 hiện lọc bằng cách loại một mã mẫu | Không phải danh sách thành phần thực | Dùng danh sách có nguồn, ngày hiệu lực; giữ nhãn mẫu đến khi tích hợp |
| Backend cache/job hiện tại | Chưa tách chắc chắn theo phiên bản dữ liệu và mô hình | Thiết kế cache cho summary lẫn ảnh; không dùng việc có ảnh để suy ra đủ kết quả |

Bản giao diện nền đã build và có kiểm tra thao tác bằng DOM. Kiểm tra trực quan bằng trình duyệt thật vẫn là công việc bắt buộc trong kế hoạch này.

## 3. Biểu đồ: đầy đủ công cụ trong phạm vi tích hợp

### 3.1. Quyết định công nghệ

Tiếp tục dùng **Advanced Chart widget** cho giai đoạn đầu để tận dụng các chỉ báo và công cụ vẽ có sẵn. Tài liệu widget mô tả bộ chỉ báo và công cụ vẽ, nhưng đó là tập chức năng của widget, không phải toàn bộ Supercharts trên tradingview.com. [TV1]

| Phương án | Phù hợp khi | Điều kiện và giới hạn |
| --- | --- | --- |
| Advanced Chart widget hiện có | Cần nhanh một chart nhiều công cụ với dữ liệu TradingView | Tùy chỉnh có giới hạn; không nối dữ liệu QuanTik vào widget [TV2] |
| Advanced Charts library | Cần quản lý chart bằng API, nối OHLCV riêng và tích hợp chỉ báo tùy biến | Cần kiểm tra quyền truy cập/điều kiện sử dụng và xây datafeed riêng [TV2][TV3][TV4] |
| Lightweight Charts | Cần chart do QuanTik kiểm soát với footprint nhỏ | Không có bộ chỉ báo dựng sẵn; phải tự tính và dựng phần cần dùng [TV2] |

**Điểm quyết định:** Nếu widget không cung cấp được chức năng bắt buộc sau khi thử nghiệm, lập hạng mục chuyển sang library. Không thêm các thuộc tính của Charting Library vào cấu hình widget rồi mặc định chúng sẽ hoạt động.

### 3.2. Các công việc cụ thể

- [ ] Tạo `ChartWorkspace` dùng chung từ bảng điện, bảng ngành và trang Quant.
- [ ] Cho workspace đầy đủ hiển thị toolbar trên và thanh công cụ vẽ bên cạnh. Chế độ compact chỉ dành cho preview.
- [ ] Bật bộ chọn chỉ báo; người dùng thêm, sửa tham số và xóa các chỉ báo có sẵn.
- [ ] Preset ban đầu chỉ bật một số ít để biểu đồ dễ đọc: Volume, SMA và RSI; MACD và các chỉ báo khác để người dùng chọn.
- [ ] Kiểm tra SMA/EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX và các chỉ báo dòng tiền được widget thực tế cung cấp. VWAP cần kiểm tra riêng theo mã và dữ liệu intraday.
- [ ] Hỗ trợ nến, thanh, đường và các kiểu chart được widget cung cấp; zoom, pan, công cụ vẽ và chế độ toàn màn hình.
- [ ] Phân biệt **độ dài một nến** với **khoảng lịch sử đang xem**. Ví dụ nến 5 phút khác khoảng lịch sử 1 tháng.
- [ ] Kiểm tra các khung mục tiêu bên dưới trên từng nguồn/sàn; không hiển thị khung không có dữ liệu như thể hoạt động được.
- [ ] Lưu mã đang xem và tùy chọn mà QuanTik thực sự kiểm soát. Việc lưu các thay đổi bên trong widget chỉ được cam kết sau khi xác nhận cơ chế widget hỗ trợ.

| Nhóm | Khung mục tiêu | Mã resolution khi dùng Charting Library* |
| --- | --- | --- |
| Phút | 1, 3, 5, 15, 30 phút | `1`, `3`, `5`, `15`, `30` |
| Giờ | 1, 2, 4 giờ | `60`, `120`, `240` |
| Ngày/tuần/tháng | 1 ngày, 1 tuần, 1 tháng | `1D`, `1W`, `1M` |

\* Bảng này là quy ước cho library/datafeed, không phải lời khẳng định rằng widget hiện tại cho cấu hình toàn bộ khung này. Khung thực tế phụ thuộc sản phẩm và dữ liệu. [TV3]

### 3.3. Dữ liệu và khả năng hỗ trợ

Tạo bảng kiểm cho mỗi mã gồm: sàn, mã TradingView đã xác minh, có/không dữ liệu intraday, khung thử thành công, độ trễ được nguồn công bố và ngày kiểm tra. Không giả định mã thuộc HNX/UPCoM có thể được ghép prefix rồi chạy ngay.

Nếu chuyển sang library, xây datafeed với tìm kiếm/resolve mã, lịch sử OHLCV, đăng ký/hủy cập nhật. Khai báo `supported_resolutions`, session và timezone theo dữ liệu thực tế. Khi tổng hợp nến phút thành giờ/ngày, phải xử lý giờ giao dịch, nghỉ giữa phiên và ranh giới phiên; không tự tạo nến giả để lấp khoảng nghỉ. [TV3]

**Nghiệm thu:** Thêm/xóa/sửa ít nhất ba chỉ báo; đổi phút → giờ → ngày trên mã có dữ liệu; đổi mã/sàn không giữ chart cũ; lỗi/thiếu dữ liệu có trạng thái rõ; mở panel không cắt toolbar hoặc làm méo chart.

## 4. Panel phân tích: kéo kích thước, ẩn và hiện

### 4.1. Bố cục và tương tác

Desktop: biểu đồ nằm bên trái, panel phân tích bên phải. Header panel gồm tên mã, thời điểm dữ liệu, trạng thái job và nút thu gọn. Có tay nắm ở mép trái để kéo rộng/hẹp.

- Mặc định rộng khoảng 380 px; giới hạn gợi ý 320–600 px, đồng thời giữ vùng chart tối thiểu phù hợp với màn hình.
- Panel đóng thành một tab “Phân tích” dễ nhìn; bấm tab để mở lại.
- Thu gọn panel không hủy job, không xóa kết quả và không remount chart.
- Đổi mã phải chuyển sang đúng kết quả của mã mới; không hiển thị số liệu mã cũ dưới tên mã mới.
- Ghi nhớ trạng thái mở/đóng và chiều rộng hợp lệ trên thiết bị; reset về mặc định khi giá trị lưu lỗi.
- Tablet: chuyển sang drawer nếu hai vùng không đủ rộng. Mobile: dùng panel phía dưới với tay nắm và nút mở/đóng rõ, không phụ thuộc hoàn toàn vào thao tác vuốt.
- Nếu triển khai dưới dạng overlay, quản lý focus và khóa nền đúng; panel cạnh chart trên desktop không cần khóa toàn trang.

### 4.2. Cách thực hiện

Tạo `AnalysisDrawer.jsx`, `ResizeHandle.jsx` và hook quản lý kích thước. Dùng Pointer Events với `setPointerCapture` để tiếp tục nhận thao tác khi con trỏ đi qua vùng iframe TradingView. Giới hạn resize bằng requestAnimationFrame nếu cần; không cập nhật widget config mỗi lần kéo.

Tay nắm có `role="separator"`, tên truy cập được, chiều rộng hiện tại và hỗ trợ phím mũi tên/Home/End. Có nút thu gọn độc lập để sử dụng bằng bàn phím. Tôn trọng `prefers-reduced-motion`.

Đưa trạng thái job lên workspace hoặc hook có vòng đời độc lập với việc panel đang hiện hay ẩn. Theo dõi job bằng `(symbol, modules, dataVersion, modelVersion)`; bỏ qua phản hồi lỗi thời khi người dùng đổi mã/chạy lại.

**Nghiệm thu:** Kéo 20 lần liên tục không tạo thêm iframe hoặc job; thu gọn rồi mở lại giữ kết quả; đổi mã trong khi job chạy không trộn dữ liệu; hoạt động bằng chuột, cảm ứng và bàn phím.

## 5. Thuật ngữ: tooltip ngắn và thẻ chi tiết

### 5.1. Hai lớp giải thích

| Hành động | Nội dung và hành vi |
| --- | --- |
| Rê chuột khoảng 250 ms hoặc focus bàn phím | Tooltip: tên tiếng Việt, tên gốc, ý nghĩa 1–2 câu, công thức render bằng LaTeX và đơn vị nếu có |
| Bấm/chạm thuật ngữ hoặc Enter/Space | Thẻ nhỏ có công thức, biến số, tham số đang dùng, cách đọc kết quả, ví dụ và giới hạn |
| Escape hoặc bấm ngoài thẻ | Đóng thẻ chi tiết và trả focus về thuật ngữ |
| Di chuyển từ nhãn sang tooltip | Không biến mất ngay; đủ thời gian để đọc và thao tác khi cần |

Không dùng riêng thuộc tính HTML `title`. Dùng một component chung `TermHint` để có giao diện, nội dung và hành vi thống nhất. Thẻ chi tiết trên mobile có thể thành bottom sheet.

### 5.2. Nội dung chuẩn hóa

Tạo `src/content/glossary.js` với cấu trúc:

```js
{
  id: 'atr',
  vi: 'Biên độ thực trung bình',
  en: 'Average True Range',
  short: 'Đo mức dao động giá, cùng đơn vị với giá cổ phiếu.',
  formulaLatex: '...',
  variables: [],
  interpretation: '...',
  example: '...',
  limitations: ['...'],
  references: [],
  version: '1.0'
}
```

Thông tin từ pipeline như chu kỳ, phương pháp smoothing, benchmark, số đường mô phỏng và kỳ dự báo được truyền vào thẻ khi hiển thị. Không để glossary nói SMA 20 trong khi mô hình thực tế dùng SMA 50.

| Nhóm | Thuật ngữ ưu tiên |
| --- | --- |
| Giá và giao dịch | Tham chiếu, trần, sàn, khớp lệnh, dư mua/dư bán, thanh khoản |
| Chỉ báo | SMA, EMA, RSI, MACD, ATR, Bollinger Bands, CMF |
| Mô hình | HMM, GARCH, Monte Carlo, beta, sức mạnh tương đối |
| Rủi ro/đánh giá | Sharpe, PSR, DSR, MaxDD, VaR, CVaR, skewness, kurtosis |
| Kết quả QuanTik | Điểm Quant, điểm vào, cắt lỗ, mục tiêu giá, tỷ lệ lợi nhuận/rủi ro |

### 5.3. Mẫu độ sâu nội dung

**SMA:**

$$\mathrm{SMA}_{n,t}=\frac{1}{n}\sum_{i=0}^{n-1}P_{t-i}$$

Giải thích `P` là giá được sử dụng, `n` là số kỳ. “20 kỳ” là 20 nến trên khung đang xét; không luôn là 20 ngày. Dùng để mô tả xu hướng, có độ trễ.

**ATR:**

$$TR_t=\max(H_t-L_t,\ |H_t-C_{t-1}|,\ |L_t-C_{t-1}|)$$

Với smoothing Wilder sau giá trị khởi tạo:

$$ATR_t=\frac{(n-1)ATR_{t-1}+TR_t}{n}$$

ATR đo mức dao động, không dự báo hướng tăng/giảm. Nêu rõ chu kỳ và cách khởi tạo trong implementation.

**Max drawdown:**

$$DD_t=\frac{V_t}{\max_{s\le t}V_s}-1,\qquad MaxDD=\min_t DD_t$$

Trong quy ước trên, MaxDD là số âm; nếu giao diện hiển thị độ lớn dương, nhãn/công thức phải giải thích điều đó. `V` phải là equity curve đúng loại, không tùy tiện dùng giá cổ phiếu thay cho giá trị chiến lược.

Với Sharpe/PSR/DSR, thẻ phải ghi tần suất lợi suất, cách annualize, số quan sát và giả định. Điểm Quant không được mô tả là xác suất sinh lời nếu mô hình chưa được hiệu chỉnh như xác suất. Các ví dụ nội dung cần được đối chiếu công thức trong pipeline trước khi đưa lên sản phẩm.

### 5.4. Giới hạn tương tác quan trọng

Tooltip áp dụng cho nhãn, bảng và thẻ do QuanTik quản lý. Không chèn tooltip vào DOM bên trong iframe TradingView khác origin. Với thuật ngữ trên toolbar TradingView, cung cấp “Tra cứu chỉ báo” ở ngoài iframe. Ảnh kết quả từ backend cũng không tự cung cấp hover theo thuật ngữ; cần JSON có cấu trúc và các nhãn HTML tương ứng.

**Nghiệm thu:** Không cần bấm để đọc ý nghĩa và công thức trên desktop; bấm mở đúng thẻ; công thức render đúng; tooltip không tràn màn hình, không bị bảng cuộn/modal cắt; có thể đọc bằng bàn phím và chạm.

## 6. Bảng điện theo trải nghiệm sàn chứng khoán

### 6.1. Cấu trúc sản phẩm

Giữ **Tổng quan** cho bảng dễ đọc hiện tại; thêm **Bảng điện** cho dữ liệu chi tiết. Hai chế độ dùng cùng dữ liệu chuẩn hóa, cùng bộ lọc và cùng danh sách theo dõi.

Bộ lọc dự kiến: sàn HOSE/HNX/UPCoM, nhóm chỉ số, ngành, danh sách cá nhân, mã/tên doanh nghiệp. Không thêm giao dịch/đặt lệnh trong phạm vi này.

### 6.2. Nhóm cột

| Nhóm | Các trường |
| --- | --- |
| Nhận diện | Ngôi sao, mã, sàn; tên doanh nghiệp qua tooltip/chi tiết |
| Giá phiên | Tham chiếu, trần, sàn |
| Dư mua | Giá và khối lượng mức 3, 2, 1; thứ tự hiển thị ghi rõ |
| Khớp lệnh | Giá khớp gần nhất, KL lần khớp gần nhất nếu có, thay đổi tuyệt đối và % |
| Dư bán | Giá và khối lượng mức 1, 2, 3 |
| Thống kê | Tổng KL, tổng giá trị, mở cửa, cao nhất, thấp nhất |
| Nước ngoài | KL mua/bán, room còn lại nếu nhà cung cấp có |
| QuanTik | Điểm Quant và nút mở phân tích |

Không nhầm **KL lần khớp gần nhất**, **KL tích lũy cả phiên** và **KL đang chờ tại một mức giá**. Không suy ra giá trị giao dịch bằng giá cuối × tổng KL khi cần số thực.

### 6.3. Quy tắc hiển thị

- Header hai hàng, có nhóm “Dư mua / Khớp lệnh / Dư bán”; sticky header và sticky mã cổ phiếu.
- Cuộn ngang trong bảng; tùy chọn hiện/ẩn nhóm cột và chế độ mật độ.
- Màu so với giá tham chiếu: tăng xanh, giảm đỏ, tham chiếu vàng, trần tím, sàn xanh lam. Kèm dấu `+/-` hoặc nhãn, không dựa hoàn toàn vào màu.
- Chuẩn hóa backend về VND/cổ phiếu; frontend chọn hiển thị nghìn đồng/nghìn CP và ghi đơn vị rõ.
- `null` hiển thị “—”; số 0 hợp lệ vẫn là 0. Đặc thù ATO/ATC dùng loại quote riêng, không ép chuỗi thành số.
- Flash ngắn ở ô đổi giá/khối lượng; không nhấp nháy cả bảng.
- Khi feed ngắt, giữ snapshot cuối cùng nhưng gắn “Mất kết nối / Dữ liệu cũ” và thời điểm cập nhật; không gọi đó là giá trực tiếp.
- Mobile có preset rút gọn và tùy chọn xem đầy đủ; không buộc mọi người kéo ngang qua toàn bộ cột.

### 6.4. Nguồn dữ liệu

Xác minh nhà cung cấp có snapshot, 3 mức giá/khối lượng, intraday, nhóm mã và luồng cập nhật nào. API key và kết nối nhà cung cấp nằm ở backend. Widget TradingView là nguồn chart độc lập, không phải nguồn dữ liệu bảng điện của QuanTik. [TV2]

Giai đoạn giao diện dùng fixture cố định; giai đoạn thật dùng adapter nhà cung cấp. Polling chỉ dùng nếu phù hợp quota và độ trễ của nguồn. Khi có streaming, backend duy trì kết nối tập trung và gửi các thay đổi qua WebSocket/SSE; tránh mỗi người dùng mở một kết nối riêng tới nhà cung cấp.

## 7. Nhóm ngành và tổng quan ngành

### 7.1. Danh mục phân ngành

Tạo danh mục có `sectorId`, tên ngành, mã thuộc ngành, hệ phân loại, nguồn và ngày cập nhật. Ưu tiên dùng nhất quán một hệ phân loại từ nhà cung cấp; không trộn các cấp phân ngành. Mã chưa phân loại được đưa vào “Chưa xác định”.

Các nhóm ban đầu có thể gồm ngân hàng, chứng khoán, bảo hiểm, bất động sản, xây dựng/vật liệu, công nghệ, bán lẻ, thực phẩm/đồ uống, năng lượng và vận tải/logistics; danh sách cuối phải khớp nguồn phân loại đã chọn.

### 7.2. Màn hình và cách tính

- Tab “Nhóm ngành” có bảng tổng quan: số mã, tăng/giảm/đứng giá, thay đổi nhóm, tổng GTGD và tỷ trọng GTGD.
- Bấm ngành để lọc bảng điện và xem các mã thành phần, mã đóng góp lớn, thanh khoản và điểm Quant có sẵn.
- Phạm vi tính luôn hiện rõ: toàn nguồn hay chỉ các mã đang tải; bộ lọc sàn nào đang áp dụng.
- Mặc định có thể dùng trung bình đều lợi suất các mã có giá hợp lệ:

$$r_{\text{ngành},t}=\frac{1}{N_t}\sum_{i=1}^{N_t}\left(\frac{P_{i,t}}{P_{i,ref}}-1\right)$$

Đặt nhãn **“Thay đổi trung bình nhóm”**; không gọi đây là chỉ số ngành chính thức. Nếu dùng trọng số vốn hóa, cần vốn hóa cùng thời điểm, chính sách trọng số và lịch sử thành phần.

- Tổng GTGD chỉ cộng dữ liệu đúng đơn vị và cùng phiên; báo độ bao phủ nếu thiếu.
- Điểm Quant ngành nếu có là tổng hợp điểm các mã, phải nêu quy tắc/trọng số và số mã có điểm. Điểm ngành không mặc nhiên là tín hiệu mua.
- Heatmap là phần mở rộng sau bảng ngành: diện tích theo GTGD hoặc vốn hóa, màu theo thay đổi; luôn có chú giải.

**Nghiệm thu:** Lọc ngành trả đúng thành phần; “Chưa xác định” không biến mất; đổi sàn làm thay đổi phạm vi tổng hợp; công thức được kiểm tra bằng fixture; không gắn nhãn chỉ số chính thức cho trung bình tự tính.

## 8. Hợp đồng dữ liệu và API

### 8.1. Dữ liệu chuẩn hóa

| Đối tượng | Trường tối thiểu |
| --- | --- |
| `Instrument` | `symbol`, `exchange`, `name`, `sectorId`, `tvSymbol`, `active`, nguồn và ngày cập nhật |
| `Quote` | `symbol`, giá tham chiếu/trần/sàn, giá khớp, tổng KL/GTGD, bid/ask, thống kê, timestamp |
| `MarketSnapshot` | `source`, `mode`, `asOf`, `session`, `isStale`, `sequence`, đơn vị, `quotes` |
| `AnalysisResult` | `symbol`, `asOf`, khung dữ liệu phân tích, modules, metrics, tham số, data/model version, trạng thái, mode |
| `Metric` | `id`, `value`, `unit`, `termId`, provenance, trạng thái có/thiếu dữ liệu |
| `SectorSnapshot` | `sectorId`, thành phần, phương pháp tính, phạm vi, độ bao phủ, chỉ tiêu tổng hợp |

`mode` phải đến từ server, ví dụ `demo`, `delayed`, `live`, `eod`; không lấy việc HTTP thành công làm bằng chứng dữ liệu live.

### 8.2. API dự kiến

- `GET /api/instruments` — danh mục mã, sàn, ngành và mapping chart.
- `GET /api/board?exchange=HOSE&sector=...&group=...` — snapshot có metadata.
- `GET /api/sectors` — danh mục phân ngành.
- `GET /api/sectors/summary?...` — tổng hợp ngành theo phạm vi.
- `POST /api/quant/jobs` và API trạng thái hiện có — bổ sung phiên bản dữ liệu/mô hình và kết quả có cấu trúc.
- `WS /api/market/stream` hoặc SSE — cập nhật quotes sau khi có nguồn streaming.
- API lịch sử OHLCV/datafeed — chỉ bổ sung khi chọn tích hợp library dùng dữ liệu riêng.

Thay response bảng từ array sang envelope phải sửa frontend/backend cùng đợt hoặc có adapter chuyển đổi. Sequence bị gián đoạn phải tải snapshot lại; reconnect không cộng dồn lại KL tích lũy.

**Riêng cache Quant:** Hiện backend có thể thấy ảnh cache rồi bỏ chạy module, nhưng không nạp summary đã lưu. Cần lưu/nạp cả kết quả cấu trúc và ảnh dưới cùng cache key; gồm mã, module, khung phân tích, phiên dữ liệu và phiên bản mô hình. Đổi khung chart không tự đổi khung pipeline: nếu pipeline chỉ dùng EOD, panel phải ghi rõ “Phân tích theo ngày”.

## 9. Các file và component cần thay đổi

| File/nhóm | Công việc |
| --- | --- |
| `src/App.jsx` | Điều hướng Bảng điện/Nhóm ngành, trạng thái mã đang xem và workspace |
| `src/components/TVWidget.jsx` | Chart đầy đủ, mapping mã/sàn, cấu hình có kiểm chứng và lỗi nguồn |
| `src/components/StockModal.jsx` | Chuyển thành workspace chart + panel; focus, Escape và toàn màn hình |
| `src/components/QuantPanel.jsx` | Kết quả có cấu trúc, TermHint, tham số và trạng thái job |
| `src/components/PriceBoard.jsx` | Chế độ tổng quan và tích hợp bảng điện; không nhồi cả hai bố cục vào một JSX lớn |
| `PriceBoardTable.jsx`, `SectorBoard.jsx` mới | Bảng điện grouped header và màn hình ngành |
| `AnalysisDrawer.jsx`, `ResizeHandle.jsx` mới | Thu gọn, resize và responsive |
| `TermHint.jsx`, `TermDetails.jsx`, `glossary.js` mới | Hệ giải thích thuật ngữ tập trung |
| `src/api.js`, các hook dữ liệu | Metadata nguồn, hủy request/ignore stale response, subscription và reconnect |
| `src/styles.css` | Tokens chung; CSS drawer/tooltip/table; tách theo component khi file lớn |
| `backend/adapters.py`, `backend/server.py` | Danh mục mã, quote schema, ngành, kết quả Quant và cache |
| Fixtures và tài liệu | Mẫu ổn định, dữ liệu thiếu/lỗi, đơn vị và hướng dẫn triển khai |

Có thể dùng Floating UI cho positioning tooltip/popover và KaTeX cho công thức; chỉ thêm dependency sau khi kiểm tra phiên bản và API hiện hành. Nếu bảng hàng nghìn mã gây chậm, benchmark trước khi chọn virtualization.

## 10. Thứ tự triển khai và ước lượng

| Giai đoạn | Công việc | Đầu ra | Ước lượng giờ tập trung |
| --- | --- | --- | --- |
| 0 — Xác minh | Khả năng TradingView, nguồn bảng điện, sàn/khung, schema và fixture | Ma trận hỗ trợ và hợp đồng dữ liệu | 4–8 |
| 1 — Chart | Workspace đầy đủ, toolbar, chỉ báo, mã/sàn, lỗi và resize chart | Chart được kiểm tra trên các mã đại diện | 5–9 |
| 2 — Panel và glossary | Resize/ẩn hiện, trạng thái job, tooltip/popover, nội dung ưu tiên | Phân tích tương tác có giải thích | 10–16 |
| 3 — Bảng điện và ngành | Grouped columns, bộ lọc, danh mục ngành, tổng hợp đúng phạm vi | Bảng điện/nhóm ngành trên fixture | 12–20 |
| 4 — Tích hợp và QA | Nối nguồn có sẵn, schema migration, cache, kiểm tra trình duyệt | Bản có thể review và triển khai thử | 8–14 |

Tổng sơ bộ **39–67 giờ**, với giả định đã có API dữ liệu phù hợp và không phải chuyển sang Charting Library. Đây là ước lượng công việc, không phải thời gian chờ cấp quyền hoặc mua/tích hợp nguồn mới. Việc chuyển library, xây datafeed mới hoặc chuyển toàn bộ pipeline thành JSON cần ước lượng riêng.

Nếu người dùng trực tiếp tham gia với quỹ dưới 15 giờ/tuần, chia thành khoảng 3–5 tuần công việc tập trung và ưu tiên review từng giai đoạn. Làm trên các nhánh nhỏ theo tính năng, qua pull request; chưa triển khai trong phạm vi yêu cầu viết kế hoạch này.

## 11. Kiểm thử và điều kiện hoàn thành

### Kiểm thử tự động có giá trị

- [ ] Unit: đổi đơn vị giá/KL; phân loại màu; số 0/null; lợi suất/thanh khoản ngành; quy tắc stale data.
- [ ] Contract: API board/modules/jobs/summary đúng schema; mã hoặc nguồn không hợp lệ trả lỗi có thể xử lý.
- [ ] React: resize/ẩn hiện giữ trạng thái; tooltip hover/focus; popover bấm/Escape; chuyển mã không nhận kết quả cũ.
- [ ] E2E: bảng điện → mã → chart → thêm indicator → mở panel → chạy Quant → tra thuật ngữ → trở lại bảng ngành.
- [ ] Streaming: mất mạng, reconnect, sequence gap, snapshot reset và dữ liệu khác phiên.

### Kiểm tra trình duyệt thật

- [ ] Desktop ở 1366×768 và 1920×1080; tablet; mobile khoảng 390×844.
- [ ] Light/dark; zoom 125–200%; bàn phím; reduced motion.
- [ ] Chrome/Edge và ít nhất một trình duyệt mobile đại diện.
- [ ] Indicator và timeframes thử trực tiếp, không chỉ kiểm tra config JSON.
- [ ] Tooltip/modal/drawer không bị iframe che hoặc vùng cuộn cắt.
- [ ] Không tràn ngang toàn trang; chỉ bảng điện được cuộn ngang.
- [ ] Network panel xác nhận không mount nhiều widget hoặc mở job lại khi resize/thu gọn.

**Definition of Done:** Build qua; các luồng chính được kiểm thử; mapping sàn và khung có bằng chứng; công thức/đơn vị đúng; thiếu dữ liệu không được tự bịa; chức năng mẫu/nguồn chậm/live có nhãn; review trực quan đã hoàn thành; README và changelog cập nhật.

## 12. Những quyết định cần chốt khi bắt đầu triển khai

| Quyết định | Mặc định đề xuất | Khi cần thay đổi |
| --- | --- | --- |
| Công nghệ chart | Giữ widget, thử nghiệm khả năng trước | Cần dữ liệu riêng, API chart hoặc indicator riêng bắt buộc |
| Panel phân tích | Bên phải desktop, phía dưới mobile | Người dùng muốn vùng dưới chart trên mọi thiết bị |
| Bảng điện | Cổ phiếu HOSE/HNX/UPCoM | Thêm phái sinh/chứng quyền làm hạng mục riêng |
| Phân ngành | Một hệ từ nhà cung cấp, có ngày cập nhật | Cần nhóm tùy chỉnh của QuanTik |
| Tần suất giá | Theo khả năng và quota nguồn được chọn | Có streaming hoặc yêu cầu độ trễ khác |
| Glossary | Nội dung tiếng Việt, kèm tên gốc và công thức | Thêm chế độ song ngữ sau |

Thông tin còn cần từ chủ dự án: nguồn dữ liệu hiện có, quyền truy cập bảng điện/intraday, file pipeline và schema kết quả thực. Các phần giao diện trên fixture có thể bắt đầu trước; phần dữ liệu thật phụ thuộc những thông tin này.

## 13. Tài liệu tham chiếu

Đối chiếu ngày 04/10/2026. Kiểm tra lại trước khi triển khai vì khả năng sản phẩm và điều kiện sử dụng có thể thay đổi.

- **[TV1]** [Advanced Chart widget — Technical Analysis demo](https://www.tradingview.com/widget-docs/widgets/charts/advanced-chart/demos/technical-analysis/): chỉ báo dựng sẵn, drawing tools và ví dụ cấu hình.
- **[TV2]** [TradingView — Product comparison](https://www.tradingview.com/charting-library-docs/latest/product-comparison/): phân biệt widget, Advanced Charts và Lightweight Charts; nguồn dữ liệu và giới hạn nối dữ liệu riêng.
- **[TV3]** [Advanced Charts — Datafeed API](https://www.tradingview.com/charting-library-docs/latest/connecting_data/Datafeed-API/): kết nối dữ liệu, khai báo mã/resolution và subscription.
- **[TV4]** [TradingView — Charting libraries](https://www.tradingview.com/free-charting-libraries/): so sánh thư viện và điều kiện tiếp cận sản phẩm.
- **[TV5]** [Advanced Charts — FAQ](https://www.tradingview.com/charting-library-docs/latest/resources/Frequently-Asked-Questions/): các khác biệt với tradingview.com và giới hạn tích hợp.

Các endpoint, component và bố cục trong tài liệu là thiết kế đề xuất cho QuanTik; tài liệu TradingView chỉ làm căn cứ cho khả năng và giới hạn sản phẩm của họ.


## 14. Bổ sung từ file “Chỉ số.xlsx”: hover xem công thức

**Nguồn nội dung:** File người dùng cung cấp, sheet `Weight Configuration`. Đã đọc 21 chỉ số thuộc 6 nhóm. File là nguồn tham chiếu cho danh mục và nội dung popup; chưa phải bằng chứng rằng pipeline thực tế đang tính đúng mọi chỉ số hoặc đang dùng các tham số ghi trong file.

### 14.1. Danh mục bắt buộc

| Nhóm trong Excel | Chỉ số có tooltip công thức và thẻ chi tiết |
| --- | --- |
| Performance Metrics | Annual Return, Sharpe, Sortino, Calmar, Win Rate, Max Drawdown |
| Market Statistics | HMM Regime, CMF, Volatility Regime, RSI |
| Forecasting | Ensemble Return, Confidence, Monte Carlo Volatility |
| Lock Risk | Lock Drawdown, Probability Loss >3% |
| Tail Risk | VaR, CVaR, Kurtosis |
| Trading Parameters | Kelly, Risk/Reward (TP2R–TP3R), Entry/SL Quality |

Mỗi chỉ số có một `termId` cố định. Những nơi xuất hiện cùng chỉ số — thẻ kết quả, bảng, header và phần tóm tắt — dùng chung nội dung. Các biến thể cách tính có `methodId` và phiên bản riêng; không gộp các phương pháp khác nhau thành một công thức chung.

### 14.2. Nội dung hiện ngay khi rê chuột

Tooltip mở khi rê vào **tên chỉ số, biểu tượng thông tin cạnh tên hoặc công thức hiển thị**. Không gắn hành vi mở tooltip vào toàn bộ hàng gây cản trở chọn cổ phiếu.

Tooltip gồm:

1. Tên chỉ số và tên tiếng Việt.
2. Ý nghĩa bằng một câu ngắn.
3. Công thức tính, render thành ký hiệu toán học rõ ràng.
4. Chú giải các biến chính; đơn vị hoặc horizon quan trọng.
5. Nhắc “Bấm để xem cách sử dụng và ví dụ”.

Kích thước đề xuất 320–420 px trên desktop, tự giới hạn theo viewport. Nếu công thức dài, xuống dòng hoặc dùng công thức tổng quát ngắn và ghi phương pháp; không thu nhỏ chữ đến mức khó đọc. Tooltip không chứa một bài giải thích dài hoặc ô cuộn khó dùng. Cho phép con trỏ đi vào tooltip để đọc; bấm nhãn mở thẻ chi tiết cố định. Trên mobile, chạm nhãn để xem cùng nội dung.

**Ví dụ nội dung hover cho Sharpe:**

> **Sharpe — Hiệu suất điều chỉnh theo biến động**  
> Đo lợi nhuận vượt mức tham chiếu trên mỗi đơn vị biến động lợi suất.  
> Công thức đang dùng: được chọn theo `methodId` của pipeline.  
> Nếu pipeline dùng lợi suất ngày và quy đổi năm, hiển thị công thức tương ứng cùng tần suất dữ liệu, lãi suất phi rủi ro và hệ số quy đổi.  
> Bấm để xem các biến, ví dụ và giới hạn diễn giải.

Không lấy một giá trị Sharpe mẫu trong Excel làm kết quả của cổ phiếu đang được người dùng xem.

### 14.3. Nội dung khi bấm

Thẻ chi tiết lấy các cột trong Excel làm khung biên tập:

| Cột nguồn | Mục hiển thị trong thẻ |
| --- | --- |
| Giá Trị Hiển Thị (Bản Chất Chỉ Số) | Ý nghĩa và chỉ số đang đo điều gì |
| Phương Pháp Tính Giá Trị Hiển Thị | Công thức/phương pháp đã đối chiếu pipeline |
| Giá Trị Đầu Vào | Giải thích biến và dữ liệu cần có |
| Các Hệ Số Đang Được Sử Dụng | Tham số thực tế của lần chạy; giá trị Excel chỉ là tham chiếu khi chưa nối pipeline |
| Phân Loại Trạng Thái | Hướng dẫn đọc hoặc ngưỡng cấu hình, ghi rõ phạm vi áp dụng |
| Trọng Số Thành Phần/Danh Mục | Trọng số cấu hình nếu hệ thống thực tế sử dụng; không hiểu thành xác suất |

Thêm ví dụ minh họa tách biệt với kết quả đang chạy, điều kiện không tính được, giới hạn và nguồn phương pháp. Các nhãn “Tốt/Tệ” và ngưỡng trong Excel cần được kiểm tra với mô hình và horizon; không đưa lên như quy luật đúng cho mọi cổ phiếu/chiến lược.

### 14.4. Quy trình chuẩn hóa trước khi đưa lên web

- [ ] Trích 21 dòng chỉ số thành dữ liệu nội dung có cấu trúc, giữ sheet/dòng nguồn để truy vết.
- [ ] Chuyển công thức dạng văn bản sang LaTeX; các mục mô tả thuật toán như HMM giữ phần phương pháp thay vì tự bịa một công thức duy nhất.
- [ ] Đối chiếu mỗi chỉ số với hàm tính thật, horizon, đơn vị, cách annualize và quy ước dấu.
- [ ] Thống nhất các biến thể còn ghi nhiều cách trong Excel: Confidence, Volatility Regime và phương pháp VaR.
- [ ] Với Monte Carlo Volatility, ghi rõ đo độ phân tán giá cuối kỳ hay lợi suất cuối kỳ và có annualize hay không.
- [ ] Với Probability Loss >3%, xác định 3% của giá tài sản, giá trị vị thế hay vốn tài khoản; phải khớp dữ liệu đầu vào của pipeline.
- [ ] Với Entry/SL Quality, bổ sung quy tắc tính và trọng số thật trước khi hiển thị một công thức chi tiết.
- [ ] Kiểm tra các ngoại lệ: chia cho 0, không có giao dịch, không đủ lịch sử, mẫu số âm/không hợp lệ, không có mô hình dự báo.
- [ ] Render và kiểm tra từng công thức; tránh ký tự lỗi, công thức tràn hoặc bị modal/bảng cắt.

### 14.5. Tiêu chí nghiệm thu bổ sung

- [ ] Cả 21 chỉ số đều có nội dung; mục chưa được pipeline định nghĩa rõ có thông báo minh bạch.
- [ ] Hover/focus hiện công thức mà không cần bấm.
- [ ] Bấm/chạm mở thẻ đúng chỉ số, có cách dùng và ví dụ.
- [ ] Công thức và tham số khớp `methodId` của kết quả đang xem.
- [ ] Chỉ số trong ảnh backend được trình bày lại bằng nhãn/thẻ HTML tương ứng để có hover; không chỉ để nguyên trong ảnh.
- [ ] Tooltip cũng dùng được khi panel hẹp, đang cuộn, ở chế độ tối/sáng và bằng bàn phím.

**Điều chỉnh ước lượng:** Danh mục tăng lên 21 chỉ số có công thức. Dành thêm khoảng 4–8 giờ biên tập/đối chiếu và kiểm tra render ngoài phần cơ chế tooltip chung; thời gian làm rõ công thức tùy biến phụ thuộc code pipeline được cung cấp.
