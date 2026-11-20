# MINIMATE — quản lý phiên học và lời nhắc trên PC

Bản bàn giao hiện thực quản lý phiên học, lịch nhắc việc, FAQ học tập và luồng
điều phối 7 intent trên máy tính. Mặc định dùng BamiBERT local đã tinh chỉnh;
keyword/rule vẫn có để so sánh bằng `--classifier keyword` và không cần thư viện ngoài.

Khi chạy CLI, dữ liệu thử nghiệm được lưu cục bộ tại `data/minimate.db` bằng
SQLite: các bảng phiên học hiện tại, lịch sử lệnh và lời nhắc.

## Model local và cài đặt Windows

Model được chọn: `models/hf_schedule_from_hf_v2`, tinh chỉnh tiếp từ
`nguen2929/minimate_intent_classifier`. Trọng số `model.safetensors` là
411.850.308 byte (khoảng 412 MB); toàn thư mục khoảng 413 MB, gồm tokenizer/config.
Không tải model khi chạy; thiếu file hoặc thư viện thì báo lỗi, không tự đổi sang baseline.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install torch transformers==4.57.1
.venv\Scripts\Activate.ps1
python src/main.py
python src/main.py --classifier keyword
python src/main.py --db :memory: --text "Bắt đầu học 25 phút"
```

Trên máy hiện tại, `.venv_hf_test` cũng đã có thư viện tương thích; có thể chạy
`.venv_hf_test\Scripts\python.exe -X utf8 src/main.py --db :memory:`.
Launcher ưu tiên `.venv`, rồi `.venv_hf_test`, cuối cùng Python trong PATH;
chuyển tiếp tham số, ví dụ `run_minimate.bat --classifier keyword`.

Classifier nạp tokenizer/model một lần lúc khởi động, đọc `id2label` từ config,
giữ dấu văn bản, dùng `truncation=True, max_length=32` giống `scripts/test_hf_intent.py`.
Điểm softmax không bảo đảm dự đoán đúng. Câu dài bị cắt, câu phủ định, nhiều ý
hoặc cách diễn đạt ngoài dữ liệu huấn luyện vẫn có thể nhận sai. Task Manager
kiểm tra hành động trước khi cập nhật phiên; intent có điểm cao không đủ để bắt đầu/hủy.

## Phạm vi lịch nhắc

Đã hỗ trợ tạo và liệt kê lời nhắc sắp tới. Câu “Tôi có lịch gì vào ngày mai?”
đi đến tra cứu và lọc riêng ngày mai. Không có ngày thì liệt kê các lời nhắc sắp tới.
Model nhận xóa vào `schedule_reminder`; backend tìm lời nhắc theo nội dung (không
phân biệt dấu/hoa thường), ngày và giờ nếu có. Một kết quả thì hỏi xác nhận;
nhiều kết quả thì hiển thị danh sách đánh số, yêu cầu chọn một số rồi hỏi xác nhận;
không có kết quả thì thông báo không tìm thấy. Không xóa hàng loạt.

```text
Xóa lời nhắc đi học ngày mai
2
đúng
```

`2` là số thứ tự trong danh sách vừa hiển thị, không phải ID SQLite.
`đúng`, `đúng rồi`, `đồng ý`, `ừ`, `ok` xác nhận khi có yêu cầu đang chờ.
`không`, `thôi`, `bỏ qua`, `hủy` bỏ thao tác xóa. Việc chọn số chưa xóa dữ liệu.
Xóa thành công loại bỏ đúng bản ghi SQLite đã chọn; không có chức năng hoàn tác.
Nếu bản ghi đã thay đổi từ lúc hỏi xác nhận, chương trình không xóa và yêu cầu tìm lại.
Ngữ cảnh chờ chỉ tồn tại trong lần chạy hiện tại; xác nhận lặp không xóa thêm bản ghi.
Chưa hỗ trợ sửa, lịch lặp hoặc thông báo đến hạn. “Vừa tạo” chưa được giải nghĩa
thành bản ghi gần nhất; nên nêu nội dung/ngày cụ thể.
FAQ hiện có vẫn được dùng cho `open_question`.

## Kiểm thử tích hợp

Bộ tách `src/minimate/reminder_parser.py` xử lý hành động, nội dung và thời điểm
sau bước dự đoán. Mẫu tạo rõ ràng như “Nhắc tôi …” được ưu tiên khi điều phối
nếu model nhận nhầm nhóm; confidence vẫn là điểm model, không phải độ chắc chắn của luật.
Phần xử lý chạy
sau model 7 intent, không thay trọng số model. Hỗ trợ ngày mai/sáng mai/chiều mai,
hôm nay/sau N ngày; giờ dạng số như 9 giờ, 9:30, 9 giờ sáng, 3 giờ chiều.
Nội dung giữ dấu tiếng Việt; hỗ trợ thời gian trước hoặc sau nội dung:

```text
Nhắc tôi 9 giờ sáng ngày mai làm bài kiểm tra
Nhắc tôi sáng mai 9 giờ đi học
Nhắc tôi đi học
Sáng mai lúc 9 giờ
```

Câu thiếu dữ liệu được hỏi đúng phần thiếu, ngữ cảnh chỉ giữ trong lần chạy hiện tại.
Yêu cầu “nhắc tôi” cũng được nhận ở giữa/cuối câu, ví dụ “Ngày mai tôi phải đi học,
nhắc tôi vào lúc 2 giờ chiều” lưu nội dung “đi học”, giờ 14:00.
Nhập `hủy`/`bỏ qua` để bỏ yêu cầu đang chờ, không xóa dữ liệu đã lưu.
Câu đủ dữ liệu nhưng không có yêu cầu tạo rõ ràng, ví dụ “9 giờ sáng ngày mai đi học”,
sẽ hỏi xác nhận nếu model phân loại vào lịch nhắc; trả lời `đồng ý` hoặc `không`.
Giờ sai, thời điểm quá khứ hoặc nhiều thời điểm cần nhập lại. Lịch lặp vẫn chưa hỗ trợ.
Bộ luật không bao phủ mọi câu tự nhiên, ngày viết số/chữ hoặc thời gian mơ hồ như “lát nữa”.

`python -m unittest discover -s tests -v` dùng SQLite trong bộ nhớ/tệp tạm.
Test classifier dùng giả lập thư viện để kiểm tra nạp một lần, nhãn config,
đầu vào rỗng, lỗi thiếu thư viện/file và cách CLI chọn model mặc định.
Đã thử thêm model local thật trong `.venv_hf_test` với `--db :memory:`:
bắt đầu thiếu thời lượng → 25 phút, thời gian còn lại, tra cứu lịch, yêu cầu xóa,
yêu cầu bật điều hòa. Không dùng SQLite thật để kiểm thử.

## Bảy intent

1. `greeting` — chào hỏi
2. `focus_session_control` — bắt đầu hoặc hủy phiên học
3. `check_focus_session` — hỏi thời gian còn lại hoặc trạng thái phiên
4. `schedule_reminder` — tạo lời nhắc hoặc tra cứu lịch đã lưu
5. `repeat_response` — yêu cầu nhắc lại phản hồi
6. `open_question` — câu hỏi kiến thức/yêu cầu giải thích
7. `out_of_scope` — yêu cầu ngoài phạm vi hoặc chưa đủ rõ để xử lý

## Chạy thử

```powershell
python src/main.py --text "bắt đầu học 25 phút"
python src/main.py
python -m unittest discover -s tests -v
```

Trên Windows, có thể nhấp đúp [`run_minimate.bat`](run_minimate.bat) để mở
chương trình terminal. Máy cần có Python trong `PATH`.

## Câu thử nhanh

```text
Bắt đầu học 25 phút
Còn bao lâu?
Nhắc tôi nộp bài ngày mai lúc 8 giờ
Xem lịch đã lưu
Pomodoro là gì?
Nhắc lại
Ngày mai 8 giờ
```

Mỗi lần nhập, terminal hiển thị câu trả lời dễ đọc và JSON response gồm
`intent`, `confidence`, `action`, `text`, `device_state`, `session_state`.

Xem kiến trúc, giao thức dữ liệu và tiêu chuẩn bàn giao tại
[`docs/architecture.md`](docs/architecture.md).
