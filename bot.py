import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ⚠️ حتماً این ۴ مقدار را با اطلاعات واقعی خودت جایگزین کن ⚠️
STUDENT_ID = "4030111152"
PASSWORD = "123456sS@"
BOT_TOKEN = "8726546315:AAFgXTiz-XigEbYoD72ujnC7ubEylx97q2Y"
CHAT_ID = "5120559674"

def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text}
  try:
    res = requests.post(url, json=payload, timeout=10)
    print("وضعیت ارسال تلگرام:", res.status_code, res.text)
  except Exception as e:
    print("خطا در ارسال پیام تلگرام:", e)


send_telegram_message(
    "🚀 اکشن گیت‌هاب استارت خورد! در حال باز کردن سایت دانشگاه..."
)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:
  driver.get("https://self.pgu.ac.ir")

  wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(
      STUDENT_ID
  )
  driver.find_element(By.ID, "password").send_keys(PASSWORD)
  time.sleep(1)

  login_btn = wait.until(
      EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ورود')]"))
  )
  login_btn.click()

  time.sleep(5)
  send_telegram_message(
      "✅ لاگین انجام شد. در حال رفتن به صفحه رزرو و بررسی هفته بعد..."
  )

  first_check = True

  while True:
    driver.get("https://self.pgu.ac.ir/#!/Reservation")
    driver.refresh()
    time.sleep(5)

    # ۱. کلیک دقیق و مستقیم فقط روی دکمه "هفته بعد" (حذف خطای -7 مربوط به هفته قبل)
    try:
      hafte_bad_btn = wait.until(
          EC.element_to_be_clickable((
              By.XPATH,
              "//button[contains(@ng-click, 'startdate,7') or"
              " contains(@ng-click, 'startdate, 7') or contains(., 'هفته بعد')]",
          ))
      )
      driver.execute_script("arguments[0].click();", hafte_bad_btn)
      time.sleep(4)  # مکث برای عوض شدن تاریخ‌های جدول به هفته آینده
    except Exception as e:
      if first_check:
        send_telegram_message("⚠️ خطا: دکمه هفته بعد پیدا نشد!")

    # ۲. کلیک روی تب شنبه و خواندن تاریخ آن برای اطمینان
    shanbe_date = "نامشخص"
    try:
      shanbe_btn = wait.until(
          EC.element_to_be_clickable((
              By.XPATH,
              "//label[contains(@href, 'tab_day0') or contains(., 'شنبه')]",
          ))
      )
      shanbe_date = shanbe_btn.text.replace("\n", " ")  # استخراج تاریخ روی تب شنبه
      driver.execute_script("arguments[0].click();", shanbe_btn)
      time.sleep(3)
    except:
      if first_check:
        send_telegram_message("⚠️ خطا: دکمه شنبه در صفحه پیدا نشد.")

    # ۳. خواندن متن تب شنبه
    try:
      day_tab = driver.find_element(By.ID, "tab_day0")
      visible_text = day_tab.text
    except:
      visible_text = driver.find_element(By.TAG_NAME, "body").text

    if "ناهار" in visible_text:
      text_after_nahar = visible_text.split("ناهار")[-1]

      if "شام" in text_after_nahar:
        nahar_only_text = text_after_nahar.split("شام")[0].strip()
      else:
        nahar_only_text = text_after_nahar.strip()

      # بررسی باز یا بسته بودن
      if "تعریف نشده است" not in nahar_only_text and len(nahar_only_text) > 2:
        msg = (
            f"🎉 خبر خوب! ظرفیت **ناهار** ({shanbe_date}) باز شد!\n\n📋 متن"
            f" داخل باکس ناهار:\n{nahar_only_text}"
        )
        send_telegram_message(msg)
        break
      else:
        print(f"ظرفیت بسته است ({shanbe_date}): {nahar_only_text}")
        if first_check:
          send_telegram_message(
              f"🔍 بررسی اول انجام شد ({shanbe_date}): ظرفیت ناهار فعلاً بسته"
              f" است.\n(متن دیده شده: {nahar_only_text})\n\n⏱ از این لحظه ربات"
              " هر ۵ دقیقه در سکوت چک می‌کند و فقط وقتی باز شد خبر می‌دهد."
          )
          first_check = False
    else:
      if first_check:
        send_telegram_message(f"⚠️ کلمه ناهار در تب ({shanbe_date}) پیدا نشد!")
        first_check = False

    time.sleep(300)

except Exception as e:
  send_telegram_message(f"❌ ربات متوقف شد! دلیل خطا:\n{str(e)[:200]}")
  print("خطای سیستمی:", e)
finally:
  driver.quit()
