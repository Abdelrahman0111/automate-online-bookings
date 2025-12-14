"""
إعداد ChromeDriver للأتمتة
"""

import os
import requests
import zipfile
import platform
from pathlib import Path

def download_chromedriver():
    """تحميل ChromeDriver تلقائياً"""
    
    # تحديد نظام التشغيل
    system = platform.system().lower()
    
    if system == "windows":
        driver_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        
        # الحصول على أحدث إصدار
        response = requests.get(driver_url)
        latest_version = response.text.strip()
        
        # رابط التحميل
        download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_win32.zip"
        
        # تحميل الملف
        print("جاري تحميل ChromeDriver...")
        response = requests.get(download_url)
        
        # حفظ الملف
        with open("chromedriver.zip", "wb") as f:
            f.write(response.content)
        
        # استخراج الملف
        with zipfile.ZipFile("chromedriver.zip", "r") as zip_ref:
            zip_ref.extractall(".")
        
        # حذف ملف الضغط
        os.remove("chromedriver.zip")
        
        print("✅ تم تحميل ChromeDriver بنجاح!")
        print("📁 الملف موجود في نفس مجلد التطبيق")
        
    else:
        print("❌ هذا السكريبت مخصص لنظام Windows فقط")
        print("يرجى تحميل ChromeDriver يدوياً من:")
        print("https://chromedriver.chromium.org/")

if __name__ == "__main__":
    download_chromedriver()