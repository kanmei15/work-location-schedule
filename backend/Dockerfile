FROM python:3.11-slim

# 作業ディレクトリ作成
WORKDIR /backend

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# アプリ起動（DB初期化 → FastAPI起動）
CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]