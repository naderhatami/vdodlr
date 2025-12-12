# استفاده از ایمیج سبک پایتون
FROM python:3.13-slim

# نصب ffmpeg و ابزارهای پایه
RUN apt-get update && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌های requirements
COPY requirements.txt .

# نصب پکیج‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کل پروژه
COPY . .

# اجرای بات
CMD ["python", "bot.py"]
