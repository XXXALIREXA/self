import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# دریافت متغیرها از تنظیمات گیت‌هاب
STUDENT_ID = os.environ.get("4030111152")
PASSWORD = os.environ.get("123456sS@")
BOT_TOKEN = os.environ.get("8726546315:AAFgXTiz-XigEbYoD72ujnC7ubEylx97q2Y")
CHAT_ID = os.environ.get("5120559674")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("خطا در ارسال پیام تلگرام:", e)

# تنظیمات مرورگر برای اجرا در سرور گیت‌هاب (بدون مانیتور)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

send_telegram_message("🤖 ربات بررسی سلف روشن شد و در حال اجرای پایش است...")

driver = webdriver.Chrome(options=options)

try:
    # ۱. ورود به صفحه اصلی برای لاگین
    driver.get("https://self.pgu.ac.ir")
    time.sleep(4)

    # وارد کردن نام کاربری و رمز عبور بر اساس کدهای سایت شما
    driver.find_element(By.ID, "username").send_keys(STUDENT_ID)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    time.sleep(1) # یک مکث کوتاه برای اینکه دکمه ورود در سیستم انگولار فعال شود
    
    # کلیک روی دکمه ورود
    driver.find_element(By.XPATH, "//button[contains(text(), 'ورود')]").click()
    
    time.sleep(5)  # مکث برای ورود کامل به پنل و تایید اطلاعات

    # پیام تایید لاگین به تلگرام
    send_telegram_message("✅ ربات با موفقیت وارد سایت شد (لاگین انجام شد).")

    # ۲. انتقال مستقیم به تب رزرو غذا
    driver.get("https://self.pgu.ac.ir/#!/Reservation")
    time.sleep(5)  # مکث برای بارگذاری کامل کدهای انگولار (AngularJS)

    # ۳. رفتن به هفته جاری و شنبه
    try:
        # کلیک روی دکمه هفته بعد/جاری
        hafte_btn = driver.find_element(By.XPATH, "//*[contains(@ng-click, 'browseWeek')]")
        hafte_btn.click()
    except:
        pass
    
    time.sleep(2)

    try:
        # کلیک روی تب شنبه (اولین تب)
        shanbe_btn = driver.find_element(By.XPATH, "//label[@href='#tab_day0']")
        shanbe_btn.click()
    except:
        send_telegram_message("⚠️ خطا: دکمه شنبه در صفحه رزرو پیدا نشد.")

    time.sleep(3)

    # ۴. بررسی وضعیت ناهار
    page_text = driver.page_source
    target_phrase = "برنامه رزرو تعریف نشده است"

    if "ناهار" in page_text:
        if target_phrase not in page_text:
            send_telegram_message(">>> 🎉 خبر خوب! ظرفیت ناهار شنبه باز شد! سریع وارد سایت شو و رزرو کن! <<<")
        else:
            print("ظرفیت هنوز بسته است. (پیامی ارسال نمیشود تا ربات اسپم نکند)")
    else:
        print("بخش ناهار در صفحه لود نشد.")

except Exception as e:
    print("خطای سیستمی در اجرای مراحل:", e)
finally:
    driver.quit()
