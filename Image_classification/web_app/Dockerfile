FROM python:3.11
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -U --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]