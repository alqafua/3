# Oonyx Ai Bot

بوت تيليجرام لإدارة اشتراكات قناة إشارات تداول خاصة، مع تحقق تلقائي من الدفع عبر
OCR والبلوكتشين (TRC20 / BEP20)، ومراجعة يدوية احتياطية عبر الأدمن لأي حالة لا
يمكن التحقق منها تلقائيًا.

## المزايا

- اختيار لغة (عربي / إنجليزي) عبر أزرار Inline.
- تجربة مجانية 7 أيام (مرة واحدة فقط لكل مستخدم) وخطط شهري/ربع سنوي/سنوي.
- استلام سكرين شوت إثبات الدفع مباشرة (بدون كتابة أي رقم يدويًا).
- استخراج رقم المعاملة (TXID) من الصورة تلقائيًا عبر OCR (Tesseract).
- التحقق الفعلي من المعاملة على البلوكتشين:
  - **USDT-TRC20** عبر [TronGrid](https://www.trongrid.io/) (مجاني).
  - **USDT-BEP20** عبر [BscScan API](https://bscscan.com/apis) (يحتاج مفتاح مجاني).
- منع إعادة استخدام نفس TXID من قبل مستخدمين مختلفين.
- تفعيل فوري للاشتراك عند نجاح التحقق، مع رابط دعوة صالح لاستخدام واحد فقط
  (`create_chat_invite_link` مع `member_limit=1`).
- تحويل تلقائي لحساب الأدمن للمراجعة اليدوية عند فشل الاستخراج/التحقق، مع زري
  "تفعيل" و"رفض"، حتى لا يُرفض أي زبون حقيقي بالخطأ.
- أمر `/status` لعرض حالة الاشتراك وتاريخ الانتهاء.
- مهمة مجدولة كل ساعة (JobQueue) تطرد المشتركين المنتهية اشتراكاتهم تلقائيًا
  (ban ثم unban فورًا حتى يقدروا يرجعوا لاحقًا) وترسل لهم إشعار.

## ⚠️ ملاحظة مهمة جدًا: تحويلات Binance UID الداخلية

التحويل الداخلي عبر **Binance UID لا يظهر أبدًا على أي بلوكتشين عام** (لأنه
تحويل داخلي داخل نظام Binance فقط)، لذلك **لا يمكن التحقق منه تلقائيًا بأي
شكل من الأشكال**. أي سكرين شوت لتحويل UID سيتم تحويله تلقائيًا لمراجعة الأدمن
اليدوية دائمًا، وهذا سلوك متوقع وليس خطأ في البوت. تأكد أن حساب الأدمن
(`ADMIN_CHAT_ID`) نشط ويراجع طلبات التفعيل بانتظام.

## بنية المشروع

```
main.py                    # نقطة التشغيل: يربط الـ handlers والـ scheduler
config.py                  # تحميل متغيرات البيئة
database.py                # نماذج SQLAlchemy (users, used_transactions) ودوال مساعدة
texts.py                   # كل نصوص البوت (عربي/إنجليزي) في قاموس واحد
keyboards.py                # كل أزرار Inline
payment_verification.py    # OCR + التحقق من البلوكتشين (مستقل عن تيليجرام)
scheduler.py                # فحص الاشتراكات المنتهية والطرد التلقائي (كل ساعة)
handlers/
  start.py                  # /start، اختيار اللغة، /status
  plans.py                  # اختيار الخطة، تفعيل التجربة المجانية، تعليمات الدفع
  payment.py                 # استقبال السكرين شوت، التحقق، ومراجعة الأدمن
requirements.txt
.env.example
nixpacks.toml                # يثبت tesseract-ocr تلقائيًا على Railway
Procfile
```

## الإعداد المحلي

### 1. المتطلبات

- Python 3.11+
- Tesseract OCR مثبت على جهازك:
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`
  - Windows: نزّل المثبت من [هنا](https://github.com/UB-Mannheim/tesseract/wiki)
    وحدد مساره في متغير `TESSERACT_CMD` داخل `.env`

### 2. تثبيت المكتبات

```bash
python -m venv .venv
source .venv/bin/activate   # على Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

```bash
cp .env.example .env
```

ثم عبّي القيم في `.env`:

| المتغير | الوصف |
|---|---|
| `BOT_TOKEN` | توكن البوت من [@BotFather](https://t.me/BotFather) |
| `ADMIN_CHAT_ID` | معرف حساب/محادثة الأدمن (لاستقبال طلبات المراجعة اليدوية) |
| `VIP_CHANNEL_ID` | معرف القناة الخاصة (رقم يبدأ بـ `-100...`) |
| `DATABASE_URL` | رابط قاعدة البيانات (SQLite افتراضيًا، PostgreSQL في الإنتاج) |
| `TRC20_WALLET` | عنوان محفظة USDT-TRC20 |
| `BSC_WALLET` | عنوان محفظة USDT-BEP20 |
| `BINANCE_UID` | معرف Binance للتحويلات الداخلية |
| `BSCSCAN_API_KEY` | مفتاح مجاني من [bscscan.com/apis](https://bscscan.com/apis) |
| `PRICE_MONTHLY` / `PRICE_QUARTERLY` / `PRICE_YEARLY` | أسعار الخطط بالدولار |
| `TRIAL_DAYS` | مدة التجربة المجانية بالأيام |
| `PAYMENT_AMOUNT_TOLERANCE` | هامش السماح عند مطابقة المبلغ المحوّل بالدولار |
| `SCHEDULER_INTERVAL_SECONDS` | فترة فحص الاشتراكات المنتهية بالثواني |
| `SUPPORT_USERNAME` | معرف تيليجرام (بدون @) اللي يفتح عليه زر "الدعم" |

### 4. تجهيز البوت في BotFather

- أنشئ البوت وخذ التوكن.
- أضف البوت كأدمن في القناة الخاصة (`VIP_CHANNEL_ID`) مع صلاحية دعوة المستخدمين
  وحظرهم (Invite Users + Ban Users) حتى يقدر ينشئ روابط الدعوة ويطرد المشتركين
  المنتهية اشتراكاتهم.

### 5. التشغيل

```bash
python main.py
```

## النشر على Railway

1. أنشئ مشروع جديد على [Railway](https://railway.app) واربطه بمستودع GitHub
   `onward-signals-bot`.
2. **مهم:** Railway يبني المشروع افتراضيًا بواسطة **Railpack** (وليس
   Nixpacks)، وRailpack لا يقرأ ملف `nixpacks.toml` إطلاقًا. لتثبيت
   `tesseract-ocr` (مطلوب لميزة OCR) أضف متغير البيئة التالي من تبويب
   **Variables**:
   ```
   RAILPACK_DEPLOY_APT_PACKAGES=tesseract-ocr
   ```
   بدون هذا المتغير، أي محاولة OCR ستفشل بخطأ tesseract غير موجود، وكل
   طلبات الدفع ستتحول تلقائيًا لمراجعة الأدمن اليدوية حتى لو كانت صحيحة.
3. من نفس تبويب **Variables** أضف كل المتغيرات الموجودة في `.env.example`
   بقيمها الحقيقية.
4. إذا كنت تريد استخدام PostgreSQL بدل SQLite (موصى به في الإنتاج لأن
   القرص في Railway غير دائم افتراضيًا لخدمات worker):
   - أضف خدمة PostgreSQL من Railway.
   - انسخ متغير `DATABASE_URL` الذي يوفره Railway والصقه كما هو في متغيرات
     البوت.
5. تأكد أن نوع الخدمة **Worker** (وليس Web) لأن البوت يعمل بـ polling وليس
   بخادم HTTP — ملف `Procfile` معرّف بالفعل بـ `worker: python main.py`.
6. بعد أول نشر ناجح، تحقق من الـ Logs للتأكد من ظهور رسالة
   `Oonyx Ai Bot starting...` بدون أخطاء.

## ملاحظات أمنية

- لا يحتوي الكود على أي مفاتيح أو توكنات حقيقية؛ كل القيم الحساسة تُقرأ من
  `.env` (محليًا) أو من متغيرات البيئة في Railway (في الإنتاج).
- ملف `.gitignore` يستثني `.env` و`__pycache__` وملفات قاعدة البيانات المحلية
  (`*.db`) من الرفع لـ GitHub.

## إضافة لغة جديدة

أضف مفتاحًا جديدًا في `texts.py` (مثلًا `"fr"`) يحتوي على نفس المفاتيح
الموجودة في `"ar"` و`"en"`، ثم أضف زرًا له في `language_keyboard()` داخل
`keyboards.py`.
