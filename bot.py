import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STUDENT_ID = "4030111152"
PASSWORD = "123456sS@"
BOT_TOKEN = "8726546315:AAFgXTiz-XigEbYoD72ujnC7ubEylx97q2Y"
CHAT_ID = "5120559674"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("خطا در ارسال پیام:", e)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://self.pgu.ac.ir")
    
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(STUDENT_ID)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ورود')]")))
    login_btn.click()
    
    send_telegram_message("✅ ربات وارد سایت شد و در حال بررسی ناهار هفته آینده است...")
    time.sleep(4)

    # حلقه تکرار تا زمان باز شدن ظرفیت
    while True:
        # انتقال به تب رزرو (یا رفرش در دفعات بعدی)
        driver.get("https://self.pgu.ac.ir/#!/Reservation")
        driver.refresh()
        time.sleep(3)

        # ۱. کلیک دقیق روی دکمه "هفته بعد"
        try:
            hafte_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'هفته بعد') or contains(@ng-click, '7')]")))
            hafte_btn.click()
            time.sleep(3)
        except:
            pass

        # ۲. کلیک روی تب شنبه
        try:
            shanbe_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@href, 'tab_day0') or contains(text(), 'شنبه')]")))
            shanbe_btn.click()
            time.sleep(3)
        except:
            send_telegram_message("⚠️ خطا: دکمه شنبه پیدا نشد.")

        # ۳. استخراج متن صفحه و دور ریختن صبحانه و شام
        visible_text = driver.find_element(By.TAG_NAME, "body").text
        target_phrase = "برنامه رزرو تعریف نشده است"

        # بررسی وضعیت ناهار به تنهایی
        if "ناهار" in visible_text:
            # تمام متن‌های قبل از ناهار (شامل صبحانه) دور ریخته می‌شود
            text_after_nahar = visible_text.split("ناهار")[1]
            
            # تمام متن‌های بعد از شام دور ریخته می‌شود
            if "شام" in text_after_nahar:
                nahar_only_text = text_after_nahar.split("شام")[0]
            else:
                nahar_only_text = text_after_nahar

            # حالا فقط محدوده متنی خالص ناهار بررسی می‌شود
            if target_phrase not in nahar_only_text:
                send_telegram_message(">>> 🍛 خبر خوب! ظرفیت **ناهار** شنبه باز شد! سریع رزرو کن! <<<")
                break  # خروج از حلقه و پایان کار اکشن پس از ارسال خبر
            else:
                print("ظرفیت ناهار هنوز بسته است. انتظار به مدت ۵ دقیقه برای بررسی مجدد...")
        else:
            print("بخش ناهار در صفحه لود نشد. انتظار به مدت ۵ دقیقه برای بررسی مجدد...")

        # توقف به مدت ۵ دقیقه (۳۰۰ ثانیه) قبل از تکرار مجدد حلقه
        time.sleep(300)

except Exception as e:
    print("خطای سیستمی:", e)
finally:
    driver.quit()
