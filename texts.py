"""All bot copy in one place, keyed by language code.

To add a new language: add a new key (e.g. "fr") with the same set of
keys as "ar" / "en" below, then it becomes selectable by extending the
language keyboard in keyboards.py.
"""

TEXTS = {
    "ar": {
        "choose_language": "👋 أهلاً بك! اختر لغتك المفضلة:\nWelcome! Please choose your language:",
        "welcome": (
            "🚀 أهلاً بك في <b>Oonyx Ai Bot</b>!\n\n"
            "قناتنا الخاصة تمنحك:\n"
            "📈 إشارات تداول احترافية يومية بدقة عالية\n"
            "🎯 نقاط دخول وخروج وأهداف واضحة لكل صفقة\n"
            "🛡️ إدارة مخاطر ووقف خسارة لكل توصية\n"
            "👨‍💻 دعم فني ومتابعة مباشرة من فريق متخصص\n\n"
            "اختر خطة الاشتراك المناسبة لك:"
        ),
        "btn_trial": "🎁 تجربة مجانية 7 أيام",
        "btn_monthly": "💳 شهري - $49",
        "btn_quarterly": "💳 ربع سنوي - $120",
        "btn_yearly": "💳 سنوي - $399",
        "trial_already_used": "⚠️ لقد استخدمت التجربة المجانية من قبل. يمكنك الاشتراك في إحدى الخطط المدفوعة.",
        "trial_activating": "⏳ جاري تفعيل تجربتك المجانية...",
        "trial_activated": (
            "🎉 تم تفعيل تجربتك المجانية لمدة {days} أيام بنجاح!\n\n"
            "🔗 رابط الانضمام للقناة (استخدام واحد فقط):\n{invite_link}"
        ),
        "payment_intro": (
            "💰 قيمة الاشتراك: <b>${price}</b>\n\n"
            "اختر طريقة الدفع المناسبة لك:"
        ),
        "btn_pay_trc20": "🔸 USDT (TRC20)",
        "btn_pay_bep20": "🔸 USDT (BEP20)",
        "btn_pay_binance": "🔸 تحويل داخلي عبر Binance UID",
        "payment_method_sent": "✅ تم إرسال بيانات الدفع أعلاه.",
        "wallet_label_trc20": "🔸 USDT (TRC20):",
        "wallet_label_bep20": "🔸 USDT (BEP20):",
        "wallet_label_binance": "🔸 تحويل داخلي عبر Binance UID:",
        "payment_footer_trc20": (
            "⚠️ <b>تنبيه مهم:</b> تأكد تمامًا إنك ترسل التحويل عبر شبكة <b>TRC20 (Tron)</b> فقط. "
            "إرسال الأموال عبر شبكة خاطئة قد يؤدي لخسارتها بشكل نهائي ولا يمكن استرجاعها أبدًا.\n\n"
            "بعد إتمام التحويل، أرسل لنا <b>صورة سكرين شوت</b> لإثبات الدفع مباشرة في هذه المحادثة "
            "(بدون الحاجة لكتابة أي رقم يدويًا)، وسنتحقق من عملية الدفع تلقائيًا.\n\n"
            "✅ بمجرد التحقق من الدفع تلقائيًا، بنضيفك فورًا للقناة الخاصة بدون أي تدخل بشري."
        ),
        "payment_footer_bep20": (
            "⚠️ <b>تنبيه مهم:</b> تأكد تمامًا إنك ترسل التحويل عبر شبكة <b>BEP20 (BSC)</b> فقط. "
            "إرسال الأموال عبر شبكة خاطئة قد يؤدي لخسارتها بشكل نهائي ولا يمكن استرجاعها أبدًا.\n\n"
            "بعد إتمام التحويل، أرسل لنا <b>صورة سكرين شوت</b> لإثبات الدفع مباشرة في هذه المحادثة "
            "(بدون الحاجة لكتابة أي رقم يدويًا)، وسنتحقق من عملية الدفع تلقائيًا.\n\n"
            "✅ بمجرد التحقق من الدفع تلقائيًا، بنضيفك فورًا للقناة الخاصة بدون أي تدخل بشري."
        ),
        "payment_footer_binance": (
            "ℹ️ التحويل الداخلي عبر Binance UID لا يظهر على أي بلوكتشين عام، لذلك يحتاج "
            "دائمًا مراجعة يدوية من فريقنا (وليس تفعيلاً تلقائيًا فوريًا).\n\n"
            "بعد إتمام التحويل، أرسل لنا <b>صورة سكرين شوت</b> لإثبات الدفع مباشرة في هذه المحادثة، "
            "وبنفعّل اشتراكك بأسرع وقت ممكن بعد المراجعة."
        ),
        "no_pending_payment": "ℹ️ لا يوجد لديك طلب دفع بانتظار المراجعة. أرسل /start لاختيار خطة اشتراك أولاً.",
        "processing_screenshot": "⏳ جاري التحقق من إثبات الدفع تلقائيًا، الرجاء الانتظار قليلاً...",
        "payment_verified": (
            "✅ تم التحقق من دفعتك وتفعيل اشتراكك بنجاح!\n\n"
            "📦 الخطة: {plan}\n"
            "📅 تنتهي بتاريخ: {expires_at}\n\n"
            "🔗 رابط الانضمام للقناة (استخدام واحد فقط):\n{invite_link}"
        ),
        "payment_pending_review": (
            "📨 تم استلام إثبات الدفع وتحويله لفريقنا للمراجعة اليدوية "
            "(هذا يحدث تلقائيًا في حال كانت العملية تحويل داخلي عبر Binance UID، أو إذا لم تكن الصورة واضحة بما يكفي). "
            "سنقوم بتفعيل اشتراكك بمجرد التأكد من الدفع."
        ),
        "payment_rejected": (
            "❌ للأسف لم نتمكن من تأكيد عملية الدفع الخاصة بك. "
            "الرجاء التأكد من صحة التحويل والمحاولة مرة أخرى، أو التواصل مع الدعم."
        ),
        "status_none": "ℹ️ ليس لديك اشتراك حاليًا. أرسل /start لاختيار خطة.",
        "status_active": "✅ اشتراكك فعّال حاليًا.\n📦 الخطة: {plan}\n📅 ينتهي بتاريخ: {expires_at}",
        "status_expired": "⌛ اشتراكك منتهي. أرسل /start للتجديد.",
        "subscription_expired_notice": (
            "⌛ انتهى اشتراكك في قناة Oonyx Ai Bot وتم إزالتك من القناة الخاصة.\n"
            "أرسل /start لتجديد اشتراكك والعودة فورًا."
        ),
        "generic_error": "⚠️ حدث خطأ غير متوقع، الرجاء المحاولة لاحقًا أو التواصل مع الدعم.",
        "plan_name_trial": "تجربة مجانية",
        "plan_name_monthly": "شهري",
        "plan_name_quarterly": "ربع سنوي",
        "plan_name_yearly": "سنوي",
    },
    "en": {
        "choose_language": "👋 Welcome! Please choose your language:\nاختر لغتك المفضلة:",
        "welcome": (
            "🚀 Welcome to <b>Oonyx Ai Bot</b>!\n\n"
            "Our private channel gives you:\n"
            "📈 Professional, high-accuracy daily trading signals\n"
            "🎯 Clear entry, exit and target points for every trade\n"
            "🛡️ Risk management and stop-loss on every call\n"
            "👨‍💻 Direct support from a dedicated team\n\n"
            "Choose the subscription plan that fits you:"
        ),
        "btn_trial": "🎁 7-Day Free Trial",
        "btn_monthly": "💳 Monthly - $49",
        "btn_quarterly": "💳 Quarterly - $120",
        "btn_yearly": "💳 Yearly - $399",
        "trial_already_used": "⚠️ You've already used your free trial. Please choose a paid plan.",
        "trial_activating": "⏳ Activating your free trial...",
        "trial_activated": (
            "🎉 Your {days}-day free trial has been activated!\n\n"
            "🔗 Channel invite link (single use):\n{invite_link}"
        ),
        "payment_intro": (
            "💰 Plan price: <b>${price}</b>\n\n"
            "Choose the payment method that suits you:"
        ),
        "btn_pay_trc20": "🔸 USDT (TRC20)",
        "btn_pay_bep20": "🔸 USDT (BEP20)",
        "btn_pay_binance": "🔸 Internal Binance transfer (UID)",
        "payment_method_sent": "✅ Payment details sent above.",
        "wallet_label_trc20": "🔸 USDT (TRC20):",
        "wallet_label_bep20": "🔸 USDT (BEP20):",
        "wallet_label_binance": "🔸 Internal Binance transfer (UID):",
        "payment_footer_trc20": (
            "⚠️ <b>Important:</b> Make sure you send the transfer on the <b>TRC20 (Tron)</b> "
            "network only. Sending funds on the wrong network can result in permanent, "
            "unrecoverable loss.\n\n"
            "After completing the transfer, just send us a <b>screenshot</b> as proof of payment "
            "directly in this chat (no need to type any number manually), and we'll verify it automatically.\n\n"
            "✅ As soon as the payment is verified automatically, you'll be added to the private "
            "channel instantly, with no human involved."
        ),
        "payment_footer_bep20": (
            "⚠️ <b>Important:</b> Make sure you send the transfer on the <b>BEP20 (BSC)</b> "
            "network only. Sending funds on the wrong network can result in permanent, "
            "unrecoverable loss.\n\n"
            "After completing the transfer, just send us a <b>screenshot</b> as proof of payment "
            "directly in this chat (no need to type any number manually), and we'll verify it automatically.\n\n"
            "✅ As soon as the payment is verified automatically, you'll be added to the private "
            "channel instantly, with no human involved."
        ),
        "payment_footer_binance": (
            "ℹ️ Internal Binance UID transfers never appear on any public blockchain, so they "
            "always require manual review from our team (not instant automatic activation).\n\n"
            "After completing the transfer, just send us a <b>screenshot</b> as proof of payment "
            "directly in this chat, and we'll activate your subscription as soon as possible "
            "after review."
        ),
        "no_pending_payment": "ℹ️ You don't have a pending payment request. Send /start to choose a plan first.",
        "processing_screenshot": "⏳ Verifying your payment proof automatically, please wait a moment...",
        "payment_verified": (
            "✅ Your payment has been verified and your subscription is now active!\n\n"
            "📦 Plan: {plan}\n"
            "📅 Expires on: {expires_at}\n\n"
            "🔗 Channel invite link (single use):\n{invite_link}"
        ),
        "payment_pending_review": (
            "📨 Your payment proof was received and forwarded to our team for manual review "
            "(this happens automatically for internal Binance UID transfers, or if the screenshot isn't clear enough). "
            "We'll activate your subscription as soon as the payment is confirmed."
        ),
        "payment_rejected": (
            "❌ Unfortunately we couldn't confirm your payment. "
            "Please double-check the transfer and try again, or contact support."
        ),
        "status_none": "ℹ️ You don't have an active subscription. Send /start to choose a plan.",
        "status_active": "✅ Your subscription is active.\n📦 Plan: {plan}\n📅 Expires on: {expires_at}",
        "status_expired": "⌛ Your subscription has expired. Send /start to renew.",
        "subscription_expired_notice": (
            "⌛ Your Oonyx Ai Bot subscription has expired and you've been removed from the private channel.\n"
            "Send /start to renew and rejoin instantly."
        ),
        "generic_error": "⚠️ An unexpected error occurred. Please try again later or contact support.",
        "plan_name_trial": "Free Trial",
        "plan_name_monthly": "Monthly",
        "plan_name_quarterly": "Quarterly",
        "plan_name_yearly": "Yearly",
    },
}
