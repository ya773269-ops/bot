from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service
# إعداد المتصفح في وضع Headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # تشغيل المتصفح بدون واجهة رسومية
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--remote-debugging-port=9222")  # تجنب بعض المشاكل في البيئات الافتراضية

# إعداد المتصفح باستخدام WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="142.0.7444.162").install()), options=chrome_options)


# فتح صفحة Instagram
driver.get("https://www.instagram.com")

# الانتظار قليلاً حتى يتم تحميل الصفحة
time.sleep(3)

# البحث عن حقول الإدخال الخاصة بالبريد الإلكتروني وكلمة المرور
username_input = driver.find_element(By.NAME, "username")
password_input = driver.find_element(By.NAME, "password")

# إدخال بيانات الدخول
username_input.send_keys("your_username")  # ضع اسم المستخدم هنا
password_input.send_keys("your_password")  # ضع كلمة المرور هنا

# الضغط على زر الدخول
password_input.send_keys(Keys.RETURN)

# الانتظار قليلاً حتى يتم تسجيل الدخول
time.sleep(5)

# إغلاق المتصفح في النهاية
driver.quit()
