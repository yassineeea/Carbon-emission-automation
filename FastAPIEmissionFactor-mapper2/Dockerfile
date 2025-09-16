FROM python:3.10

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Set Hugging Face cache to a writable location
ENV HF_HOME=/tmp/hf_cache

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
