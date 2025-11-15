FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt functions-framework

COPY main.py .

ENTRYPOINT ["functions-framework", "--target=generate_sales_report", "--source=main.py"]
