FROM python:3.11-slim

WORKDIR /app

# COPY packages.txt .
RUN apt-get update && \
apt-get install -y tesseract-ocr poppler-utils && \
rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Dockerfile .

COPY .streamlit/ ./.streamlit/

COPY utils.py .

COPY images/ ./images/

COPY pages/ ./pages/

COPY Main.py .

EXPOSE 8501

CMD ["streamlit", "run", "Main.py"]
