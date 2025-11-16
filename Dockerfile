# نبدأ من صورة تحتوي على Python و Chrome و ChromeDriver
FROM selenium/standalone-chrome:latest

# تحديث الحزم وتثبيت Python و pip
USER root
RUN apt-get update -y && apt-get install -y python3 python3-pip

# تثبيت المكتبات التي نحتاجها مثل selenium و webdriver_manager
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# نسخ السكربت الخاص بك إلى الحاوية
COPY your_script.py .

# تشغيل السكربت
CMD ["python3", "your_script.py"]
