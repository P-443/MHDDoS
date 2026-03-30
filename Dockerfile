FROM python:3.8.12-buster

WORKDIR /app

COPY ./ ./

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "mm.py"]
