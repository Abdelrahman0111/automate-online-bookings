# 📋 GitHub و Streamlit - دليل الإعداد الكامل

## 🚀 الخطوة 1: إعداد Git محلياً

### 1.1 تثبيت Git
- قم بتحميل Git من: https://git-scm.com/download/win
- قم بتثبيته مع الخيارات الافتراضية

### 1.2 إعداد Git الأولي
افتح PowerShell واكتب:
```powershell
git config --global user.name "اسمك"
git config --global user.email "بريدك@example.com"
```

### 1.3 تهيئة Repository محلياً
انتقل إلى مجلد المشروع:
```powershell
cd d:\Arkan_Almotamer\Automation_add_supplier_number_on_webbeds_from_jood
git init
git add .
git commit -m "Initial commit - WebBeds Automation Project"
```

---

## 📝 الخطوة 2: إنشاء Repository على GitHub

### 2.1 إنشاء حساب GitHub
- اذهب إلى: https://github.com
- انقر "Sign up" وأكمل التسجيل

### 2.2 إنشاء Repository جديد
1. اضغط على `+` في الزاوية اليمنى العلوية
2. اختر "New repository"
3. أدخل الاسم:
   - **Repository name**: `Automation_add_supplier_number_on_webbeds_from_jood`
   - **Description**: "Automate adding WebBeds supplier references from Jood system"
4. اختر "Public" (للعمل مع Streamlit)
5. **لا تختر** "Initialize with README" (لأننا سنرفع ملفاتنا)
6. اضغط "Create repository"

---

## 🔗 الخطوة 3: ربط المشروع المحلي بـ GitHub

بعد إنشاء Repository، ستظهر لك الأوامر. قم بتنفيذ الأوامر التالية:

```powershell
# إضافة GitHub كـ remote
git remote add origin https://github.com/YOUR_USERNAME/Automation_add_supplier_number_on_webbeds_from_jood.git

# إعادة تسمية الفرع إلى main
git branch -M main

# رفع الملفات إلى GitHub
git push -u origin main
```

**ملاحظة**: استبدل `YOUR_USERNAME` باسم حسابك على GitHub

---

## 🌐 الخطوة 4: نشر التطبيق على Streamlit Cloud

### 4.1 الدخول إلى Streamlit Cloud
1. اذهب إلى: https://streamlit.io/cloud
2. اضغط "Sign in with GitHub"
3. اختر حسابك على GitHub

### 4.2 نشر التطبيق
1. اضغط "New app"
2. اختر الخيارات:
   - **Repository**: اختر `Automation_add_supplier_number_on_webbeds_from_jood`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. اضغط "Deploy"

التطبيق سيكون متاحاً على رابط مثل:
```
https://automation-webbeds.streamlit.app
```

---

## 📦 الخطوة 5: تحديث المشروع

عندما تريد تحديث التطبيق:

```powershell
# قم بإجراء التغييرات على الملفات

# إضافة التغييرات
git add .

# كتابة رسالة التحديث
git commit -m "وصف التحديث هنا"

# رفع التحديثات
git push
```

Streamlit Cloud سيكتشف التغييرات تلقائياً ويعيد نشر التطبيق.

---

## 🔐 الخطوة 6: مفاتيح الوصول (اختياري)

إذا كنت تحتاج إلى مفاتيح وصول (مثل API keys):

1. اذهب إلى إعدادات Repository
2. اذهب إلى "Secrets" 
3. أضف المفاتيح التي تحتاجها
4. استخدمها في التطبيق:
```python
import streamlit as st
secret_key = st.secrets["key_name"]
```

---

## 📦 ملفات المشروع المطلوبة

تأكد من وجود هذه الملفات في المشروع:

```
Automation_add_supplier_number_on_webbeds_from_jood/
├── app.py                  # تطبيق Streamlit الرئيسي
├── requirements.txt        # المكتبات المطلوبة
├── .gitignore              # ملفات تُتجاهل من Git
├── .streamlit/
│   └── config.toml        # إعدادات Streamlit
├── chrome-extension/       # مجلد الإضافة
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   ├── background.js
│   └── README.md
├── README.md               # توثيق المشروع
└── requirements.txt        # المكتبات Python
```

---

## ✅ تأكد من requirements.txt

تأكد من وجود الملف `requirements.txt` بهذا المحتوى:

```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
```

---

## 🆘 حل المشاكل الشائعة

### المشكلة: GitHub رفض دفع التحديثات
**الحل:**
```powershell
git pull origin main
```

### المشكلة: Streamlit لم تكتشف التحديثات
**الحل:**
1. اذهب إلى Streamlit Cloud
2. اضغط على القائمة (⋮) في التطبيق
3. اختر "Reboot app"

### المشكلة: خطأ في المكتبات
**الحل:**
تأكد من أن `requirements.txt` يحتوي على جميع المكتبات المستخدمة.

---

## 📞 روابط مهمة

- GitHub: https://github.com
- Streamlit Cloud: https://streamlit.io/cloud
- توثيق Streamlit: https://docs.streamlit.io
- GitHub Desktop (بديل سهل لـ Git): https://desktop.github.com

---

## 🎉 الخلاصة

بعد هذه الخطوات:
1. ✅ المشروع على GitHub
2. ✅ التطبيق مشروع على Streamlit Cloud
3. ✅ أي تحديث محلي سيُنشر تلقائياً
4. ✅ الإضافة تبقى بدون أي تأثر
