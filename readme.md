# 🤖 MINIMATE – Thiết Bị Trợ Lý Học Tập Thông Minh Tích Hợp AI & Nhúng

**Học phần:** Trí tuệ nhân tạo (INT3401 12) – Trường Đại học Công nghệ, ĐHQGHN (UET-VNU)  
**Nhóm thực hiện:** Nhóm 10  
**Repository:** `24022943/Artificial-Intelligence_MiniMate`

## 📖 Giới Thiệu Đề Tài

**MINIMATE** là thiết bị trợ lý học tập để bàn kết hợp giữa xử lý ngôn ngữ tự nhiên tiếng Việt (AI/ML), hệ thống điều phối hội thoại trên máy tính (Backend) và thiết bị phần cứng nhúng tương tác trực tiếp (ESP32-S3 + màn hình biểu cảm OLED/TFT + âm thanh).

Thiết bị hỗ trợ người học quản lý phiên học tập rảnh tay bằng giọng nói tiếng Việt, theo dõi thời gian học, kiểm tra trạng thái, giải đáp câu hỏi mở và phản hồi trực quan qua cả giọng nói (Text-to-Speech) lẫn biểu cảm mắt hoạt họa theo thời gian thực.

## ✨ Tính Năng Chính

- **Nhận dạng ý định (Intent Classification) tiếng Việt:** Phân loại câu lệnh người dùng bằng mô hình học máy (`TF-IDF` kết hợp `Logistic Regression` / `SVM`) đối sánh với `Keyword Baseline`, có cơ chế kiểm soát ngưỡng tin cậy (*Clarification Threshold*) để hỏi lại khi câu lệnh mơ hồ hoặc thiếu thông tin.
- **Quản lý phiên học & Điều phối 6 nhóm tác vụ:**
  1. **Bắt đầu phiên học:** Khởi tạo bộ đếm thời gian học tập theo yêu cầu.
  2. **Hủy phiên học:** Dừng hoặc kết thúc sớm phiên học hiện tại.
  3. **Hỏi thời gian còn lại:** Thông báo thời lượng còn lại của phiên học đang diễn ra.
  4. **Hỏi trạng thái:** Báo cáo trạng thái hoạt động hiện tại của hệ thống và phiên học.
  5. **Nhắc lại phản hồi:** Phát lại câu trả lời gần nhất của thiết bị.
  6. **Hội thoại mở:** Chuyển các câu hỏi kiến thức hoặc trò chuyện ngoài tác vụ cố định sang module hội thoại mở.
- **Tương tác giọng nói hai chiều (STT & TTS):** Chuyển đổi giọng nói tiếng Việt từ microphone sang văn bản (*Speech-to-Text*) và tổng hợp giọng nói phản hồi tự nhiên (*Text-to-Speech*).
- **Tương tác phần cứng & 6 trạng thái biểu cảm hoạt họa:** Đồng bộ thời gian thực giữa trạng thái xử lý của Backend với firmware ESP32-S3 và màn hình OLED/TFT qua 6 trạng thái:
  - `Idle` (Nghỉ)
  - `Listening` (Đang nghe)
  - `Processing` (Đang xử lý)
  - `Speaking` (Đang trả lời)
  - `Clarification` (Chờ làm rõ / Xác nhận)
  - `Error` (Lỗi kết nối / Hệ thống)

## 🏗️ Kiến Trúc Hệ Thống & Luồng Hoạt Động

Hệ thống MINIMATE hoạt động theo pipeline khép kín từ phần cứng đầu cuối đến mô hình AI và quay lại thiết bị:

1. **Thu nhận tín hiệu (Hardware Input):** Người dùng nhấn nút trên thiết bị ESP32-S3 và nói vào microphone; thiết bị chuyển sang trạng thái `Listening` (màn hình hiển thị biểu cảm *Đang nghe*).
2. **Chuyển đổi giọng nói (STT):** Âm thanh được gửi về máy tính qua giao thức giao tiếp và chuyển thành văn bản tiếng Việt; thiết bị chuyển sang trạng thái `Processing` (*Đang xử lý*).
3. **Nhận dạng Intent (AI/ML Module):** Văn bản được tiền xử lý và đưa qua mô hình `TF-IDF + Logistic Regression / SVM` để dự đoán nhãn Intent cùng điểm tin cậy (*Confidence Score*).
4. **Quản lý trạng thái & Điều phối tác vụ (Task Manager & Dialogue):**
   - Nếu độ tin cậy thấp hơn ngưỡng hoặc thiếu tham số (ví dụ: chưa rõ thời lượng học), hệ thống chuyển sang trạng thái `Clarification` (*Chờ làm rõ*) và yêu cầu người dùng xác nhận.
   - Nếu đủ thông tin, bộ quản lý tác vụ thực thi hành động tương ứng hoặc chuyển sang module hội thoại mở.
5. **Phản hồi đa phương thức (TTS & Embedded UI):** Backend sinh câu trả lời bằng giọng nói (TTS), gửi tín hiệu trạng thái `Speaking` (*Đang trả lời*) và âm thanh về ESP32-S3 để phát ra loa đồng bộ với animation trên màn hình OLED/TFT, đồng thời ghi log độ trễ (*Latency*) của toàn bộ quá trình.

## 🛠️ Công Nghệ & Phần Cứng Sử Dụng

| Phân hệ | Công nghệ / Thiết bị | Vai trò trong dự án |
| :--- | :--- | :--- |
| **AI / Machine Learning** | Python, Scikit-learn, Pandas, NumPy | Tiền xử lý dữ liệu tiếng Việt, trích xuất đặc trưng `TF-IDF`, huấn luyện `Logistic Regression` / `SVM`, đánh giá `Precision`, `Recall`, `Macro-F1`, `Confusion Matrix` |
| **Backend & Voice** | Python, REST API / Serial / WebSocket, STT & TTS Engine | Điều phối tác vụ, quản lý trạng thái phiên học, hội thoại mở, chuyển đổi giọng nói ↔ văn bản và ghi log thời gian xử lý |
| **Vi điều khiển & Firmware** | C/C++ (Arduino / ESP-IDF), ESP32-S3 | Đọc sự kiện nút nhấn, thu/phát âm thanh, quản lý State Machine thiết bị và truyền nhận dữ liệu với máy tính |
| **Linh kiện ngoại vi & UI** | Màn hình OLED/TFT, Microphone, Loa & Mạch khuếch đại âm thanh, Nút nhấn | Hiển thị 6 trạng thái biểu cảm mắt hoạt họa và giao tiếp âm thanh trực tiếp với người dùng |

## 📂 Cấu Trúc Thư Mục Dự Án

- `data/` – Bộ dữ liệu câu lệnh tiếng Việt và tài liệu hướng dẫn gán nhãn (`labeling_guideline.md`)
  - `data/raw/` – Dữ liệu thu thập thô ban đầu
  - `data/processed/` – Dữ liệu đã tiền xử lý và chia tập `train.csv`, `val.csv`, `test.csv`
- `ml/` – Module huấn luyện và đánh giá mô hình nhận dạng Intent
  - `ml/baseline/` – Mô hình phân loại cơ sở bằng từ khóa (Keyword Baseline)
  - `ml/models/` – Script huấn luyện `TF-IDF + Logistic Regression / SVM` và file model đã lưu (`.pkl`)
  - `ml/evaluation/` – Công cụ tính `Precision`, `Recall`, `Macro-F1`, vẽ `Confusion Matrix` và phân tích lỗi
- `backend/` – Chương trình xử lý chính trên máy tính
  - `backend/intent_service/` – API nạp model ML và kiểm tra ngưỡng yêu cầu làm rõ (`clarification_threshold`)
  - `backend/task_manager/` – Bộ quản lý trạng thái phiên học và điều phối 6 tác vụ
  - `backend/dialogue/` – Module xử lý câu hỏi mở và xác nhận thông tin thiếu
  - `backend/speech/` – Tích hợp Speech-to-Text (STT) và Text-to-Speech (TTS)
  - `backend/protocol/` – Giao thức truyền thông giữa máy tính và ESP32-S3
  - `backend/logs/` – Công cụ theo dõi và ghi log thời gian xử lý (latency) từng yêu cầu
- `firmware/` – Mã nguồn nhúng C/C++ trên vi điều khiển ESP32-S3
  - `firmware/main/` – Xử lý sự kiện nút nhấn, microphone, loa và quản lý 6 trạng thái thiết bị
  - `firmware/protocol/` – Module gửi/nhận gói tin với máy tính
- `embedded_ui/` – Giao diện và hoạt họa biểu cảm trên màn hình OLED/TFT
  - `embedded_ui/animations/` – Bộ khung hình biểu cảm cho 6 trạng thái (`Idle`, `Listening`, `Processing`, `Speaking`, `Clarification`, `Error`)
  - `embedded_ui/state_machine/` – Bộ chuyển đổi trạng thái hiển thị đồng bộ với hệ thống
- `hardware/` – Sơ đồ mạch nguyên lý, danh sách linh kiện (BOM) và hướng dẫn lắp ráp thiết bị
- `docs/` – Tài liệu kiến trúc phần mềm, đặc tả giao thức, mapping trạng thái → biểu cảm và báo cáo kết quả ML

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử Nghiệm

### 1. Yêu cầu hệ thống

- **Máy tính:** Python `3.9+`, Git, kết nối cổng USB/Serial hoặc Wi-Fi cùng mạng với ESP32-S3.
- **Phần cứng nhúng:** Arduino IDE hoặc PlatformIO / ESP-IDF (hỗ trợ board `ESP32-S3`), màn hình OLED/TFT, module microphone, mạch âm thanh + loa và nút nhấn.

### 2. Cài đặt môi trường phần mềm (AI/ML & Backend)

Sao chép kho mã nguồn về máy tính và cài đặt các thư viện cần thiết:

```bash
git clone https://github.com/24022943/Artificial-Intelligence_MiniMate.git
cd Artificial-Intelligence_MiniMate
pip install -r requirements.txt
```

### 3. Huấn luyện và đánh giá mô hình Intent (ML)

```bash
# Chạy thử nghiệm Keyword Baseline
python ml/baseline/keyword_baseline.py

# Huấn luyện mô hình TF-IDF + Logistic Regression / SVM
python ml/models/train_intent_model.py

# Đánh giá mô hình trên tập Test (Precision, Recall, Macro-F1, Confusion Matrix)
python ml/evaluation/evaluate_model.py
```

### 4. Khởi chạy chương trình chính (Backend Service)

```bash
python backend/main.py
```

### 5. Nạp Firmware và Giao diện lên ESP32-S3

1. Kết nối các linh kiện (nút nhấn, màn hình OLED/TFT, microphone, loa) với ESP32-S3 theo sơ đồ mạch trong thư mục `hardware/`.
2. Mở dự án trong `firmware/` bằng Arduino IDE hoặc PlatformIO.
3. Cấu hình thông số kết nối (cổng Serial hoặc Wi-Fi/IP của máy tính chạy Backend) và nạp code xuống mạch ESP32-S3.

## 📊 Chỉ Số Đánh Giá Hệ Thống

- **Đánh giá mô hình phân loại Intent:**
  - Độ chính xác theo từng lớp và toàn cục: `Precision`, `Recall`, `Macro-F1`.
  - Ma trận nhầm lẫn (`Confusion Matrix`) giữa các nhóm intent.
  - Phân tích lỗi nhận dạng trên câu lệnh nhiễu từ STT và hiệu quả của ngưỡng yêu cầu làm rõ (*Clarification Threshold*).
- **Đánh giá hiệu năng & Trải nghiệm thiết bị:**
  - Độ trễ toàn trình (*End-to-End Latency*) từ thời điểm người dùng nhấn nút nói đến khi thiết bị phát âm thanh và đổi biểu cảm phản hồi.
  - Tốc độ làm tươi khung hình animation trên màn hình OLED/TFT và độ ổn định khi hoạt động liên tục.

## 👥 Thành Viên Nhóm 10 & Phân Công Trách Nhiệm

| STT | Họ và tên | Mã SV / GitHub | Vai trò chính | Sản phẩm bàn giao trọng tâm |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Phạm Thị Ngọc Anh** *(Trưởng nhóm)* | `24022943` | AI/ML, Dataset & Quản lý tích hợp phần mềm | Dataset tiếng Việt & hướng dẫn gán nhãn, Keyword Baseline, Model `TF-IDF + LR/SVM`, Báo cáo đánh giá ML, Cấu trúc Git |
| 2 | **Nguyễn Ngọc Hiệp** | `23021545` | Backend, Quản lý tác vụ, Hội thoại & STT/TTS | Chương trình xử lý chính, Intent API, Task Manager (6 tác vụ), Module hội thoại mở, tích hợp STT/TTS, Công cụ ghi log |
| 3 | **Nguyễn Quốc Đạt** | – | Phần cứng, Firmware ESP32-S3 & Giao tiếp | Sơ đồ mạch, Danh sách linh kiện (BOM), Firmware C/C++ (6 trạng thái & nút nhấn), Giao thức ESP32 ↔ PC, Prototype phần cứng |
| 4 | **Nguyễn Ngọc Khôi Nguyên** | `24020254` | Embedded UI, Biểu cảm hoạt họa & UX | Code giao diện OLED/TFT, Bộ animation 6 trạng thái, State Machine biểu cảm, Tài liệu mapping trạng thái → biểu cảm |

## 📅 Lộ Trình Thực Hiện (4 Tuần: Tuần 9 – Tuần 12)

| Giai đoạn | Thời gian | Trọng tâm thực hiện | Mốc kiểm soát (Milestone) |
| :--- | :--- | :--- | :--- |
| **Tuần 1** *(Tuần 9)* | `02/11 – 08/11/2026` | Khảo sát kiến trúc, chốt danh sách intent, thu thập & chia tập dataset tiếng Việt, xây dựng baseline từ khóa, thiết kế sơ đồ mạch ESP32-S3 & prototype biểu cảm | **M1:** Chốt kiến trúc hệ thống, hoàn thành Dataset v1, Baseline & kiểm tra xong linh kiện rời |
| **Tuần 2** *(Tuần 10)* | `09/11 – 15/11/2026` | Huấn luyện mô hình `TF-IDF + LR/SVM`, xây dựng Intent API & Task Manager 6 tác vụ, lập trình firmware nút nhấn/6 trạng thái & State Machine biểu cảm | **M2:** Model ML đạt chuẩn, Task Manager chạy đủ 6 tác vụ & giao thức 2 chiều ESP32 ↔ PC hoạt động |
| **Tuần 3** *(Tuần 11)* | `16/11 – 22/11/2026` | Tích hợp STT/TTS, lắp ráp hoàn chỉnh phần cứng vào vỏ thiết bị, ghép nối màn hình thật & đồng bộ toàn bộ pipeline liên module | **M3:** Hoàn thiện Prototype phần cứng & thông suốt luồng Giọng nói → AI/Backend → Thiết bị |
| **Tuần 4** *(Tuần 12)* | `23/11 – 29/11/2026` | Kiểm thử End-to-End, đo kiểm latency từ nút nhấn đến phản hồi, đánh giá UX, hoàn thiện báo cáo ML & diễn tập kịch bản Demo | **M4:** Hệ thống đạt chỉ số `Macro-F1` & độ trễ mục tiêu; hoàn tất tài liệu và sẵn sàng bảo vệ Demo |
