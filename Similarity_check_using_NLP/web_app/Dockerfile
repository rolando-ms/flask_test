FROM python:3.11
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -U --no-cache-dir -r requirements.txt
COPY . .
RUN pip install ./en_core_web_sm-3.8.0-py3-none-any.whl
CMD ["python", "app.py"]