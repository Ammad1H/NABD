"""English/Arabic UI strings for the NABD app."""

STRINGS = {
    "title": {"en": "NABD: Respiratory Season Forecasts", "ar": "نبض: توقعات موسم أمراض الجهاز التنفسي"},
    "subtitle": {"en": "Calibrated RSV and influenza forecasts with human-approved actions",
                 "ar": "توقعات معايَرة للفيروس المخلوي التنفسي والإنفلونزا مع إجراءات يعتمدها الإنسان"},
    "demo_banner": {"en": "DEMO DATA: some panels use placeholder data because model results are not yet in results/. Not NABD output.",
                    "ar": "بيانات تجريبية: بعض اللوحات تستخدم بيانات مؤقتة لعدم توفر نتائج النموذج بعد. ليست مخرجات نبض."},
    "simulated": {"en": "SIMULATED", "ar": "محاكاة"},
    "nav_card": {"en": "Weekly card", "ar": "البطاقة الأسبوعية"},
    "nav_us": {"en": "US proof", "ar": "الإثبات الأمريكي"},
    "nav_ledger": {"en": "Ledger receipt", "ar": "إيصال السجل"},
    "nav_ablation": {"en": "Feed removal", "ar": "إزالة مصدر البيانات"},
    "nav_workforce": {"en": "Workforce (simulated)", "ar": "القوى العاملة (محاكاة)"},
    "nav_about": {"en": "About & limitations", "ar": "حول النظام والقيود"},
    "freshness": {"en": "Data freshness", "ar": "حداثة البيانات"},
    "last_week": {"en": "Last published week", "ar": "آخر أسبوع منشور"},
    "lag": {"en": "Lag", "ar": "التأخير"},
    "days": {"en": "days", "ar": "أيام"},
    "expected": {"en": "expected", "ar": "المتوقع"},
    "stale": {"en": "STALE: older than expected", "ar": "قديمة: أقدم من المتوقع"},
    "fresh": {"en": "Within expected publication lag", "ar": "ضمن تأخير النشر المتوقع"},
    "rsv": {"en": "RSV positivity (sentinel, %)", "ar": "نسبة إيجابية الفيروس المخلوي التنفسي (رصد، %)"},
    "flu": {"en": "Influenza positivity (sentinel, %)", "ar": "نسبة إيجابية الإنفلونزا (رصد، %)"},
    "horizon": {"en": "Horizon (relative to issue date)", "ar": "الأفق (نسبة إلى تاريخ الإصدار)"},
    "median": {"en": "Median", "ar": "الوسيط"},
    "band80": {"en": "80% band", "ar": "نطاق 80%"},
    "band95": {"en": "95% band", "ar": "نطاق 95%"},
    "persistence": {"en": "Persistence (no-change) forecast", "ar": "توقع الاستمرارية (بلا تغيير)"},
    "drivers": {"en": "Drivers", "ar": "العوامل المؤثرة"},
    "action": {"en": "Proposed playbook action", "ar": "الإجراء المقترح من دليل العمل"},
    "illustrative": {"en": "ILLUSTRATIVE playbook: pending clinical and public-health review",
                     "ar": "دليل عمل توضيحي: بانتظار المراجعة السريرية ومراجعة الصحة العامة"},
    "role": {"en": "Role", "ar": "الدور"},
    "approver": {"en": "Approver name (required)", "ar": "اسم المعتمِد (إلزامي)"},
    "decision": {"en": "Decision", "ar": "القرار"},
    "reason": {"en": "Reason code (required)", "ar": "رمز السبب (إلزامي)"},
    "note": {"en": "Note", "ar": "ملاحظة"},
    "modified": {"en": "Modified action (required for Modify)", "ar": "الإجراء المعدّل (إلزامي عند التعديل)"},
    "submit": {"en": "Record decision", "ar": "تسجيل القرار"},
    "recorded": {"en": "Decision recorded in the audit log", "ar": "تم تسجيل القرار في سجل التدقيق"},
    "audit": {"en": "Audit log (append-only, hash-chained)", "ar": "سجل التدقيق (إلحاق فقط، مترابط بالتجزئة)"},
    "approve": {"en": "Approve", "ar": "اعتماد"},
    "modify": {"en": "Modify", "ar": "تعديل"},
    "dismiss": {"en": "Dismiss", "ar": "رفض"},
    "verdict": {"en": "Pre-registered primary endpoint", "ar": "نقطة النهاية الأساسية المسجّلة مسبقاً"},
    "language": {"en": "Language", "ar": "اللغة"},
}


def t(key: str, lang: str) -> str:
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry["en"]
