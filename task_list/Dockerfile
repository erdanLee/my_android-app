FROM python:3.11-slim
WORKDIR /task_list
COPY requirements.txt .
RUN pip install --no-cache-dir flet==0.27.6
COPY . .
CMD ["python", "app.py"]