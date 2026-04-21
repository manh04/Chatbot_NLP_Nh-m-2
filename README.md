# LEGAL AGENT - Hệ thống tư vấn Nghị định 168 về đăng ký doanh nghiệp

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.7.3-green.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
## Giới thiệu

Legal Agent là một hệ thống trợ lý ảo thông minh chuyên tư vấn và tra cứu Nghị định 168/NĐ-CP về đăng ký doanh nghiệp. Dự án được xây dựng như một bài tập nhóm, áp dụng các kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) và trí tuệ nhân tạo (AI) để giải quyết bài toán tra cứu văn bản pháp luật một cách hiệu quả.

## Mục tiêu

- Tự động hóa việc tra cứu thông tin từ văn bản pháp luật dài hàng trăm trang
- Cung cấp câu trả lời chính xác, nhanh chóng thay vì đọc toàn bộ văn bản
- Hỗ trợ người dùng cuối (doanh nghiệp, cá nhân) trong việc tìm hiểu thủ tục đăng ký kinh doanh
- Ứng dụng các công nghệ AI hiện đại như RAG (Retrieval-Augmented Generation), Hybrid Search, Reranking
  
---

# Thành viên nhóm

| STT | Họ tên           | Mã Sinh Viên |
| --- | ---------------- | -------------|
| 1   | Nguyễn Đình Mạnh | 22174600037  |
| 2   | Lê Văn Khá       | 22174600096  |
| 3   | Hà Quang Vinh    | 22174600065  |
| 4   | Lưu Nhật Nam     | 22174600109  |
| 5   | Đặng Hữu Tâm     | 22174600022  |

---
## Tính năng chính

**1. Xử lý PDF scanned**

Hệ thống có thể xử lý các file PDF được scan từ sách giấy, sử dụng EasyOCR kết hợp với tiền xử lý ảnh (tăng contrast, nhị phân hóa, khử nhiễu) để trích xuất văn bản với độ chính xác cao.

**2. Parse cấu trúc pháp luật thông minh**

Tự động nhận diện và trích xuất cấu trúc phân cấp của văn bản pháp luật: Chương, Điều, Khoản, Điểm.

**3. Hybrid Search (BM25 + Dense Embedding)**

Kết hợp hai phương pháp tìm kiếm: BM25 tìm kiếm chính xác theo từ khóa và Dense Embedding tìm kiếm theo ngữ nghĩa.

**4. Reranking kết quả**

Sử dụng Cross-Encoder để tái sắp xếp kết quả tìm kiếm, đưa ra những thông tin liên quan nhất lên đầu.

**5. Truy xuất tham chiếu chéo**

Khi một điều khoản nhắc đến điều khoản khác, hệ thống tự động tìm và lấy nội dung của điều khoản được tham chiếu.

**6. Cache thông minh**

Lưu cache OCR, câu trả lời, model config để tăng tốc độ xử lý.

**7. Hướng dẫn chi tiết**

Câu trả lời kèm hướng dẫn thực hiện, giấy tờ cần chuẩn bị, cơ quan có thẩm quyền.

**8. Giao diện Streamlit**

Web app thân thiện, dễ sử dụng, hiển thị rõ nguồn tham khảo.

## Kiến trúc hệ thống

Hệ thống được chia thành 3 giai đoạn xử lý chính:

**Giai đoạn 1: Tiền xử lý và xây dựng database**

- OCR file PDF bằng EasyOCR
- Parse cấu trúc Chương, Điều, Khoản, Điểm
- Tạo chunks và embeddings bằng Vietnamese-SBERT
- Lưu vào Qdrant vector database
- Xây dựng BM25 index

**Giai đoạn 2: Truy xuất và xử lý**

- Hybrid Search (BM25 + Dense)
- Reranking bằng Cross-Encoder
- Phát hiện và truy xuất tham chiếu chéo

**Giai đoạn 3: Sinh câu trả lời**

- Prompt engineering
- LLM sinh câu trả lời tự nhiên (TinyLlama hoặc Qwen)
- Đưa ra hướng dẫn chi tiết

## Cấu trúc dự án
# Legal Agent - Hệ thống AI Tra cứu Nghị định 168

Hệ thống AI hỗ trợ tra cứu, hỏi đáp và tư vấn nội dung **Nghị định 168 về đăng ký doanh nghiệp** bằng công nghệ NLP, Vector Search và LLM nội bộ.

---

##  Cấu trúc thư mục dự án

```text
Bai_tap_nhom/
│
├── README.md                     # Tài liệu dự án
├── requirements.txt              # Danh sách thư viện
│
├── config.py                     # Cấu hình hệ thống
├── utils.py                      # Hàm tiện ích
│
├── data/                         # Module xử lý dữ liệu
│   ├── __init__.py
│   ├── ocr.py                    # OCR và cache
│   ├── parser.py                 # Parse văn bản pháp luật
│   └── chunker.py                # Chunking và tạo database
│
├── retrieval/                    # Module truy xuất dữ liệu
│   ├── __init__.py
│   └── qdrant_retriever.py       # Hybrid Search + Rerank
│
├── agent/                        # Module Agent
│   ├── __init__.py
│   ├── legal_agent.py
│
├── creat_database.py             # Chạy giai đoạn 1
├── chatbot.py                    # Chạy CLI
├── app.py                        # Ứng dụng Streamlit
│
├── nghi_dinh_168.pdf             # File PDF đầu vào
│
├── qdrant_legal_db/              # Vector DB (tự tạo)
├── metadata_qdrant/              # Metadata (tự tạo)
├── ocr_cache/                    # Cache OCR (tự tạo)
│
└── NLP/                          # Virtual environment
```

---

# Công nghệ sử dụng

* **Python 3.10+**
* **Streamlit** - Giao diện web
* **Qdrant** - Vector Database
* **BM25** - Keyword Search
* **Sentence-BERT** - Embedding tiếng Việt
* **Cross Encoder** - Rerank kết quả
* **EasyOCR** - OCR file scan
* **OpenCV** - Tiền xử lý ảnh
* **PyMuPDF** - Đọc PDF
* **Transformers** - Load mô hình HuggingFace
* **LangChain** - Kết nối pipeline
* **TinyLlama / Qwen / Phi-3** - Local LLM

---

# Cài đặt

## Bước 1: Clone project

```bash
git clone https://github.com/manh04/Chatbot_NLP_Nhom.git
cd legal-agent
```

---

## Bước 2: Tạo môi trường ảo

### Windows

```bash
python -m venv NLP
NLP\Scripts\activate
```

### Linux / MacOS

```bash
python -m venv NLP
source NLP/bin/activate
```

---

## Bước 3: Cài thư viện

```bash
pip install -r requirements.txt
```

---

## requirements.txt

```txt
streamlit>=1.28.0
qdrant-client==1.7.3
langchain>=0.1.0
langchain-community>=0.0.10
langchain-huggingface>=0.0.3
sentence-transformers>=2.2.0
rank-bm25>=0.2.2
transformers>=4.35.0
torch>=2.0.0
pymupdf>=1.23.0
easyocr>=1.7.0
pandas>=2.0.0
tqdm>=4.65.0
Pillow>=10.0.0
numpy>=1.24.0
opencv-python>=4.8.0
```

---

# Chuẩn bị dữ liệu

Đặt file PDF vào thư mục gốc:

```text
nghi_dinh_168.pdf
```

---

#  Chạy hệ thống

## Giai đoạn 1: OCR + Parse + Tạo Database

```bash
python creat_database.py
```

### Hệ thống sẽ:

* OCR file scan
* Parse Chương / Điều / Khoản / Điểm
* Chunking dữ liệu
* Sinh Embedding
* Tạo Qdrant Database
* Tạo BM25 Index
* Lưu metadata

---

## Giai đoạn 2: Chạy CLI Test

```bash
python chatbot.py
```

---

## Giao diện Web Streamlit

```bash
streamlit run app.py
```

Mở tại:

```text
http://localhost:8501
```

---

#  Hướng dẫn sử dụng

## Sidebar trái:

* Chọn Chương cần hỏi

## Ô nhập câu hỏi:

Ví dụ:

* Đăng ký doanh nghiệp là gì?
* Hồ sơ đăng ký gồm những gì?
* Thủ tục đăng ký qua mạng?
* Có được ủy quyền không?
* Mã số doanh nghiệp có đổi không?
* Điều 3 khoản 1 quy định gì?

---

# ⚙️ Tùy chỉnh cấu hình

File:

```python
config.py
```

```python
class Config:
    PDF_PATH = BASE_DIR / "nghi_dinh_168.pdf"
    QDRANT_DB_PATH = BASE_DIR / "qdrant_legal_db"

    EMBEDDING_MODEL = "keepitreal/vietnamese-sbert"

    # Chọn model
    LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    # LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
    # LLM_MODEL = "microsoft/Phi-3-mini-4k-instruct"

    TOP_K_RESULTS = 5
    BM25_WEIGHT = 0.3
    DENSE_WEIGHT = 0.7

    TEMPERATURE = 0.3
    MAX_NEW_TOKENS = 256
```

---

## Máy yếu nên dùng:

```python
LLM_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
TOP_K_RESULTS = 2
MAX_NEW_TOKENS = 128
```

---

# 🛠️ Xử lý lỗi thường gặp

## 1. Lỗi qdrant search

```text
'QdrantClient' object has no attribute 'search'
```

### Fix:

```bash
pip uninstall qdrant-client -y
pip install qdrant-client==1.7.3
```

---

## 2. Lỗi fitz frontend

```text
No module named frontend
```

### Fix:

```bash
pip uninstall fitz -y
pip uninstall PyMuPDF -y
pip install PyMuPDF
```

---

## 3. Database bị khóa

```text
Storage folder is already accessed
```

### Fix:

```bash
rmdir /s /q qdrant_legal_db
rmdir /s /q metadata_qdrant
python create_database.py
```

---

## 4. Out of Memory

### Giảm cấu hình:

```python
MAX_NEW_TOKENS = 64
TOP_K_RESULTS = 2
```

---

## 5. Lỗi import agent

```text
Cannot import name 'SimpleAgent'
```

### Fix:

Tạo file:

```text
agent/__init__.py
```

(có thể để trống)


---

#  Tài liệu tham khảo

* Nghị định 168/NĐ-CP về đăng ký doanh nghiệp
* Qdrant Documentation
* HuggingFace Transformers
* Streamlit Docs
* Sentence-BERT

---


