FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libappindicator3-1 \
    libx11-xcb1 \
    xdg-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]
