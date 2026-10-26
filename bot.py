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

    while True:
        driver.get("https://self.pgu.ac.ir/#!/Reservation")
        driver.refresh()
        time.sleep(5)  # مکث بیشتر برای لود شدن کامل جدول انگولار

        # ۱. کلیک روی دکمه "هفته بعد"
        try:
            hafte_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'هفته بعد') or contains(@ng-click, '7')]")))
            hafte_btn.click()
            time.sleep(4)  # صبر برای دریافت جدول هفته بعد از سرور
        except:
            pass

        # ۲. کلیک روی تب شنبه
        try:
            shanbe_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@href, 'tab_day0') or contains(text(), 'شنبه')]")))
            shanbe_btn.click()
            time.sleep(3)
        except:
            send_telegram_message("⚠️ خطا: دکمه شنبه پیدا نشد.")

        # ۳. پیدا کردن بخش مربوط به روز شنبه به صورت دقیق (فقط تب فعال)
        try:
            # تلاش برای خواندن فقط محتوای داخل تب شنبه (tab_day0) به جای کل صفحه
            day_tab = driver.find_element(By.ID, "tab_day0")
            visible_text = day_tab.text
        except:
            # اگر آی‌دی تب پیدا نشد، کل صفحه را می‌خواند
            visible_text = driver.find_element(By.TAG_NAME, "body").text

        if "ناهار" in visible_text:
            # استفاده از آخرین کلمه "ناهار" در صفحه (مربوط به جدول اصلی)
            text_after_nahar = visible_text.split("ناهار")[-1]
            
            if "شام" in text_after_nahar:
                nahar_only_text = text_after_nahar.split("شام")[0].strip()
            else:
                nahar_only_text = text_after_nahar.strip()

            # بررسی وجود عبارت کلیدی "تعریف نشده است" (که هم شامل برنامه رزرو و هم رزرو سلف می‌شود)
            if "تعریف نشده است" not in nahar_only_text and len(nahar_only_text) > 2:
                msg = f"🎉 خبر خوب! ظرفیت **ناهار** شنبه باز شد!\n\n📋 متنی که ربات در بخش ناهار دید:\n{nahar_only_text}"
                send_telegram_message(msg)
                break
            else:
                print(f"ظرفیت بسته است. متن خوانده شده: {nahar_only_text}")
        else:
            print("کلمه ناهار در صفحه پیدا نشد.")

        time.sleep(300)

except Exception as e:
    print("خطای سیستمی:", e)
finally:
    driver.quit()
