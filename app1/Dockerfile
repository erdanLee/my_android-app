FROM python:3.11-slim
WORKDIR /app1
COPY requirements.txt .
RUN pip install --no-cache-dir flet==0.27.6
COPY . .
CMD ["python", "main.py"]