FROM python:3.11-slim
WORKDIR /task_list
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]