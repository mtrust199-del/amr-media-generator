# Amr Cloud Control

مركز التحكم السحابي المتكامل لمشروع Amr Media Generator.

## المميزات

- **Cloud Control**: دردشة فورية مع ترجمة آلية (عربي ↔ إنجليزي)
- **Temp Mail**: بريد مؤقت مدمج عبر iframe
- **Control Panel**: لوحة تحكم رئيسية للنظام
- **GitHub Pages**: استضافة سحابية سريعة
- **Local Backend**: ربط مع النظام المحلي (Flask)

## هيكل الموقع

```
cloud_site/
├── index.html              # الصفحة الرئيسية (الهب)
├── cloud-control.html      # صفحة التحكم السحابي
├── temp-mail.html         # صفحة البريد المؤقت
├── control-panel.html     # لوحة التحكم
├── css/
│   └── style.css       # الأنماط المشتركة
├── js/
│   └── main.js         # كود JavaScript الرئيسي
└── README.md            # هذا الملف
```

## التشغيل المحلي

1. تأكد من تشغيل النظام المحلي:
   ```bash
   cd "D:/All DATA/claude project/generat photo and video"
   python app.py
   ```

2. افتح الموقع السحابي:
   - الصفحة الرئيسية: `index.html`
   - أو عبر GitHub Pages: `https://mtrust199-del.github.io/amr-cloud-site/`

## النشر على GitHub Pages

1. أنشئ مستودع جديد (إذا لم يكن موجوداً):
   ```bash
   cd cloud_site
   git init
   git add .
   git commit -m "Initial commit: Amr Cloud Control"
   gh repo create mtrust199-del/amr-cloud-site --public
   git remote add origin https://github.com/mtrust199-del/amr-cloud-site.git
   git push -u origin main
   ```

2. فعل GitHub Pages:
   - اذهب إلى إعدادات المستودع (Settings → Pages)
   - اختر فرع `main` كمصدر للصفحات
   - احفظ الإعدادات

3. الموقع سيصبح متاحاً على: `https://mtrust199-del.github.io/amr-cloud-site/`

## الربط مع النظام المحلي

- زر **"فتح النظام المحلي"** في الموقع السحابي سيوجهك إلى `http://127.0.0.1:5000/`
- تأكد من تشغيل `app.py` محلياً قبل النقر على الروابط المحلية

## المتطلبات

- متصفح حديث يدعم JavaScript
- النظام المحلي (Flask) يعمل على المنفذ 5000
- اتصال بالإنترنت للوصول إلى Google Translate و Temp Mail

## الترخيص

جميع الحقوق محفوظة © 2026 Amr Media Generator
