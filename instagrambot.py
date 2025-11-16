# !pip install rarfile
# import rarfile

# # استخراج الملف المضغوط
# with rarfile.RarFile("/content/mybot.rar") as rf:
#     rf.extractall("/content/bot")  # اختر المجلد الذي ترغب في استخراج الملفات فيه
#  !pip install selenium
# !pip install pyotp
# !pip install telegram
# !pip install selenium
import threading
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import os
import json
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import os
import pyotp
import json
import threading
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import sys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 يتم الآن إعادة تشغيل البوت...")
    await asyncio.sleep(1)
    os.system("taskkill /f /im chrome.exe >nul 2>&1")
    os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
    await update.message.reply_text("تم اغلاق جميع العمليات.")
    
    python = sys.executable
    os.execl(python, python, *sys.argv)
    await asyncio.sleep(2)
    await update.message.reply_text("تم اعاده تشغيل البوت")
# عدد العمليات المتزامنة المسموح بها
MAX_PARALLEL_THREADS = 5
thread_limiter = threading.Semaphore(MAX_PARALLEL_THREADS)


PENDING_TASKS=[]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "account", "accounts.json")
FAILED_ACCOUNTS_FILE= os.path.join(BASE_DIR, "account", "failed_accounts.json")
WATCHLIST=os.path.join(BASE_DIR, "account", "watchlist.json")
PENDING_TASKS_FILE=os.path.join(BASE_DIR, "account", "pending.json")
backup_filename= os.path.join(BASE_DIR, "account", "accounts_backup.json")
TOKENS_FILE =  os.path.join(BASE_DIR, "cookies", "tokens.json") 

def load_accounts(file_path=ACCOUNTS_FILE):
    with open(file_path, "r", encoding="utf-8") as f:
        accounts = json.load(f)
        return random.sample(accounts, len(accounts))  # يرجع نسخة عشوائية مرتبة
    
def load_accounts1(file_path=WATCHLIST):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
stop_flag = False

def load_comments_from_file(file_path=os.path.join(BASE_DIR, "account", "commit.txt")):
    if not os.path.exists(file_path):
        print(f"⚠️ ملف التعليقات غير موجود: {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        comments = [line.strip() for line in f if line.strip()]
    return comments


COMMENT_LIST=load_comments_from_file()


CURRENT_OPERATION = {
    "name": None,        
    "active": False,     
    "completed": 0,     
    "total": 0 ,
    "number" :0
                     
}
 

PROSSING = {
    "post_url": None,       
    "story_username": None,   
    "completed": 0,      
    "total": 0           
}
ACCOUNTS = load_accounts()
#ACCOUNTS_FILE = "C:/Users/ACER/Desktop/script_python/New folder/account/accounts.json"
#FAILED_ACCOUNTS_FILE = "C:/Users/ACER/Desktop/script_python/New folder/account/failed_accounts.json"
SETTING_LIKE_COUNT, SETTING_COMMENT_ACCOUNTS,UNFOLLOW_USER, SETTING_COMMENTS_PER_ACCOUNT, SETTING_FOLLOW_COUNT,ADD_USER, DEL_USER,EDIT_COMMENTS,SHOW_COMMENT,SETTING_OPTION = range(100, 110)

TYPING_CHECK_USERNAMES = range(1000, 1001)  
waiting_users = []
# 💬 تفاصيل المنشور والتفاعل
PHOTO_URL_FOR_COMMENT = "https://www.instagram.com/reel/DKuzkEjIsMb/?utm_source=ig_web_copy_link&igsh=YTJoOGxtcDh3cGQw"
COMMENT_TEXT = "naic"
PHOTO_URL_FOR_LIKE = "https://www.instagram.com/reel/DKuzkEjIsMb/?utm_source=ig_web_copy_link&igsh=YTJoOGxtcDh3cGQw"
ACCOUNT_TO_FOLLOW = "alhaydari.7"
REPLY_TEXT_ON_STORY = "Awesome Story!"
open_browsers = []
def human_delay(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

def get_secret_for_username(username):
    try:
        
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                tokens = json.load(f)
                return tokens.get(username)
    except:
        pass
    return None


class process_account():

    def __init__(self, username, password, photo_url_for_comment=None, account_to_follow=None, reply_text_on_story=None, like_url=None,
        comment_text=None):
        self.username = username
        self.password = password
        # self.token = token
        self.photo_url_for_comment = photo_url_for_comment
        self.account_to_follow = account_to_follow
        self.reply_text_on_story = reply_text_on_story
        self.like_url = like_url
        self.comment_text = comment_text
        # self.driver = None 
        self.trigger_lock = threading.Lock()  # لقفل التفاعل


        print(f"\n🔐 بدء المعالجة للحساب: {self.username}")
        self.cookie_file = os.path.join("cookies", f"{self.username}.pkl")

        
       
        self.options = Options()
        # self.options.add_argument("--headless=new")
        # self.options.add_argument("--blink-settings=imagesEnabled=false")#تقليل تحميل الصور 
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("--start-maximized")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")

        # ✅ إنشاء المتصفح و WebDriverWait هنا:
        try:
         print("🧪 محاولة تشغيل المتصفح...")
         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
         print("✅ تم إنشاء المتصفح.")
        except Exception as e:
           print(f"❌ فشل تشغيل المتصفح: {e}")

        self.wait = WebDriverWait(self.driver, 15)

   
  #  cookie_file = f"C:/Users/ACER/Desktop/script_python/New folder/cookies/{username}.pkl"
   




    def save_cookies(self):
        try:
           
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            pickle.dump(self.driver.get_cookies(), open(self.cookie_file, "wb"))
            print(f"💾 [{self.username}] تم حفظ الكوكيز بنجاح.")
        except Exception as e:
            print(f"⚠️ [{self.username}] لم أتمكن من حفظ الكوكيز: {e}")

    def load_cookies(self):
        if os.path.exists(self.cookie_file):
            self.driver.get("https://www.instagram.com/")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            cookies = pickle.load(open(self.cookie_file, "rb"))
            for cookie in cookies:
                if "expiry" in cookie:
                    del cookie["expiry"]
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
                print(f"🔑 [{self.username}] تم تحميل الكوكيز وتسجيل الدخول تلقائياً.")
                return True
            except:
                print(f"⚠️ [{self.username}] فشل في التحقق من تسجيل الدخول بعد تحميل الكوكيز.")
                return False
        return False

   

    def login(self):
        self.driver.get("https://www.instagram.com/accounts/login/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password + Keys.ENTER)
    
        time.sleep(5)
    
        # ✅ تحقق مما إذا تم طلب كود التحقق الثنائي
        try:
            code_input = self.wait.until(
              EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Security Code' or @name='verificationCode' or @name='security_code']"))
                         )


            print(f"🔐 [{self.username}] تم طلب كود تحقق ثنائي. جاري توليد الرمز...")
    
            # 🔑 استخدم المفتاح السري لتوليد كود TOTP
            secret = get_secret_for_username(self.username)  # تأكد من حفظ secret في الكائن
            if not secret:
                print(f"⚠️ [{self.username}] لم يتم العثور على secret في ملف tokens.json")
                self.driver.quit()
                return False
                        
            # إزالة الفراغات
            secret = secret.replace(" ", "")
            
            try:
                totp = pyotp.TOTP(secret)
                code = totp.now()
                code_input.send_keys(code)
                code_input.send_keys(Keys.ENTER)
                print(f"✅ [{self.username}] تم إدخال كود التحقق تلقائيًا.")
                                # ✅ الموافقة على حفظ معلومات تسجيل الدخول إذا ظهرت

                try:
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save info')]"))).click()

                    print(f"💾 [{self.username}] تم الضغط على زر حفظ معلومات الدخول.")
                except Exception as e:
                    print(f"ℹ️ [{self.username}] لم يظهر زر حفظ المعلومات أو حدث خطأ: {e}")
                    pass
                try:
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))).click()
                except:
                    pass
            except Exception as e:
                print(f"⚠️ [{self.username}] فشل توليد الكود: {e}")
                return False
           
        except Exception as e:
            print(f"ℹ️ [{self.username}] لم يُطلب رمز تحقق ثنائي أو حدث خطأ: {e}")
    
        # التحقق إذا نجح تسجيل الدخول أو لا
        try:
            current_url = self.driver.current_url
            if "login" in current_url.lower():
                print(f"❌ [{self.username}] فشل تسجيل الدخول. سيتم إغلاق المتصفح.")
                time.sleep(2)
                self.driver.quit()
                return False
        except:
            pass
        try:
            time.sleep(2)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save info')]"))).click()
            time.sleep(2)
            # انتظر حتى يظهر عنصر مميز في الصفحة الرئيسية، مثلاً nav
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav")))
            print(f"✅ [{self.username}] تم تسجيل الدخول بنجاح، وصلت للصفحة الرئيسية.")
        except:
            print(f"❌ [{self.username}] لم يتم تسجيل الدخول، لم تظهر الصفحة الرئيسية.")
            self.driver.quit()
            return False
        # تجاوز نوافذ الحفظ والإشعارات
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save info')]"))).click()
        except:
            pass
    
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))).click()
        except:
            pass
    
        human_delay(1,3)
        self.save_cookies()
        self.driver.quit()
        return True
 

    def like_post(self,url, retries=1):
       
        self.driver.get(url)
        human_delay(2, 4)
        self.driver.execute_script("window.scrollBy(0, 300);")
        print(f"🔍 [{self.username}] البحث عن زر الإعجاب...")
        for attempt in range(retries):
            try:
                section_element = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "section.x6s0dn4.xrvj5dj.x1o61qjw")
                ))
                element = WebDriverWait(section_element, 3).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        ".//div[@role='button']//*[name()='svg'][@aria-label='Like' or @aria-label='أعجبني']/ancestor::div[@role='button']"
                    ))
                )
                aria_label = element.find_element(By.TAG_NAME, "svg").get_attribute("aria-label")
                if aria_label and aria_label.lower() in ["like", "أعجبني"]:
                    ActionChains(self.driver).move_to_element(element).perform()
                    human_delay(0.3, 0.7)
                    element.click()
                    CURRENT_OPERATION["number"]+=1
                    print(f"❤️ [{self.username}] تم الإعجاب بالمنشور.")
                    return
                elif aria_label and aria_label.lower() in ["unlike", "إلغاء الإعجاب"]:
                    print(f"ℹ️ [{self.username}] تم الإعجاب مسبقًا.")
                    return
                else:
                    print(f"⚠️ [{self.username}] حالة زر الإعجاب غير معروفة: {aria_label}")
            except Exception as e:
                print(f"❌ [{self.username}] خطأ في المحاولة {attempt + 1} للإعجاب: {e}")
            human_delay(2, 4)
        print(f"❌ [{self.username}] فشل في الإعجاب بعد {retries} محاولات.")

    def comment_on_post(self, comment_text, post_url):
     
     try:
        print(f"🔍 [{self.username}] الانتقال إلى المنشور للتعليق...")
        self.driver.get(post_url)
        time.sleep(2)
        self.driver.execute_script("window.scrollBy(0, 300);")

        print(f"💬 [{self.username}] البحث عن صندوق التعليق...")
        # إعادة البحث عن العنصر مباشرة قبل الاستخدام
        comment_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder="إضافة تعليق..."], textarea[placeholder="Add a comment…"]'))
        )
        comment_box.click()
        time.sleep(1)

        # إعادة البحث عن العنصر مرة أخرى لتجنب stale element
        comment_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder="إضافة تعليق..."], textarea[placeholder="Add a comment…"]'))
        )
        comment_box.send_keys(comment_text)
        comment_box.send_keys(Keys.ENTER)
        CURRENT_OPERATION["number"]+=1
        print(f"✅ [{self.username}] تم إرسال التعليق بنجاح.")
     except Exception as e:
        print(f"❌ [{self.username}] فشل في إرسال التعليق: {e}")


    def follow_user(self,user,array = ["follow", "متابعة"]):
        self.driver.get(f"https://www.instagram.com/{user}/")
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            human_delay(2, 4)
            buttons = self.driver.find_elements(By.XPATH, "//header//button")
            for button in buttons:
                label = button.text.strip().lower()
                if label in array:
                    button.click()
                    if button.click():
                      CURRENT_OPERATION["number"]+=1
                      print(f"➕ [{self.username}] تم متابعة الحساب: {user}")
                      time.sleep(2)
                    return
                elif label in ["following", "requested", "تم الطلب", "تمت المتابعة"]:
                    print(f"ℹ️ [{self.username}] الحساب متابع بالفعل أو تم إرسال طلب.")
                    return
            print(f"⚠️ [{self.username}] لم يتم العثور على زر مناسب للمتابعة.")
        except Exception as e:
            print(f"❌ [{self.username}] خطأ أثناء محاولة المتابعة: {e}")

    def unfollow_user(self, user, array=['following', 'اتابع', 'requested', 'تم الطلب']):
      try:
          self.driver.get(f"https://www.instagram.com/{user}/")
          self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
          human_delay(2, 4)
   
          # اضغط على زر Following
          buttons = self.driver.find_elements(By.XPATH, "//header//button")
          for button in buttons:
              label = button.text.strip().lower()
              if label in array:
                  print(f"🔘 الضغط على زر: {label}")
                  button.click()
                  human_delay(2, 3)
   
                  try:
                      # حدد div يحتوي على Unfollow كنص
                      unfollow_div = WebDriverWait(self.driver, 7).until(
                          EC.element_to_be_clickable((
                              By.XPATH,
                              "//div[@role='button']//span[text()='Unfollow' or text()='إلغاء المتابعة']/ancestor::div[@role='button']"
                          ))
                      )
                      unfollow_div.click()
                      print(f"🚫 [{self.username}] تم إلغاء متابعة الحساب: {user}")
                      return
                  except Exception as e:
                      print(f"⚠️ [{self.username}] لم يتم العثور على زر Unfollow داخل النافذة: {e}")
                      return
   
          print(f"⚠️ [{self.username}] لم يتم العثور على زر 'Following'.")
      except Exception as e:
          print(f"❌ [{self.username}] خطأ أثناء محاولة إلغاء المتابعة: {e}")
   
    
      
        
    def like_story(self,driver, username):
     try:
       
        # نجرب نبحث عن أزرار إعجاب ضمن عناصر تحتوي svg أو نصوص معروفة
        possible_selectors = [
            # زر يكون div أو button وله aria-label يحتوي Like أو أعجبني
            (By.XPATH, "//div[@role='button' and (contains(@aria-label, 'Like') or contains(@aria-label, 'أعجبني'))]"),
            (By.XPATH, "//button[contains(@aria-label, 'Like') or contains(@aria-label, 'أعجبني')]"),

            # svg يحمل aria-label
            (By.XPATH, "//*[name()='svg' and (contains(@aria-label, 'Like') or contains(@aria-label, 'أعجبني'))]/ancestor::div[@role='button']"),
            (By.XPATH, "//*[name()='svg' and (contains(@aria-label, 'Like') or contains(@aria-label, 'أعجبني'))]/ancestor::button"),

            # زر فيه نص "Like" أو "أعجبني"
            (By.XPATH, "//div[@role='button' and (contains(text(), 'Like') or contains(text(), 'أعجبني'))]"),
            (By.XPATH, "//button[contains(text(), 'Like') or contains(text(), 'أعجبني')]"),

        (By.XPATH, "//div[@role='button']//*[name()='svg'][@aria-label='أعجبني' or @aria-label='Like']/ancestor::div[@role='button']"),
            (By.XPATH, "//button//*[name()='svg'][@aria-label='أعجبني' or @aria-label='Like']/ancestor::button"),
            (By.XPATH, "//button[@aria-label='أعجبني' or @aria-label='Like']"),
            (By.XPATH, "//div[@role='button' and (@aria-label='أعجبني' or @aria-label='Like')]"),
            (By.XPATH, "//span//*[name()='svg'][@aria-label='أعجبني' or @aria-label='Like']/ancestor::button"),
            (By.XPATH, "//div//*[name()='svg'][@aria-label='أعجبني' or @aria-label='Like']/ancestor::button"),
            (By.XPATH, "//div[@role='button' and (contains(@aria-label, 'أعجبني') or contains(@aria-label, 'Like'))]"),
        ]

        found = False
        for by, selector in possible_selectors:
            try:
                like_btn = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                ActionChains(driver).move_to_element(like_btn).perform()
                time.sleep(0.3)
                like_btn.click()
                CURRENT_OPERATION["number"]+=1
                print(f"❤️ [{username}] تم الإعجاب بالستوري باستخدام المحدد: {selector}")
                found = True
                break
            except Exception:
                continue

        if not found:
            print(f"⚠️ [{username}] لم أتمكن من إيجاد زر الإعجاب في الستوري في كل الاحتمالات.")

     except Exception as e:
        print(f"⚠️ [{username}] حدث خطأ أثناء محاولة الإعجاب بالستوري: {e}")



     

    def reply_to_story(self, user, reply_text="Nice!"):
     
     driver=self.driver
     print(f"👁️ [{user}] محاولة الرد على قصة {user}")
     try:
        driver.get(f"https://www.instagram.com/{user}/")
        print('mmmmmmmmmmm')
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print('jjjjjjjjjj')

        # بحث مرن عن زر فتح الستوري
        story_selectors = [
            '//div[contains(@role,"link")]//img[contains(@alt, "Story")]',
            '//span[@role="link" and @tabindex="0"]/img',
            '//a[contains(@href,"/stories/")]',
            '//button[contains(@aria-label, "Story")]',
            '//div[contains(@aria-label, "Story")]',
            '//div[contains(@class, "story")]//img',
            'https://www.instagram.com/stories/'
        ]
        
        story_button = None
        for selector in story_selectors:
            try:
                print(f"🔍 [{user}] محاولة إيجاد زر فتح الستوري باستخدام المحدد: {selector}")
                story_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if story_button:
                    print(f"✅ [{user}] تم العثور على زر فتح الستوري.")
                    break
            except Exception as e:
                print(f"⚠️ [{user}] فشل في إيجاد زر الستوري بالمحدد {selector}: {e}")
                continue

        if not story_button:
            print(f"⚠️ [{user}] لم يتم العثور على زر فتح الستوري في كل الاحتمالات.")
            return False
        # self.driver.get(f"https://www.instagram.com/stories/{user}/")
         # فتح الستوري
        story_button.click()
       # الضغط على زر View story إن وُجد بعد فتح واجهة الستوري
        try:
           print("🔘 محاولة الضغط على زر View story...")
           view_story_btn = WebDriverWait(driver, 5).until(
              EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and (text()="View story" or text()="عرض القصة")]'))
         )
           view_story_btn.click()
           print("✅ تم الضغط على زر View story.")
           time.sleep(2)
        except Exception as e:
             print(f"ℹ️ لم يتم العثور على زر View story: {e}")

        
# تمرير لإظهار كل العناصر
        # ActionChains(driver).move_by_offset(0, 300).perform()
        # time.sleep(1)

        previous_story_id = ""

        reply_box_selectors = [
            '//textarea[starts-with(@placeholder, "رد على")]',
            '//textarea[contains(@placeholder, "Reply to")]',
            '//textarea[contains(@aria-label, "Reply to")]',
            '//textarea[contains(@class,"reply to")]',
            '//textarea[starts-with(@placeholder, "Reply")]',
                        '//textarea[contains(@placeholder, "Reply")]',
                        '//textarea[contains(@aria-label, "Reply")]',
        ]
        while True :

        
            sent_reply = False
            self.like_story(driver,user)
            reply_box = None
            for r_selector in reply_box_selectors:
                try:
                    print(f"🔍 [{user}] محاولة إيجاد مربع الرد باستخدام المحدد: {r_selector}")
                    reply_box = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, r_selector))
                )
                    if reply_box:
                         print(f"✅ [{user}] تم العثور على مربع الرد.")
                         ActionChains(driver).move_to_element(reply_box).click().perform()
                         reply_box.clear()
                         reply_box.send_keys(reply_text)
                        #  time.sleep(1)
                         reply_box.send_keys(Keys.ENTER)
                         print(f"✅ [{user}] تم إرسال الرد على الستوري.")
                         sent_reply=True

                    #like_story()
                         break
                except Exception as e:
                    print(f"⚠️ [{user}] فشل في إيجاد مربع الرد بالمحدد {r_selector}: {e}")
                    continue
            
            if not reply_box:
                print(f"⚠️ [{user}] لم أتمكن من إيجاد مربع الرد على الستوري.")
                return False
            

        # إرسال الرد
            try:
             print("➡️ الانتقال إلى القصة التالية...")
             ActionChains(driver).move_by_offset(300, 0).click().perform()
             ActionChains(driver).move_by_offset(-300, 0).perform()
             time.sleep(1.5)
            except:
             print("❌ لا توجد قصة تالية. إنهاء الحلقة.")
       #  break
             return True

     except Exception as e:
        print(f"❌ [{user}] فشل في الرد على الستوري: {e}")
       
        print(traceback.format_exc())
        return False
 
   

              
            
    def process(self):
    # بداية العملية
     if not self.load_cookies():
         self.login()
     human_delay(1, 2)

    #  self.like_post(PHOTO_URL_FOR_LIKE)
    #  human_delay(1, 3)

    #  self.comment_on_post(COMMENT_TEXT, PHOTO_URL_FOR_COMMENT)
    #  human_delay(1, 3)
     self.follow_user(ACCOUNT_TO_FOLLOW)
    # human_delay(1, 3)

     self.reply_to_story(ACCOUNT_TO_FOLLOW, REPLY_TEXT_ON_STORY)
    #  human_delay(1, 2)

     self.driver.quit()
     print(f"✅ انتهت المعالجة للحساب: {self.username}")
    
    

        


    
            
   
    def monitor_watchlist_stories_and_posts(self,story_username=None, comment_text=" رائع!", story_reply="رهيب!", delay=4, delay_between_cycles=1 ,):
    # print(f"🚀 بدء المراقبة للحساب: {self.username}") 
    #  while True:
        #  if stop_flag:
        #       print(f"🛑 تم إيقاف المراقبة بناءً على الطلب. في انتظار انتهاء المهمة الحالية...")
        #       break  # هذا يوقف الحلقة الكبيرة لكن يسمح بإنهاء ما يجري أولاً

        #  if hasattr(self, "driver"):
        #   try:
        #       self.driver.quit()
        #   except Exception:
        #       pass
        #  print('fwewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        

        #  time.sleep(delay_between_cycles)  # ⏳ الانتظار بين الدورات
         
 # حلقة التكرار الكاملة
        #  if not self.driver:
        #     self.driver = webdriver.Chrome(options=self.options)
        #     if not self.load_cookies():
        #         self.login()
        #  open_browsers.append(self.driver)
         
        #  print(f"📡 [{self.username}] بدء دورة جديدة لمراقبة الحسابات...")

         watchlist=[story_username]
         
         last_post_ids = {}
         last_story_timestamps = {}
    
             
         def get_last_post_info(user, max_items=5):
             try:
                profile_url = f"https://www.instagram.com/{user}/"
                self.driver.get(profile_url)
                print(f"📥 فتح صفحة المستخدم: {profile_url}")
         
                time.sleep(3)  # تأخير بسيط لتحميل الصفحة
         
                # جلب روابط المنشورات فقط (بدون عناصر WebElement)
                post_links = [elem.get_attribute("href") for elem in self.driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')][:max_items]
                reel_links = [elem.get_attribute("href") for elem in self.driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')][:max_items]
         
                def get_timestamp(url):
                    if not url:
                        return None
                    self.driver.get(url)
                    try:
                        time_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "time"))
                        )
                        return time_element.get_attribute("datetime")
                    except:
                        print(f"⚠️ لم يتم العثور على عنصر الوقت في الصفحة: {url}")
                        return None
         
                posts = []
                for link in post_links:
                    timestamp = get_timestamp(link)
                    posts.append({"url": link, "timestamp": timestamp})
         
                reels = []
                for link in reel_links:
                    timestamp = get_timestamp(link)
                    reels.append({"url": link, "timestamp": timestamp})
         
                # فرز حسب التاريخ (تنازلي)
                posts_sorted = sorted(posts, key=lambda x: x['timestamp'] or '', reverse=True)
                reels_sorted = sorted(reels, key=lambda x: x['timestamp'] or '', reverse=True)
         
                latest_post = posts_sorted[0] if posts_sorted else None
                latest_reel = reels_sorted[0] if reels_sorted else None
         
                return {
                    "latest_post": latest_post,
                    "latest_reel": latest_reel
                }
         
             except Exception as e:
                 print(f"❌ خطأ أثناء استخراج معلومات المستخدم: {e}")
                 return None
         
         LAST_SEEN_FILE = os.path.join(BASE_DIR, "account", "last_seen_posts.json")
         
         def save_last_seen_post(username, post_type, url, timestamp):
             data = {}
             if os.path.exists(LAST_SEEN_FILE):
                 with open(LAST_SEEN_FILE, "r", encoding="utf-8") as f:
                     try:
                         data = json.load(f)
                     except:
                         data = {}
         
             data[username] = data.get(username, {})
             data[username][post_type] = {
                 "url": url,
                 "timestamp": timestamp
             }
         
             with open(LAST_SEEN_FILE, "w", encoding="utf-8") as f:
                 json.dump(data, f, ensure_ascii=False, indent=4)
           
         def get_saved_post_info(username, post_type):
           if not os.path.exists(LAST_SEEN_FILE):
               return None
           with open(LAST_SEEN_FILE, "r", encoding="utf-8") as f:
               try:
                   data = json.load(f)
                   return data.get(username, {}).get(post_type)
               except:
                   return None
       
          
        
        
             
             
         def get_last_story_timestamp(user):
           try:
              # الضغط على زر بدء مشاهدة الستوري إن وُجد
              self.driver.get(f"https://www.instagram.com/stories/{user}/")
              time.sleep(3)

# الضغط على زر بدء الستوري
              try:
                 print("🔘 محاولة الضغط على زر View story...")
                 view_story_btn = WebDriverWait(self.driver, 5).until(
                     EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and (text()="View story" or text()="عرض القصة")]'))
                 )
                 view_story_btn.click()
                 print("✅ تم الضغط على الزر، سيتم عرض الستوري الآن.")
                 time.sleep(2)
              except Exception as e:
                print(f"⚠️ تعذر العثور على زر View story: {e}")

        # نحاول التقاط عنصر <time>
              try:
                time_element = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.TAG_NAME, "time"))
                )
                timestamp = time_element.get_attribute("datetime")
                print(f"⏱️ [{user}] التاريخ المستخرج من الستوري: {timestamp}")

                return timestamp
              except Exception as e:
                print(f"⚠️ [{user}] لم يظهر عنصر <time> بعد عرض الستوري: {e}")
                return None

          
           except Exception as e:
             print(f"⚠️ خطأ في جلب ستوري {user}: {e}")
             return None


       
         for _ in range(1):  # راقب 3 مرات فقط ضمن هذه الدورة
             for user in watchlist:
                                  # داخل for user in watchlist:
                 story_new = False
                 post_new = False
                 post_data = None
                 
                 # فحص المنشور
                 info = get_last_post_info(user)
                 if info:
                     latest_post = info.get("latest_post")
                     latest_reel = info.get("latest_reel")
                 
                     def parse_time(ts):
                         try:
                             return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
                         except:
                             return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                 
                     post_time = parse_time(latest_post["timestamp"]) if latest_post and latest_post["timestamp"] else None
                     reel_time = parse_time(latest_reel["timestamp"]) if latest_reel and latest_reel["timestamp"] else None
                 
                     if post_time and (not reel_time or post_time > reel_time):
                         chosen = ("latest_post", latest_post)
                     elif reel_time:
                         chosen = ("latest_reel", latest_reel)
                     else:
                         chosen = None
                 
                     if chosen:
                         post_type, data = chosen
                         saved = get_saved_post_info(user, post_type)
                 
                         if not saved or saved["timestamp"] != data["timestamp"]:
                             post_new = True
                             post_data = (data["url"], data["timestamp"])
                             save_last_seen_post(user, post_type, data["url"], data["timestamp"])
                 
                
                 
                
                 if post_new :
                     print(f"🚀 [{user}] بدء التفاعل على {'المنشور' if post_new else ''} {'و' if post_new and story_new else ''} {'الستوري' if story_new else ''}")
                    
                    
                    
                     PENDING_TASKS.append({
                    "action": "post",
                    "username": user,
                    "post_url": post_data[0] if post_new else None,
                   
                })
                                      
                                  
                 new_story_timestamp = get_last_story_timestamp(user)

                 if new_story_timestamp:
                  print(f"🔎 [{user}] مقارنة التاريخ الجديد: {new_story_timestamp} مع القديم: {last_story_timestamps.get(user)}")
                
                  # إذا لم يتم التفاعل مع هذه القصة بعد (حتى لو لم يتغير التاريخ)
                  if last_story_timestamps.get(user) != new_story_timestamp:
                      print(f"🆕 [{user}] قصة جديدة (أو لم يتم التفاعل معها بعد).")
                    #   self.trigger_all_accounts_actions(story_username=user, story_reply=story_reply)
                      PENDING_TASKS.append({
                    "action": "story",
                    "username": user,
                    "story_usernamea": user,
                   
                })
                      last_story_timestamps[user] = new_story_timestamp
                      if stop_flag:
                          print("🛑 [المراقبة] توقف بناء على طلب المستخدم.")
                          break

                  else:
                      print(f"ℹ️ [{user}] لا توجد قصة جديدة.")
                


           





    def trigger_all_accounts_actions(self):
      if not PENDING_TASKS:  # إذا لم يكن هناك مهام في الانتظار
          print("ℹ️ لا توجد مهام للتنفيذ.")
          return
      with self.trigger_lock:
          try:
              with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                  accounts = json.load(f)
          except Exception as e:
              print(f"⚠️ خطأ في تحميل الحسابات: {e}")
              return
          CURRENT_OPERATION["active"] = True
          CURRENT_OPERATION["completed"] = 0
          CURRENT_OPERATION["total"] = len(accounts)

          def task(acc):
              
              with thread_limiter:
                  account = None
                  try:
                      
                      print(f"🚀 بدء تفاعل الحساب: {acc['username']}")
                      account = process_account(acc["username"], acc["password"])
                      
                      if not account.load_cookies():
                          account.login()
                      
                      for task in PENDING_TASKS:
                         if task["action"] == "story":
                             # التفاعل مع الستوري
                             print(f"🚀 بدء التفاعل على ستوري [@{task['username']}]")
                             CURRENT_OPERATION["name"] = f"{task['story_usernamea']}التفاعل التلقائي علي الحساب"
                             account.reply_to_story(task['story_usernamea'],random.choice(COMMENT_LIST))
             
                         if task["action"] == "post":
                             # التفاعل مع المنشور
                             print(f"🚀 بدء التفاعل على منشور [@{task['username']}]")
                             CURRENT_OPERATION["name"] = f"{task['username']}التفاعل التلقائي علي الحساب"
                             account.like_post(task['post_url'])
                             
                             account.comment_on_post(random.choice(COMMENT_LIST), task['post_url'])

                     
                      CURRENT_OPERATION["completed"] += 1
                  except Exception as e:
                      print(f"❌ [{acc['username']}] خطأ أثناء تنفيذ المهام: {e}")
                  finally:
                      try:
                          if hasattr(account, 'driver') and account.driver:
                              account.driver.quit()
                              print(f"🛑 [{acc['username']}] تم إغلاق المتصفح.")
                          else:
                              print(f"⚠️ حساب [{acc['username']}] ليس لديه كائن driver.")
                          
                      except Exception as e:
                          print(f"⚠️ تعذر إغلاق المتصفح للحساب {acc['username']}: {e}")

          threads = []
          for acc in accounts:
              t = threading.Thread(target=task, args=(acc,))
              t.daemon = True
              t.start()
              threads.append(t)

          for t in threads:
              t.join()
          CURRENT_OPERATION["active"] = False

    
    
# تحديد الحد الأقصى لعدد الخيوط المتوازية، على سبيل المثال: إذا كنت ترغب في مراقبة 5 حسابات في وقت واحد

# تعديل دالة start_monitoring

async def start_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("monitoring_started"):
        await update.message.reply_text("⚠️ المراقبة تعمل بالفعل.")
        return CHOOSING
    while True :
        accounts = context.user_data.get("ACCOUNTS") or load_accounts()
        watchlist_users = load_accounts1(file_path=WATCHLIST)
        monitoring_started = False
    
        # نربط كل حساب مراقب بحساب مراقِب (واحد فقط)
        pairs = zip(watchlist_users, accounts)
        acc_objs = []
        def monitor_task(acc, watch_username):
            with thread_limiter:
                try:
                    acc_obj = process_account(acc["username"], acc["password"])
                    acc_objs.append(acc_obj) 
    
                    if not acc_obj.load_cookies():
                        acc_obj.login()
    
                    acc_obj.monitor_watchlist_stories_and_posts(
                        story_username=watch_username
                    )
    
                except Exception as e:
                    print(f"❌ [{acc['username']}] فشل في تشغيل المراقبة لـ [{watch_username}]: {e}")
        
        threads = []
        for watch_username, acc in pairs:
            try:
                t = threading.Thread(target=monitor_task, args=(acc, watch_username), daemon=True)
                t.start()
                threads.append(t)
                await update.message.reply_text(f"✅ [{acc['username']}] يراقب [{watch_username}].")
                monitoring_started = True
            except Exception as e:
                await update.message.reply_text(f"❌ [{acc['username']}] فشل في إعداد المراقبة: {e}")
    
        if monitoring_started:
            context.user_data["monitoring_started"] = True
    
            # انتظر جميع الخيوط حتى تكتمل
            for t in threads:
                t.join()
            
           
            for acc_obj in acc_objs:
                try:
                    if hasattr(acc_obj, 'driver') and acc_obj.driver:
                        acc_obj.driver.quit()  # إغلاق المتصفح
                        print(f"🛑 تم إغلاق المتصفح للحساب {acc_obj.username}.")
                except Exception as e:
                    print(f"⚠️ فشل في إغلاق المتصفح للحساب {acc_obj.username}: {e}")
            # بعد الانتهاء من جميع الخيوط، نفذ المهام
            x=0
            for acc_obj in acc_objs:
                if (x<=1) :
                  acc_obj.trigger_all_accounts_actions() 
                  x+=1
                break 
    
            
        else:
            await update.message.reply_text("❌ لم تنجح المراقبة لأي حساب.")

            return CHOOSING
        time.sleep(86400) 
        await update.message.reply_text("بدا الدوره الثانيه")




    

# دالة لإغلاق جميع المتصفحات المفتوحة
def close_all_browsers():
    for driver in open_browsers:
        try:
            driver.quit()  # إغلاق المتصفح
        except Exception as e:
            print(f"⚠️ فشل في إغلاق المتصفح: {e}")
    open_browsers.clear()  # مسح القائمة بعد الإغلاق

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag
    stop_flag = True
    print("🛑 تم استدعاء دالة STOP")  # ← لتأكيد التنفيذ
    await update.message.reply_text("🛑 تم إيقاف المراقبة وإغلاق المتصفحات.")
    close_all_browsers()







def add_users_to_watchlist():
    watchlist_file = WATCHLIST
    
    # قراءة القائمة الحالية أو إنشاء قائمة جديدة
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r", encoding="utf-8") as f:
            try:
                watchlist = json.load(f)
                if not isinstance(watchlist, list):
                    watchlist = []
            except json.JSONDecodeError:
                watchlist = []
    else:
        watchlist = []

    print("📥 أدخل أسماء المستخدمين للمراقبة (واحدًا تلو الآخر). اكتب 'done' لإنهاء الإدخال:")

    while True:
        user = input("> ").strip()
        if user.lower() == "done":
            break
        if user and user not in watchlist:
            watchlist.append(user)
            print(f"✅ تم إضافة المستخدم '{user}' إلى قائمة المراقبة.")
        else:
            print("⚠️ المستخدم فارغ أو مكرر، حاول مرة أخرى.")

    # حفظ القائمة بعد التعديل
    with open(watchlist_file, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)

    print(f"✅ تم تحديث قائمة المراقبة. إجمالي المستخدمين في القائمة: {len(watchlist)}")
  

TOKEN = "7579140710:AAHvLK8dh6hMCL6fxdtRlQMxhActky6WYV8"

CHOOSING, TYPING_ACCOUNTS, WATCHLIST_OPTIONS, TYPING_WATCH_USERNAME = range(4)

# # تحميل الحسابات من الملف
# def load_accounts():
#     file_path = ACCOUNTS_FILE
#     if os.path.exists(file_path):
#         with open(file_path, "r", encoding="utf-8") as f:
#             try:
#                 return json.load(f)
#             except json.JSONDecodeError:
#                 return []
#     return []
 
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
     # ← استدع القاموس

    if CURRENT_OPERATION["active"]:
        await update.message.reply_text("🟢 البوت يعمل حالياً ويوجد عمليات نشطة.")
        await update.message.reply_text(
            f"🔄 العملية الحالية: {CURRENT_OPERATION['name']}\n"
            f"📊 الحسابات المنفذة: {CURRENT_OPERATION['completed']} من {CURRENT_OPERATION['total']}"
        )
    else:
        

        await update.message.reply_text("🔴 لا توجد عملية نشطة حاليًا.")
        await update.message.reply_text("العمليه التي تم تنفيذها مسبقا"
            f"🔄 العملية السابقه: {CURRENT_OPERATION['name']}\n"
            f"📊 الحسابات المنفذة: {CURRENT_OPERATION['completed']} من {CURRENT_OPERATION['total']}"
             f"🔄  الحسابات الفعليه التي قامت بي العمليه: {CURRENT_OPERATION['number']}\n"
        )


from telegram import ReplyKeyboardMarkup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user_id = update.effective_user.id
    # if 
    # await update.message.reply_text(
    #     f"مرحبًا! 👋\n"
    #     f"معرفك: `{user_id}`\n"
    #     ,
    #     parse_mode="Markdown")
    global COMMENT_LIST
    COMMENT_LIST=load_comments_from_file()
    context.user_data["ACCOUNTS"] = load_accounts()
    global stop_flag 
    stop_flag = False
   
    keyboard = [  [ "لمعرفه انه البوت قيد التشغيل /status \n لي اعاده تشغيل البوت /restart \n للذهاب للعددات /setting ",],

                
        ["1️⃣اضهار عدد الحسابات ", "2️⃣ إدخال الحسابات"],
        ["5️⃣: فحص الحسابات\n"],
        ["4\ufe0f\u20e3 اختيار العمليات علي الحساب يدويًا\n", "9️⃣ التفاعل التلقائي مع المستخدمين"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True,one_time_keyboard=False)

    await update.message.reply_text(
        "🎛️ اختر ما تريد تنفيذه:",
       


        reply_markup=reply_markup
    )
    return CHOOSING

import asyncio
from concurrent.futures import ThreadPoolExecutor
bot_objects = []

async def check_single_account(acc):
    loop = asyncio.get_running_loop()

    def blocking_check():
     with thread_limiter:
        if not acc.get("username") or not acc.get("password"):
            return ("failed", acc)

        obj = None
        try:
            obj = process_account(acc["username"], acc["password"])
            load_cookies_result = obj.load_cookies()
            print(f"[{acc['username']}] load_cookies returned: {load_cookies_result}")
            login_result = False
            if not load_cookies_result:
                login_result = obj.login()
                print(f"[{acc['username']}] login returned: {login_result}")

            success = load_cookies_result or login_result
            return ("working" if success else "failed", acc)
        except Exception as e:
            print(f"[{acc['username']}] Exception during check: {e}")
            return ("failed", acc)
        finally:
            if obj:
                try:
                    obj.driver.quit()
                except:
                    pass

                try:
                    bot_objects.remove(obj)
                except ValueError:
                    pass


    result = await loop.run_in_executor(None, blocking_check)
    backup_all_data()
    return result


import shutil
import shutil
import os

def backup_all_data():
    backup_dir = os.path.join(BASE_DIR, "backup")

    try:
        os.makedirs(backup_dir, exist_ok=True)

        # نسخ ملف الحسابات
        shutil.copy(ACCOUNTS_FILE, os.path.join(backup_dir, "accounts.json"))
        print(f"✅ تم نسخ accounts.json إلى {backup_dir}")

        # نسخ ملفات الكوكيز
        cookies_src = os.path.join(BASE_DIR, "cookies")
        cookies_dst = os.path.join(backup_dir, "cookies")

        if os.path.exists(cookies_src):
            os.makedirs(cookies_dst, exist_ok=True)

            for filename in os.listdir(cookies_src):
                src_file = os.path.join(cookies_src, filename)
                dst_file = os.path.join(cookies_dst, filename)
                shutil.copy2(src_file, dst_file)
                print(f"📁 تم نسخ ملف الكوكيز: {filename}")
        else:
            print("⚠️ مجلد الكوكيز غير موجود.")
    except Exception as e:
        print(f"❌ فشل النسخ الاحتياطي: {e}")



import glob

async def restore_accounts_from_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
   
    backup_dir = os.path.join(BASE_DIR, "backup")

    try:
        # استرجاع ملف الحسابات
        backup_accounts = os.path.join(backup_dir, "accounts.json")
        if os.path.exists(backup_accounts):
            shutil.copy(backup_accounts, ACCOUNTS_FILE)
            print(f"✅ تم استرجاع accounts.json من النسخة الاحتياطية.")
        else:
            print("⚠️ لم يتم العثور على accounts.json في النسخة الاحتياطية.")

        # استرجاع ملفات الكوكيز دون حذف المجلد الأصلي
        backup_cookies = os.path.join(backup_dir, "cookies")
        cookies_dir = os.path.join(BASE_DIR, "cookies")

        if os.path.exists(backup_cookies):
            os.makedirs(cookies_dir, exist_ok=True)

            for filename in os.listdir(backup_cookies):
                src_file = os.path.join(backup_cookies, filename)
                dst_file = os.path.join(cookies_dir, filename)

                # نسخ أو استبدال كل ملف كوكيز
                shutil.copy(src_file, dst_file)
                print(f"📁 تم استرجاع ملف الكوكيز: {filename}")
        else:
            print("⚠️ لم يتم العثور على مجلد cookies في النسخة الاحتياطية.")
    except Exception as e:
        print(f"❌ فشل في استرجاع النسخة الاحتياطية: {e}")


async def check_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CURRENT_OPERATION["name"] = "فحص الحسابات"
    CURRENT_OPERATION["active"] = True
    CURRENT_OPERATION["completed"] = 0
    # CURRENT_OPERATION["total"] = len(accounts)

    if context.user_data.get("is_running"):
        await update.message.reply_text("⚠️ هناك عملية قيد التنفيذ. انتظر انتهاءها أو أرسل 'إلغاء' لإيقافها.")
        return CHOOSING
    context.user_data["is_running"] = True

    if not os.path.exists(ACCOUNTS_FILE):
        await update.message.reply_text("⚠️ لا يوجد ملف الحسابات.")
        context.user_data["is_running"] = False
        return CHOOSING
    
    accounts = context.user_data.get("ACCOUNTS")

    if not accounts:
       if not os.path.exists(ACCOUNTS_FILE):
           await update.message.reply_text("⚠️ لا يوجد ملف الحسابات.")
           context.user_data["is_running"] = False
           return CHOOSING
    
       with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
           accounts = json.load(f)
    

    working = []
    failed = []
   
    # استخدم ThreadPoolExecutor بحد 5 ثريدات
    executor = ThreadPoolExecutor(max_workers=5)
    loop = asyncio.get_running_loop()
    accounts = [acc for acc in accounts if acc.get("username") and acc.get("password")]

    if not accounts:
     await update.message.reply_text("⚠️ لا توجد حسابات صالحة في الملف.")
     context.user_data["is_running"] = False
     return CHOOSING


    # لكن لأن process_account يحتاج تحقق login, أستخدم دالة async مع run_in_executor
    # نعيد كتابة بشكل صحيح:
    tasks = [check_single_account(acc) for acc in accounts]

    results = await asyncio.gather(*tasks)

    for status, acc in results:
        if status == "working":
            working.append(acc)
        else:
            failed.append(acc)
        CURRENT_OPERATION["completed"] += 1 

    # حفظ الحسابات الفاشلة
    with open(FAILED_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(failed, f, indent=4, ensure_ascii=False)

    # حفظ الحسابات التي نجحت
        # حفظ الحسابات التي نجحت
    if "ACCOUNTS" in context.user_data:
        # ➕ دمج مع الحسابات القديمة إن وجدت
        existing_accounts = []
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                try:
                    existing_accounts = json.load(f)
                except:
                    existing_accounts = []
    
        # إزالة التكرار بناءً على username
        usernames = {acc["username"]: acc for acc in existing_accounts}
        for acc in working:
            usernames[acc["username"]] = acc  # سيستبدل القديم إن وُجد
    
        merged_accounts = list(usernames.values())
    
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(merged_accounts, f, indent=4, ensure_ascii=False)
    
    else:
        # ⛔ لم تأتِ من check_by_usernames → استبدال الملف كالمعتاد
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(working, f, indent=4, ensure_ascii=False)


    if failed:
        context.user_data["awaiting_change_password_decision"] = True
        usernames = [acc["username"] for acc in failed]
        usernames_list = "\n".join(f"• {u}" for u in usernames)
        await update.message.reply_text(
            f"✅ تم فحص الحسابات:\n"
            f"✔️ صالحة: {len(working)}\n"
            f"❌ غير صالحة: {len(failed)} (تم نقلهم)\n\n"
            f"📛 الحسابات الفاشلة:\n{usernames_list}\n\n"
            "هل ترغب في تغيير كلمة المرور لأحد هذه الحسابات؟\n"
            "🟢 أرسل 'نعم' للمتابعة أو 'لا' لتجاهل."
        )
    else:
        await update.message.reply_text(
            f"✅ تم فحص الحسابات:\n✔️ كل الحسابات صالحة!", reply_markup=get_main_menu_keyboard()
        )
    CURRENT_OPERATION["active"] = False
    context.user_data["is_running"] = False
    executor.shutdown(wait=False)
    return CHOOSING



async def change_failed_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["changing_multiple_passwords"] = True
    context.user_data["updated_failed_accounts"] = []
    await update.message.reply_text("✏️ أرسل الحسابات الجديدة بهذا الشكل:\n`username:newpassword`\n\n🟢 أرسل 'done' عند الانتهاء.", parse_mode=ParseMode.MARKDOWN)


async def recheck_failed_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not os.path.exists(FAILED_ACCOUNTS_FILE):
        await update.message.reply_text("📭 لا يوجد حسابات فاشلة.")
        return

    with open(FAILED_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        failed = json.load(f)

    recovered = []
    still_failed = []

    for acc in failed:
        try:
            with thread_limiter:
                obj = process_account(acc["username"], acc["password"])
                if obj.load_cookies() or obj.login():
                    recovered.append(acc)
                else:
                    still_failed.append(acc)
                obj.driver.quit()
        except Exception:
            still_failed.append(acc)


    # أضف الناجحين إلى الحسابات
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            current_accounts = json.load(f)
    else:
        current_accounts = []

    current_accounts.extend(recovered)

    # حفظ النتائج
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_accounts, f, indent=4, ensure_ascii=False)

    with open(FAILED_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(still_failed, f, indent=4, ensure_ascii=False)

    await update.message.reply_text(f"🔁 تم الفحص:\n"
                                    f"✔️ تم استعادة: {len(recovered)}\n"
                                    f"❌ ما زال فاشل: {len(still_failed)}", reply_markup=get_main_menu_keyboard())

async def reset_is_running(context):
    context.user_data["is_running"] = False


async def set_like_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("is_running"):
        await update.message.reply_text("⚠️ توجد عملية قيد التنفيذ حاليًا. يرجى الانتظار أو أرسل 'إلغاء' لإيقافها.")
        if update.effective_chat.id not in waiting_users:
            waiting_users.append(update.effective_chat.id)
        return CHOOSING

    context.user_data["is_running"] = True
    count = int(update.message.text.strip())
    sub_choice = context.user_data.get("sub_choice")
    accounts = context.user_data.get("ACCOUNTS") or load_accounts()
    max_accounts = min(count, len(accounts))

    await update.message.reply_text(f"🔍 عدد الحسابات المستخدمة: {max_accounts}")

    
    CURRENT_OPERATION["active"] = True
    CURRENT_OPERATION["completed"] = 0
    CURRENT_OPERATION["total"] = max_accounts
    def run_task(task_type):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        def worker(acc, action):
            with thread_limiter:
                try:
                    print(f"🚀 [{acc['username']}] بدء تنفيذ: {action}")
                    obj = process_account(acc["username"], acc["password"])
                    if not obj.load_cookies():
                        obj.login()
                   
                    if action == "like":
                        obj.like_post(context.user_data["PHOTO_URL_FOR_LIKE"])
                    elif action == "reply":
                        print(context.user_data["STORY_USER"])
                        obj.reply_to_story(context.user_data["STORY_USER"],random.choice(COMMENT_LIST))
        
                    obj.driver.quit()
                    print(f"✅ [{acc['username']}] تم تنفيذ {action}.")
                    CURRENT_OPERATION["completed"] += 1 
                except Exception as e:
                    print(f"❌ [{acc['username']}] خطأ أثناء تنفيذ {action}: {e}")
        

        threads = []
        for i, acc in enumerate(accounts[:max_accounts]):
            t = threading.Thread(target=worker, args=(acc, task_type), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        CURRENT_OPERATION["active"] = False
        print("✅ تم الانتهاء من جميع الخيوط.")
        asyncio.run_coroutine_threadsafe(
            update.message.reply_text("✅ تم الانتهاء من العملية.", reply_markup=get_main_menu_keyboard()),
            loop
        )
        for user_id in waiting_users:
            asyncio.run_coroutine_threadsafe(
                context.bot.send_message(
                    chat_id=user_id,
                    text="✅ تم الانتهاء من العملية التي كنت تنتظرها.",
                    reply_markup=get_main_menu_keyboard()
                ),
                loop
            )

        # ✅ إعادة is_running إلى False وتنظيف القائمة
        waiting_users.clear()
        loop.run_until_complete(reset_is_running(context))
        loop.close()

    if sub_choice == "like_only":
        await update.message.reply_text("🚀 جاري تنفيذ الإعجابات...",reply_markup=get_main_menu_keyboard())
        threading.Thread(target=run_task, args=("like",)).start()
        CURRENT_OPERATION["name"] = "ارسال لايكات قيد التشغيل"

    elif sub_choice == "story_reply_only":
        await update.message.reply_text("🚀 جاري تنفيذ الرد على الستوري...",reply_markup=get_main_menu_keyboard())
        threading.Thread(target=run_task, args=("reply",)).start()
        CURRENT_OPERATION["name"] = "الرد علي القصه قيد التشغيل"

    return CHOOSING


async def set_comments_per_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("is_running"):
        await update.message.reply_text("⚠️ توجد عملية قيد التنفيذ حاليًا. يرجى الانتظار أو أرسل 'إلغاء' لإيقافها.")
        if update.effective_chat.id not in waiting_users:
            waiting_users.append(update.effective_chat.id)
        return CHOOSING

    try:
        comments_per = int(update.message.text.strip())
        context.user_data["comments_per_account"] = comments_per
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح لعدد التعليقات.")
        return CHOOSING

    context.user_data["is_running"] = True
    await update.message.reply_text("✅ تم حفظ عدد التعليقات لكل حساب.")

    accounts = context.user_data.get("ACCOUNTS") or load_accounts()
    # comment_text = random.choice(COMMENT_LIST)
    post_url = context.user_data.get("PHOTO_URL_FOR_COMMENT")
    total_accounts = context.user_data.get("max_commenters", 5)

    if not post_url:
        context.user_data["is_running"] = False
        await update.message.reply_text("❌ تأكد من إدخال رابط المنشور أولاً.")
        return CHOOSING

    await update.message.reply_text("🚀 جاري تنفيذ التعليقات...",reply_markup=get_main_menu_keyboard())
    CURRENT_OPERATION["name"] = "تنفيذ التعليقات قيد التشغيل"
    CURRENT_OPERATION["active"] = True
    CURRENT_OPERATION["completed"] = 0
    CURRENT_OPERATION["total"] = total_accounts
        # تشغيل المهمة في خيط منفصل
    def run_comments():
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        def worker(acc):
            with thread_limiter:
                try:
                    print(f"💬 [{acc['username']}] بدء تنفيذ التعليق...")
                    obj = process_account(acc["username"], acc["password"])
                    if not obj.load_cookies():
                        obj.login()
                   
                    for _ in range(comments_per):
                        comment_text = random.choice(COMMENT_LIST) if COMMENT_LIST else "روووعه"
                        obj.comment_on_post(comment_text, post_url)
                    obj.driver.quit()
                    print(f"✅ [{acc['username']}] تم تنفيذ التعليقات.")
                    CURRENT_OPERATION["completed"] += 1
                except Exception as e:
                    print(f"❌ [{acc['username']}] خطأ أثناء تنفيذ التعليق: {e}")

        threads = []
        for acc in accounts[:total_accounts]:
            t = threading.Thread(target=worker, args=(acc,), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        CURRENT_OPERATION["active"] = False
        print("✅ تم الانتهاء من جميع التعليقات.")

        asyncio.run_coroutine_threadsafe(
            update.message.reply_text("✅ تم الانتهاء من التعليقات.", reply_markup=get_main_menu_keyboard()),
            loop
        )
        for user_id in waiting_users:
            asyncio.run_coroutine_threadsafe(
                context.bot.send_message(
                    chat_id=user_id,
                    text="✅ تم الانتهاء من العملية التي كنت تنتظرها.",
                    reply_markup=get_main_menu_keyboard()
                ),
                loop
            )

        # ✅ إعادة is_running إلى False وتنظيف القائمة
        waiting_users.clear()
        loop.run_until_complete(reset_is_running(context))
        loop.close()

    threading.Thread(target=run_comments).start()

    return CHOOSING

async def set_follow_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if context.user_data.get("is_running"):
        await update.message.reply_text("⚠️ توجد عملية قيد التنفيذ حاليًا. يرجى الانتظار أو أرسل 'إلغاء' لإيقافها.")
        if update.effective_chat.id not in waiting_users:
            waiting_users.append(update.effective_chat.id)
        return CHOOSING

    context.user_data["is_running"] = True
    
    try:
        count = int(update.message.text.strip())
    except ValueError:
        context.user_data["is_running"] = False
        await update.message.reply_text("❌ الرجاء إدخال عدد صحيح.")
        return CHOOSING

    await update.message.reply_text("🚀 جاري تنفيذ المتابعة...", reply_markup=get_main_menu_keyboard())
    
   
    CURRENT_OPERATION["name"] = "المتابعه قيد التشغيل"
    CURRENT_OPERATION["active"] = True
    CURRENT_OPERATION["completed"] = 0

    
    accounts = context.user_data.get("ACCOUNTS") or load_accounts()
    username_to_follow = context.user_data.get("ACCOUNT_TO_FOLLOW")
    CURRENT_OPERATION["total"] = len(accounts)
    if not username_to_follow:
        context.user_data["is_running"] = False
        await update.message.reply_text("❌ يرجى تحديد اسم الحساب الذي تريد متابعته أولًا.")
        return CHOOSING

    def run_followers():
        # إنشاء event loop خاص بالخيط
        # asyncio.set_event_loop(asyncio.new_event_loop())
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        chat_id = update.effective_chat.id  # ✅ نحفظ chat_id لاستخدامه لاحقًا

       

        def worker(acc):
            with thread_limiter:
                try:
                    print(f"👤 [{acc['username']}] بدء تنفيذ المتابعة...")
                    obj = process_account(acc["username"], acc["password"])
                    if not obj.load_cookies():
                        obj.login()
                   
                    obj.follow_user(username_to_follow)
                    obj.driver.quit()
                    print(f"✅ [{acc['username']}] تم تنفيذ المتابعة.")
                    CURRENT_OPERATION["completed"] += 1 
                except Exception as e:
                    print(f"❌ [{acc['username']}] خطأ أثناء تنفيذ المتابعة: {e}")

        threads = []
        for acc in accounts[:count]:
            t = threading.Thread(target=worker, args=(acc,), daemon=True)
            t.start()
            threads.append(t)

        # انتظار كل الخيوط
        for t in threads:
            t.join()
      
        print("✅ تم الانتهاء من جميع عمليات المتابعة.")
        CURRENT_OPERATION["active"] = False
        try:
          future = asyncio.run_coroutine_threadsafe(
              context.bot.send_message(
                  chat_id=chat_id,
                  text="✅ تم الانتهاء من جميع عمليات المتابعة.",
                  reply_markup=get_main_menu_keyboard()
              ),
              loop
          )
          future.result(timeout=5)
        except Exception as e:
          print(f"⚠️ فشل في إرسال رسالة المتابعة: {e}")
        
        waiting_users.clear()
        loop.run_until_complete(reset_is_running(context))
        loop.close()
        return
    
    threading.Thread(target=run_followers).start()
    
    
    

    return CHOOSING




async def check_by_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower() == "done":
        usernames = context.user_data.get("usernames_to_check", [])
        if not usernames:
            await update.message.reply_text("⚠️ لم يتم إدخال أي اسم مستخدم.")
            return CHOOSING

        if not os.path.exists(ACCOUNTS_FILE):
            await update.message.reply_text("⚠️ لا يوجد ملف حسابات.")
            return CHOOSING

        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            all_accounts = json.load(f)

        selected_accounts = [acc for acc in all_accounts if acc["username"] in usernames]

        if not selected_accounts:
            await update.message.reply_text("⚠️ لم يتم العثور على أي حساب من الأسماء التي أدخلتها.")
            return CHOOSING

        # حفظ فقط الحسابات المحددة مؤقتًا
        context.user_data["ACCOUNTS"] = selected_accounts
        await update.message.reply_text("⏳ جاري فحص الحسابات المحددة...")
        return await check_accounts(update, context)

    else:
        context.user_data.setdefault("usernames_to_check", []).append(text)
        await update.message.reply_text(f"✅ تم استلام: {text}")
        return TYPING_CHECK_USERNAMES




def get_main_menu_keyboard():
         return ReplyKeyboardMarkup([
  [ "لمعرفه انه البوت قيد التشغيل /status \n لي اعاده تشغيل البوت /restart \n للذهاب للعددات /setting ",],
        ["1️⃣اضهار عدد الحسابات ", "2️⃣ إدخال الحسابات"],
                    ["5️⃣: فحص الحسابات\n"],
        ["4\ufe0f\u20e3 اختيار العمليات علي الحساب يدويًا\n", "9️⃣ التفاعل التلقائي مع المستخدمين"],
        ['6️⃣ فحص حسب بالاسم'],["3️⃣ استرجاع النسخة الاحتياطية","🔙 الرجوع إلى القائمة"],
    
         ], resize_keyboard=True, one_time_keyboard=False)
        


async def set_unfollow_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if context.user_data.get("is_running"):
        await update.message.reply_text("⚠️ توجد عملية قيد التنفيذ حاليًا. يرجى الانتظار أو أرسل 'إلغاء' لإيقافها.")
        if update.effective_chat.id not in waiting_users:
            waiting_users.append(update.effective_chat.id)
        return CHOOSING

    context.user_data["is_running"] = True
    
  

    await update.message.reply_text("🚀 جاري تنفيذ الغاء  المتابعة...", reply_markup=get_main_menu_keyboard())
    
   
    CURRENT_OPERATION["name"] = " الغاء المتابعه قيد التشغيل"
    CURRENT_OPERATION["active"] = True
    CURRENT_OPERATION["completed"] = 0

    
    accounts = context.user_data.get("ACCOUNTS") or load_accounts()
    username_to_follow = context.user_data.get("ACCOUNT_TO_UNFOLLOW")
    CURRENT_OPERATION["total"] = len(accounts)
    if not username_to_follow:
        context.user_data["is_running"] = False
        await update.message.reply_text("❌ يرجى تحديد اسم الحساب الذي تريد متابعته أولًا.")
        return CHOOSING

    def run_followers():
        # إنشاء event loop خاص بالخيط
        # asyncio.set_event_loop(asyncio.new_event_loop())
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        chat_id = update.effective_chat.id  # ✅ نحفظ chat_id لاستخدامه لاحقًا

       

        def worker(acc):
            with thread_limiter:
                try:
                    print(f"👤 [{acc['username']}] بدء تنفيذالغاء  المتابعة...")
                    obj = process_account(acc["username"], acc["password"])
                    if not obj.load_cookies():
                        obj.login()
                   
                    obj.unfollow_user(username_to_follow)
                    obj.driver.quit()
                    print(f"✅ [{acc['username']}] تم تنفيذ الغاء المتابعة.")
                    CURRENT_OPERATION["completed"] += 1 
                except Exception as e:
                    print(f"❌ [{acc['username']}] خطأ أثناء تنفيذ الغاء  المتابعة: {e}")

        threads = []
        for acc in accounts:
            t = threading.Thread(target=worker, args=(acc,), daemon=True)
            t.start()
            threads.append(t)

        # انتظار كل الخيوط
        for t in threads:
            t.join()
      
        print("✅ تم الانتهاء من جميع عمليات الغاءالمتابعة.")
        CURRENT_OPERATION["active"] = False
       
        
        waiting_users.clear()
        loop.run_until_complete(reset_is_running(context))
        loop.close()
        return
    
    threading.Thread(target=run_followers).start()
    
    
    

    return CHOOSING

   
async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    def listoprtion():
       return ReplyKeyboardMarkup([
            ["1️⃣ إعجاب فقط", "2️⃣ تعليق فقط"],
            ["3️⃣ متابعة فقط", "4️⃣ رد على الستوري"],
            ["7️⃣ إلغاء متابعة حساب"],["🔙 الرجوع إلى القائمة"]

        ], resize_keyboard=True ,one_time_keyboard=False)
    
    def listaout():
        return ReplyKeyboardMarkup([
            ["1️⃣ إضافة مستخدم", "2️⃣ عرض القائمة"],
            ["3️⃣ بدء المراقبة"],["🔙 الرجوع إلى القائمة"],

        ], resize_keyboard=True,one_time_keyboard=False)
    

    if text.lower() in ["نعم", "yes"] and context.user_data.get("awaiting_change_password_decision"):
          context.user_data["awaiting_change_password_decision"] = False
          return await change_failed_password(update, context)
    if text.lower() in ["لا", "no"] and context.user_data.get("awaiting_change_password_decision"):
           context.user_data["awaiting_change_password_decision"] = False
         
           # تحميل الحسابات الحالية
           if os.path.exists(ACCOUNTS_FILE):
               with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                   current_accounts = json.load(f)
           else:
               current_accounts = []
         
           # تحميل الحسابات الفاشلة
           if os.path.exists(FAILED_ACCOUNTS_FILE):
               with open(FAILED_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                   failed_accounts = json.load(f)
           else:
               failed_accounts = []
         
           # حذف الحسابات الفاشلة من القائمة العامة
           failed_usernames = {acc["username"] for acc in failed_accounts}
           updated_accounts = [acc for acc in current_accounts if acc["username"] not in failed_usernames]
         
           # حفظ الحسابات المحدثة
           with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
               json.dump(updated_accounts, f, ensure_ascii=False, indent=4)
         
           await update.message.reply_text(
               f"🗑️ تم حذف {len(failed_accounts)} حساب فاشل من الملف.",
               reply_markup=get_main_menu_keyboard()
           )
         
           return CHOOSING
         
    



    if text.startswith("البوت قيد التشغيل"):
         return await status(update, context)

    if text == "🔁 إعادة المحاولة" and context.user_data.get("retry_failed_accounts"):
          context.user_data["changing_password"] = True
          context.user_data["updated_failed_accounts"] = []
          
          # استبدل الحسابات الفاشلة بالمحاولة الجديدة
          with open(FAILED_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
              json.dump(context.user_data["retry_failed_accounts"], f, indent=4, ensure_ascii=False)
      
          await update.message.reply_text(
              "✏️ أرسل الحسابات بصيغة username:newpassword\nوأرسل 'done' عند الانتهاء.",
              reply_markup=ReplyKeyboardRemove()
          )
          return CHOOSING

    if text == "❌ تجاهل":
         failed_accounts = context.user_data.pop("retry_failed_accounts", [])

         if os.path.exists(ACCOUNTS_FILE):
             with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                 all_accounts = json.load(f)
         else:
             all_accounts = []

         # إزالة الحسابات الفاشلة من القائمة
         usernames_to_remove = {acc["username"] for acc in failed_accounts}
         updated_accounts = [acc for acc in all_accounts if acc["username"] not in usernames_to_remove]

         # حفظ القائمة الجديدة
         with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
             json.dump(updated_accounts, f, ensure_ascii=False, indent=4)

         await update.message.reply_text(
             f"✅ تم حذف {len(failed_accounts)} حساب فاشل من الملف.",
             reply_markup=get_main_menu_keyboard()
         )
         return CHOOSING


    if context.user_data.get("changing_password"):
        line = update.message.text.strip()
 
        if "updated_failed_accounts" not in context.user_data:
            context.user_data["updated_failed_accounts"] = []
    
        if line.lower() == "done":
            # استخدم نفس منطق إعادة المحاولة عبر تفعيل changing_multiple_passwords
            context.user_data["changing_password"] = False
            context.user_data["changing_multiple_passwords"] = True
            await update.message.reply_text("✅ سيتم الآن التحقق من الحسابات التي تم تعديلها...")
            return await choice_handler(update, context)
    
        if ":" not in line:
            await update.message.reply_text("❌ صيغة خاطئة. استخدم `username:newpassword` أو أرسل 'done' عند الانتهاء.")
            return CHOOSING
    
        username, new_pass = line.split(":", 1)
        context.user_data["updated_failed_accounts"].append({
            "username": username,
            "password": new_pass
        })
        await update.message.reply_text(f"✅ تم استلام: {username}")
        return CHOOSING
 
    if context.user_data.get("changing_multiple_passwords"):
           line = update.message.text.strip()
          
           if "updated_failed_accounts" not in context.user_data:
               context.user_data["updated_failed_accounts"] = []
          
           # إذا كتب "done"، ننهي الإدخال ونبدأ الفحص والنقل
           if line.lower() == "done":
               context.user_data["changing_multiple_passwords"] = False
               updated = context.user_data["updated_failed_accounts"]
          
               if not updated:
                   await update.message.reply_text("ℹ️ لم يتم إدخال أي حساب جديد.")
                   return CHOOSING
          
               if os.path.exists(FAILED_ACCOUNTS_FILE):
                   with open(FAILED_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                       failed = json.load(f)
               else:
                   failed = []
          
               if os.path.exists(ACCOUNTS_FILE):
                   with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                       working = json.load(f)
               else:
                   working = []
          
               success_count = 0
               failed_updated = []
          
               for item in updated:
                   username = item["username"]
                   new_pass = item["password"]
          
                   # تحديث كلمة المرور في القائمة الفاشلة
                   for acc in failed:
                       if acc["username"] == username:
                           acc["password"] = new_pass
                           break
          
                   try:
                       obj = process_account(username, new_pass)
                       if obj.load_cookies() or obj.login():
                           working.append({"username": username, "password": new_pass})
                           failed = [acc for acc in failed if acc["username"] != username]
                           success_count += 1
                           await update.message.reply_text(f"✅ [{username}] تم التحقق ونقله إلى الحسابات الصالحة.")
                       else:
                           failed_updated.append({"username": username, "password": new_pass})
                           await update.message.reply_text(f"❌ [{username}] لا يزال غير صالح بعد التغيير.")
                       obj.driver.quit()
                   except Exception as e:
                       failed_updated.append({"username": username, "password": new_pass})
                       await update.message.reply_text(f"⚠️ [{username}] حدث خطأ: {e}")
          
               # حفظ الملفات بعد التعديل
               with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                   json.dump(working, f, indent=4, ensure_ascii=False)
          
               with open(FAILED_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                   json.dump(failed + failed_updated, f, indent=4, ensure_ascii=False)
          
               context.user_data.pop("updated_failed_accounts", None)

               if failed_updated:
                   context.user_data["retry_failed_accounts"] = failed_updated
                
                   await update.message.reply_text(
                       f"🎉 تم إنهاء العملية:\n"
                       f"✔️ حسابات تم تصحيحها: {success_count}\n"
                       f"❌ لم يتم تصحيح: {len(failed_updated)}\n\n"
                       "هل ترغب في إعادة المحاولة للحسابات التي لم يتم تصحيحها؟",
                       reply_markup=ReplyKeyboardMarkup([
                           ["🔁 إعادة المحاولة", "❌ تجاهل"]
                       ], resize_keyboard=True)
                   )
               else:
                   await update.message.reply_text(
                       f"🎉 تم تصحيح جميع الحسابات بنجاح!",
                       reply_markup=get_main_menu_keyboard()
                   )

               context.user_data.pop("updated_failed_accounts", None)
               return CHOOSING
          
           # فحص الصيغة
           if ":" not in line:
               await update.message.reply_text("❌ صيغة خاطئة. استخدم `username:newpassword` أو أرسل 'done' عند الانتهاء.")
               return CHOOSING
          
           # إضافة الحساب للتحديث
           username, new_pass = line.split(":", 1)
           context.user_data["updated_failed_accounts"].append({"username": username, "password": new_pass})
           await update.message.reply_text(f"✅ تم استلام: {username}")
           return CHOOSING
          

    # تحديث الأزرار في القائمة الفرعية للعمليات اليدوية
    if context.user_data.get("awaiting_sub_choice"):
        context.user_data["sub_choice"] = text
        context.user_data["awaiting_sub_choice"] = False

        if text.startswith("1"):
            context.user_data["sub_choice"] = "like_only"
            await update.message.reply_text("🔗 أرسل رابط المنشور لعمل إعجاب:", reply_markup=ReplyKeyboardRemove())
            context.user_data["awaiting_like_url"] = True
            return CHOOSING

        elif text.startswith("2"):
            context.user_data["sub_choice"] = "comment_only"
            await update.message.reply_text("🔗 أرسل رابط المنشور للتعليق:", reply_markup=ReplyKeyboardRemove())
            context.user_data["awaiting_comment_url"] = True
            return CHOOSING
        
        elif text.startswith("3"):
            context.user_data["sub_choice"] = "follow_only"
            await update.message.reply_text("👤 أرسل اسم المستخدم للمتابعة:", reply_markup=ReplyKeyboardRemove())
            context.user_data["awaiting_follow_user"] = True
            return CHOOSING
        
        elif text == "7️⃣ إلغاء متابعة حساب":
           await update.message.reply_text("📛 أرسل اسم المستخدم الذي تريد إلغاء متابعته:")
           context.user_data["awaiting_unfollow"] = True
           return CHOOSING


        elif text.startswith("4"):
            context.user_data["sub_choice"] = "story_reply_only"
            await update.message.reply_text("👁️ أرسل اسم المستخدم الذي تريد الرد على الستوري الخاص به:", reply_markup=ReplyKeyboardRemove())
            context.user_data["awaiting_story_user"] = True
            return CHOOSING

        elif text.startswith("5"):
            await update.message.reply_text("🔗 أرسل رابط المنشور لعمل إعجاب:", reply_markup=ReplyKeyboardRemove())
            context.user_data["awaiting_like_url"] = True
        return CHOOSING

    if context.user_data.get("awaiting_like_url"):
        context.user_data["PHOTO_URL_FOR_LIKE"] = text
        context.user_data["awaiting_like_url"] = False
        if context.user_data.get("sub_choice") in ["2", "5"]:
            await update.message.reply_text("📝 اختر أحد التعليقات التالية:",
                reply_markup=ReplyKeyboardMarkup([
                    ["🔥 رائع!", "👏 ممتاز!"],
                    ["💯 محتوى مميز", "❤️ أحببته"]
                ], resize_keyboard=True))
            context.user_data["awaiting_comment_text"] = True
            return CHOOSING
        
        if context.user_data.get("sub_choice") == "like_only":
            await update.message.reply_text("🔢 كم عدد الحسابات التي ستعمل لايك؟", reply_markup=ReplyKeyboardRemove())
            return SETTING_LIKE_COUNT
        await update.message.reply_text("✅ تم حفظ الرابط.", reply_markup=ReplyKeyboardRemove())
        return CHOOSING
    

    if text.lower() in ["إلغاء", "cancel", "الغاء"]:
     if context.user_data.get("is_running"):
        context.user_data["is_running"] = False
        await update.message.reply_text("🛑 تم إلغاء العملية الجارية.")
     else:
        await update.message.reply_text("ℹ️ لا توجد عملية قيد التشغيل.")
     return CHOOSING
    
    


    if context.user_data.get("awaiting_unfollow"):
         context.user_data["ACCOUNT_TO_UNFOLLOW"] =text.strip()
         context.user_data["awaiting_unfollow"] = False
         await update.message.reply_text("🚀 جاري تنفيذ إلغاء المتابعة...")
         return await set_unfollow_count(update, context)



    if context.user_data.get("awaiting_comment_url"):
        context.user_data["PHOTO_URL_FOR_COMMENT"] = text
        context.user_data["awaiting_comment_url"] = False
        await update.message.reply_text("🔢 كم عدد الحسابات التي ستعمل تعليق؟", reply_markup=ReplyKeyboardRemove())
        context.user_data["awaiting_comment_accounts"] = True
        return CHOOSING

    if context.user_data.get("awaiting_comment_accounts", False):
        context.user_data["max_commenters"] = int(text)
        await update.message.reply_text("✏️ كم عدد التعليقات التي سيكتبها كل حساب؟")
        context.user_data["awaiting_comments_per_account"] = True
        return SETTING_COMMENTS_PER_ACCOUNT
    # if context.user_data.get("awaiting_comments_per_account", False):
    #    return SETTING_COMMENTS_PER_ACCOUNT


    if context.user_data.get("awaiting_follow_user"):
        context.user_data["ACCOUNT_TO_FOLLOW"] = text
        context.user_data["awaiting_follow_user"] = False
        await update.message.reply_text("🔢 كم عدد الحسابات التي ستقوم بالمتابعة؟", reply_markup=ReplyKeyboardRemove())
        return SETTING_FOLLOW_COUNT

    if context.user_data.get("awaiting_story_user"):
        context.user_data["STORY_USER"] = text
        context.user_data["awaiting_story_user"] = False
        await update.message.reply_text("🔢 كم عدد الحسابات التي ستقوم بالرد على الستوري؟", reply_markup=ReplyKeyboardRemove())
        return SETTING_LIKE_COUNT
    
    if text.strip().startswith("1") or "اضهار عدد الحسابات" in text:
        accounts = load_accounts()
        await update.message.reply_text(f"📂 عدد الحسابات المحفوظة: {len(accounts)}",reply_markup=get_main_menu_keyboard())
        
        return CHOOSING
    
    if text == "🔙 الرجوع إلى القائمة":
         await update.message.reply_text("🔙 تم الرجوع إلى القائمة الرئيسية.")
         return await start(update, context)


    if text.strip().startswith("6") or "فحص حسب الاسم" in text:
         context.user_data["usernames_to_check"] = []
         await update.message.reply_text("✏️ أرسل أسماء المستخدمين (سطر لكل اسم). أرسل 'done' عند الانتهاء.")
         return TYPING_CHECK_USERNAMES
    #  text.strip() =="2️⃣" or " عرض القائمة"in text:
    if text.strip()=="2" or "إدخال الحسابات" in text:
        context.user_data["new_accounts"] = []
        await update.message.reply_text("✏️ أرسل الحسابات بصيغة username:password، واكتب 'done' عند الانتهاء:",  )
        return TYPING_ACCOUNTS
    

    if text.strip().startswith("5") or "فحص الحسابات" in text:
        await update.message.reply_text("⏳ جاري فحص الحسابات...") 

        return await check_accounts(update, context)

    if text == "3️⃣ استرجاع النسخة الاحتياطية":
           return await restore_accounts_from_backup(update, context)

    # القوائم الرئيسية بالأزرار
    if text.strip().startswith("4") or "اختيار العمليات" in text:
        reply_markup = listoprtion()
        await update.message.reply_text(
            "🔍 اختر العملية التي تريد تنفيذها فقط:",
            reply_markup=reply_markup
        )
        context.user_data["awaiting_sub_choice"] = True
        return CHOOSING

    if text.strip().startswith("9") or "9️⃣ التفاعل التلقائي مع المستخدمين" in text:
        reply_markup = listaout()
        await update.message.reply_text(
            "👥 التفاعل مع مستخدمين محددين:\n🛑 لإلغاء العملية ارسل /stop",
            reply_markup=reply_markup
        )
        return WATCHLIST_OPTIONS


    elif text == "0":
        accounts = context.user_data.get("ACCOUNTS")
        if not accounts:
            accounts = load_accounts()
            context.user_data["ACCOUNTS"] = accounts

        if not accounts:
            await update.message.reply_text("⚠️ لم يتم إدخال أو تحميل أي حساب.")
            return CHOOSING

        await update.message.reply_text("🚀 بدء المعالجة لجميع الحسابات...\n")

        threads = []
        for acc in accounts:
            account_obj = process_account(
                acc["username"], acc["password"],
                photo_url_for_comment=context.user_data.get("PHOTO_URL_FOR_COMMENT"),
                account_to_follow=context.user_data.get("ACCOUNT_TO_FOLLOW"),
                reply_text_on_story=random.choice(COMMENT_LIST),
                like_url=context.user_data.get("PHOTO_URL_FOR_LIKE"),
                comment_text=context.user_data.get("COMMENT_TEXT")
            )
            def run_account(obj):
             with thread_limiter:
               obj.process()

           
            t = threading.Thread(target=run_account, args=(account_obj,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        await update.message.reply_text("✅ تم تنفيذ جميع المهام بنجاح.")
    


    else:
        await update.message.reply_text("❌ خيار غير صحيح، حاول مرة أخرى.")

    return CHOOSING


async def accounts_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    line = update.message.text.strip()

    if "awaiting_token_username" in context.user_data:
        username = context.user_data.pop("awaiting_token_username")
        token = line

        # حمّل ملف التوكنات
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                try:
                    tokens_data = json.load(f)
                except json.JSONDecodeError:
                    tokens_data = {}
        else:
            tokens_data = {}

        # احفظ التوكن تحت اسم المستخدم
        tokens_data[username] = token
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, ensure_ascii=False, indent=4)

        await update.message.reply_text(f"🔐 تم حفظ التوكن للحساب: {username}")
        return TYPING_ACCOUNTS

    if line.lower() == "done":
        new_accounts = context.user_data.get("new_accounts", [])
        file_path = ACCOUNTS_FILE

        existing_accounts = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_accounts = json.load(f)
                    if not isinstance(existing_accounts, list):
                        existing_accounts = []
                except json.JSONDecodeError:
                    existing_accounts = []

        existing_accounts.extend(new_accounts)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_accounts, f, ensure_ascii=False, indent=4)

        context.user_data["ACCOUNTS"] = existing_accounts
        await update.message.reply_text(f"✅ تم حفظ {len(new_accounts)} حساب جديد بنجاح.", reply_markup=get_main_menu_keyboard())
        return CHOOSING

    if ":" in line:
        username, password = line.split(":", 1)
        if "new_accounts" not in context.user_data:
            context.user_data["new_accounts"] = []
        context.user_data["new_accounts"].append({"username": username, "password": password})

        # نطلب التوكن لهذا المستخدم
        context.user_data["awaiting_token_username"] = username
        await update.message.reply_text(f"✅ تم إضافة الحساب: {username}\n🔐 أرسل الآن التوكن المرتبط بهذا الحساب.")
    else:
        await update.message.reply_text("❌ صيغة غير صحيحة. أدخل الحساب كـ username:password")

    return TYPING_ACCOUNTS


async def watchlist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    file_path = WATCHLIST

    if text.strip() == "اضهار عدد الحسابات" or "1️⃣"  in text:
        await update.message.reply_text("👤 أرسل اسم المستخدم لإضافته إلى المراقبة:")
        return TYPING_WATCH_USERNAME

    elif  text.strip() =="2️⃣" or " عرض القائمة"in text:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                watchlist = json.load(f)
                msg = "\n".join(f"- {user}" for user in watchlist)
                await update.message.reply_text(f"📋 المستخدمين في المراقبة:\n{msg}")
        else:
            await update.message.reply_text("📭 لا توجد قائمة مراقبة.")
        return CHOOSING

    elif text.strip() == "3️⃣"  or "بدء المراقبة" :
       await start_monitoring(update, context)
       return CHOOSING

    elif text == "🔙 الرجوع إلى القائمة":
        await update.message.reply_text("🔙 تم الرجوع إلى القائمة الرئيسية.")
        return await start(update, context)
      
      


    else:
        await update.message.reply_text("❌ خيار غير صحيح. أرسل 1 أو 2 أو 3.")
        return WATCHLIST_OPTIONS
    
    
async def watchlist_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    file_path = WATCHLIST

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                watchlist = json.load(f)
                if not isinstance(watchlist, list):
                    watchlist = []
            except json.JSONDecodeError:
                watchlist = []
    else:
        watchlist = []

    if username not in watchlist:
        watchlist.append(username)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=4)
        await update.message.reply_text(f"✅ تم إضافة المستخدم {username}.")
    else:
        await update.message.reply_text("ℹ️ المستخدم موجود بالفعل.")
    return CHOOSING


from telegram.ext import filters


# أي رسالة من غير المصرّح لهم يتم رفضها

# بداية من اختيار "الإعدادات"
async def setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["➕ إضافة مستخدم", "➖ حذف مستخدم"],
        ["📝 تغيير ملف التعليقات", "📄 عرض ملف التعليقات"],
        ["🔙 الرجوع إلى القائمة"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("⚙️ إعدادات البوت:", reply_markup=reply_markup)
    return SETTING_OPTION


async def setting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "➕ إضافة مستخدم":
        await update.message.reply_text("👤 أرسل معرف المستخدم الذي تريد إضافته.")
        return ADD_USER

    elif text == "➖ حذف مستخدم":
        await update.message.reply_text("🗑️ أرسل معرف المستخدم الذي تريد حذفه.")
        return DEL_USER

    elif text == "📝 تغيير ملف التعليقات":
        await update.message.reply_text("✏️ أرسل التعليقات الجديدة، كل تعليق في سطر.")
        return EDIT_COMMENTS

    elif text == "📄 عرض ملف التعليقات":
        return await show_comments(update, context)

    elif text == "🔙 الرجوع إلى القائمة":
        await update.message.reply_text("🔙 تم الرجوع إلى القائمة الرئيسية.")
        return await start(update, context)

    else:
        await update.message.reply_text("❌ خيار غير صحيح. اختر من القائمة.",reply_markup=get_main_menu_keyboard())
        return SETTING_OPTION


      # حالة تنتظر الردود بناءً على الخيارات
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text.strip())
        file_path = os.path.join(BASE_DIR, "account", "allowed_users.json")

        users = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                users = json.load(f)

        if user_id not in users:
            users.append(user_id)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            await update.message.reply_text("✅ تم إضافة المستخدم." ,reply_markup=get_main_menu_keyboard())
        else:
            await update.message.reply_text("ℹ️ المستخدم موجود مسبقًا.", reply_markup=get_main_menu_keyboard())
    except:
        await update.message.reply_text("❌ صيغة خاطئة. أرسل المعرف كرقم.", reply_markup=get_main_menu_keyboard())
    return CHOOSING


async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text.strip())
        if user_id =='7531743437'or '828920195':
            return
        file_path = os.path.join(BASE_DIR, "account", "allowed_users.json")

        users = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                users = json.load(f)

        if user_id in users:
            users.remove(user_id)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            await update.message.reply_text("✅ تم حذف المستخدم.", reply_markup=get_main_menu_keyboard())
        else:
            await update.message.reply_text("⚠️ المستخدم غير موجود.", reply_markup=get_main_menu_keyboard())
    except:
        await update.message.reply_text("❌ صيغة خاطئة. أرسل المعرف كرقم.", reply_markup=get_main_menu_keyboard())
    return CHOOSING


async def edit_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("❌ لم يتم إرسال تعليقات.", reply_markup=get_main_menu_keyboard())
        return CHOOSING

    file_path = os.path.join(BASE_DIR, "account", "commit.txt")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        await update.message.reply_text("✅ تم تحديث ملف التعليقات.", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ أثناء الحفظ: {e}", reply_markup=get_main_menu_keyboard())
    return CHOOSING


async def show_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = os.path.join(BASE_DIR, "account", "commit.txt")

    if not os.path.exists(file_path):
        await update.message.reply_text("📭 لا يوجد ملف تعليقات.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            comments = f.read().strip()
        await update.message.reply_text(comments or "📭 الملف فارغ.", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء قراءة الملف: {e}", reply_markup=get_main_menu_keyboard())
    return CHOOSING

AUTHORIZED_USER_ID=None
def main():
          
     allowed_file = os.path.join(BASE_DIR, "account", "allowed_users.json")
     with open(allowed_file, "r", encoding="utf-8") as f:
             AUTHORIZED_USER_ID = json.load(f)
             
     app = ApplicationBuilder().token(TOKEN).build()
    # أضف handlers هنا
    
    




     conv_handler = ConversationHandler(
         entry_points=[CommandHandler("start", start)],
         states={
             CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(AUTHORIZED_USER_ID), choice_handler)],
             TYPING_ACCOUNTS: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, accounts_input)],
             WATCHLIST_OPTIONS: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, watchlist_handler)],
             TYPING_WATCH_USERNAME: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, watchlist_input)],
             SETTING_LIKE_COUNT: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, set_like_count)],
             SETTING_COMMENTS_PER_ACCOUNT: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, set_comments_per_account)],
             SETTING_FOLLOW_COUNT: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, set_follow_count)],
             TYPING_CHECK_USERNAMES: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, check_by_usernames)],
            ADD_USER: [MessageHandler(filters.TEXT  & filters.User(AUTHORIZED_USER_ID)& ~filters.COMMAND, add_user)],
            DEL_USER: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, del_user)],
            EDIT_COMMENTS: [MessageHandler(filters.TEXT  & filters.User(AUTHORIZED_USER_ID)& ~filters.COMMAND, edit_comments)],
           SETTING_OPTION: [MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, setting_handler)],
           UNFOLLOW_USER:[MessageHandler(filters.TEXT & filters.User(AUTHORIZED_USER_ID) & ~filters.COMMAND, set_unfollow_count)],

         },
         fallbacks=[CommandHandler("stop", stop,filters.User(AUTHORIZED_USER_ID)),
                    CommandHandler("start", start,filters.User(AUTHORIZED_USER_ID)),
                    CommandHandler("status", status),
                    CommandHandler("restart", restart_bot,filters.User(AUTHORIZED_USER_ID)),
                    CommandHandler("setting", setting,filters.User(AUTHORIZED_USER_ID))
                    
                    ], 
     )
 
     app.add_handler(conv_handler)
     app.run_polling()
     app.add_handler( CommandHandler("start", start, filters.User(AUTHORIZED_USER_ID ))) 
     app.add_handler(CommandHandler("stop", stop))
     app.add_handler(CommandHandler("check_accounts", check_accounts,filters.User(AUTHORIZED_USER_ID)))
     app.add_handler(CommandHandler("change_password", change_failed_password,filters.User(AUTHORIZED_USER_ID)))
     app.add_handler(CommandHandler("recheck_failed", recheck_failed_accounts,filters.User(AUTHORIZED_USER_ID)))
     app.add_handler(CommandHandler("status", status,filters.User(AUTHORIZED_USER_ID)))
     app.add_handler(CommandHandler("restart", restart_bot, filters.User(AUTHORIZED_USER_ID)))
    #  app.add_handler(CommandHandler("show_comments", restart_bot, filters.User(AUTHORIZED_USER_ID)))

     async def unauthorized_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
       await update.message.reply_text("🚫 لا تملك صلاحية استخدام هذا البوت.")

# أي رسالة من غير المصرّح لهم يتم رفضها
     app.add_handler(MessageHandler(~filters.User(AUTHORIZED_USER_ID), unauthorized_handler))



if __name__ == "__main__":
    main()
