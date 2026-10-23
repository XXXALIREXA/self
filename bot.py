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
# تنظیم سایز صفحه برای جلوگیری از پنهان شدن دکمه‌ها در حالت موبایلی
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)  # حداکثر ۱۵ ثانیه برای لود هر دکمه صبر می‌کند

try:
    driver.get("https://self.pgu.ac.ir")
    
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(STUDENT_ID)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ورود')]")))
    login_btn.click()
    
    send_telegram_message("✅ ربات با موفقیت وارد سایت شد (لاگین انجام شد).")
    time.sleep(3)

    # انتقال مستقیم به تب رزرو غذا
    driver.get("https://self.pgu.ac.ir/#!/Reservation")

    # کلیک روی دکمه هفته (اگر وجود داشت)
    try:
        hafte_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@ng-click, 'browseWeek')]")))
        hafte_btn.click()
        time.sleep(2)  # مکث برای رفرش شدن جدول بعد از کلیک
    except:
        pass

    # پیدا کردن دقیق دکمه شنبه با صبر هوشمند
    try:
        shanbe_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@href, 'tab_day0') or contains(text(), 'شنبه')]")))
        shanbe_btn.click()
        time.sleep(2)
    except:
        send_telegram_message("⚠️ خطا: دکمه شنبه حتی پس از ۱۵ ثانیه پیدا نشد.")

    # بررسی وضعیت ناهار
    page_text = driver.page_source
    target_phrase = "برنامه رزرو تعریف نشده است"

    if "ناهار" in page_text:
        if target_phrase not in page_text:
            send_telegram_message(">>> 🎉 خبر خوب! ظرفیت ناهار شنبه باز شد! سریع وارد سایت شو و رزرو کن! <<<")
        else:
            print("ظرفیت ناهار هنوز بسته است.")
    else:
        print("بخش ناهار در صفحه لود نشد.")

except Exception as e:
    print("خطای سیستمی:", e)
finally:
    driver.quit()
