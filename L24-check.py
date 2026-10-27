import sys
import time

print("\n" + "═" * 62)
print("  فحص ميزة /history")
print("═" * 62)

try:
    import httpx
except ImportError:
    print("\n  ✗ مكتبة httpx مش مثبّتة.   pip install httpx\n")
    sys.exit()

if len(sys.argv) < 3:
    print("\n  ✗ ناقص معلومات.")
    print('\n    python L24-check.py <رابطك> "<سؤالك>"')
    print('\n    مثال:')
    print('    python L24-check.py http://127.0.0.1:8099 "الدوام"\n')
    sys.exit()

BASE = sys.argv[1].strip().rstrip("/")
if not BASE.startswith("http"):
    BASE = "https://" + BASE
سؤال = sys.argv[2].strip()

print(f"\n  المشروع : {BASE}")
print(f"  السؤال  : {سؤال}\n")


def جيب(مسار, **params):
    try:
        return httpx.get(BASE + مسار, params=params or None,
                         timeout=40, follow_redirects=True)
    except Exception as e:
        return e


def رمز(r):
    return r.status_code if isinstance(r, httpx.Response) else 0


def جسم(r):
    if not isinstance(r, httpx.Response):
        return {}
    try:
        return r.json()
    except Exception:
        return {}


# الخدمة ممكن تكون نايمة (Render)
for محاولة in range(1, 8):
    ص = جيب("/health")
    if isinstance(ص, httpx.Response) and ص.status_code < 500:
        break
    print(f"  … محاولة {محاولة} — الخدمة لسا بتصحى، بنستنّى")
    time.sleep(10)

if not isinstance(ص, httpx.Response):
    print("\n  ✗ ما قدرت أوصل للخدمة أبداً.")
    print(f"    {type(ص).__name__}: {ص}\n")
    sys.exit()

# ── المسار موجود أصلاً؟ ──
أولي = جيب("/history")
موجود = رمز(أولي) == 200

# ── نسأل بترتيب معروف ──
جيب("/ask", q=سؤال)
time.sleep(0.4)
جيب("/ask", q="zzz-مش-موجود-أبداً-9q7x")
time.sleep(0.4)
علامة = f"{سؤال} -آخر-سؤال"
جيب("/ask", q=علامة)

ر = جيب("/history")
ج = جسم(ر)
بنود = ج.get("items") if isinstance(ج.get("items"), list) else None
عدد = ج.get("count")

أول_بند = بنود[0] if بنود else {}
أسئلة = [str(b.get("question", "")) for b in بنود if isinstance(b, dict)] \
    if بنود else []
أكواد = [b.get("status") for b in بنود if isinstance(b, dict)] \
    if بنود else []

# ── الأجدد أول؟ ──
الأجدد_أول = bool(أسئلة) and علامة in أسئلة[0]

# ── الحدّ ٢٠ ──
فوق_الحد = None
if بنود is not None:
    for i in range(24):
        جيب("/ask", q=f"ملء-{i}")
    ب2 = جسم(جيب("/history")).get("items")
    فوق_الحد = isinstance(ب2, list) and len(ب2) <= 20

# ── ما خرّب الموجود ──
بعد_ask = جيب("/ask", q=سؤال)
ج_ask = جسم(بعد_ask)
بعد_metrics = جسم(جيب("/metrics"))
بعد_health = جيب("/health")

بنود_الفحص = [
    ("المسار /history موجود وبيرجّع 200", موجود),
    ("الردّ فيه items وهي قائمة", بنود is not None),
    ("وفيه count وهو رقم", isinstance(عدد, int)),
    ("و count بيطابق طول items",
     isinstance(عدد, int) and بنود is not None and عدد == len(بنود)),
    ("وفيه ٣ أسئلة على الأقل", bool(بنود) and len(بنود) >= 3),
    ("وكل بند فيه question و status",
     bool(أول_بند) and "question" in أول_بند and "status" in أول_بند),
    ("والأجدد أول — آخر سؤال سألته بالأعلى", الأجدد_أول),
    ("وسجّل الـ 404 كمان مش بس الناجح", 404 in أكواد),
    ("والسجل ما بيزيد عن ٢٠ بند", فوق_الحد),
    ("ولسا /ask شغّال وبيرجّع جواب ومصادر",
     رمز(بعد_ask) == 200 and bool(ج_ask.get("answer"))
     and "sources" in ج_ask),
    ("ولسا /metrics شغّال وفيه requests_total",
     isinstance(بعد_metrics.get("requests_total"), int)),
    ("ولسا /health شغّال", رمز(بعد_health) == 200),
]

ناجح = 0
for ن_ص, ok in بنود_الفحص:
    رمز_ = "–" if ok is None else ("✓" if ok else "✗")
    print(f"  {رمز_} {ن_ص}")
    ناجح += 1 if ok else 0

print(f"\n  ══ المجموع: {ناجح} / {len(بنود_الفحص)} ══")

# ─────────── التشخيص ───────────
print("\n" + "─" * 62)
print("  شو شفت")
print("─" * 62)
print(f"  /history        → {رمز(أولي)}")
if isinstance(ر, httpx.Response):
    print(f"  أول ١٥٠ حرف    → {ر.text.strip()[:150]}")
if أسئلة:
    print(f"\n  أول ٤ أسئلة بالسجل (الأجدد أول):")
    for s_ in أسئلة[:4]:
        print(f"      {s_[:50]}")

if not موجود:
    print("\n  ⚠ المسار /history مش موجود.")
    print("    يعني الوكيل ما بناه · أو بناه وما نشرت التعديل.")
    print("    تأكّد إنك عملت commit و push ورفعت على Render.")
elif not الأجدد_أول:
    print("\n  ⚠ الترتيب معكوس — الأقدم بالأعلى.")
    print("    هاد أشيع غلط. اعطِ الوكيل الملاحظة بالضبط:")
    print('    «بدي الأجدد أول بالقائمة مش آخرها»')

print()
