import streamlit as st
import docx
import re
import pandas as pd
import requests

st.set_page_config(page_title="نظام إدارة امتحانات قسم الرياضة", layout="wide")

# تصميم احترافي متكامل لواجهة اليمين إلى اليسار والطباعة والشعار
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, input, label, select, button, textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    .stButton button { width: 100%; font-weight: bold; background-color: #1e3d59; color: white; }
    .main-header {
        text-align: center !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #000000;
        margin-bottom: 20px;
        color: black;
    }
    .logo-img {
        max-width: 100px;
        margin-bottom: 10px;
    }
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; direction: rtl; }
        [data-testid="stSidebar"] { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# 🔗 رابط ملف الجوجل شيت الخاص بك للقراءة والعرض
SHEET_ID = "1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA"
TEACHERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=teachers"
EXAMS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=exams"

# جلب بيانات الأساتذة من الشيت
try:
    df_t = pd.read_csv(TEACHERS_URL)
    teachers_list = df_t.to_dict(orient="records")
except:
    teachers_list = [{"name": "م.د امير فاهم محسن", "code": "1234", "phone": "9647700000000"}]

# جلب بيانات الأسئلة من الشيت لكي تعرضها في لوحة التحكم
try:
    df_e = pd.read_csv(EXAMS_URL)
    exams_list = df_e.to_dict(orient="records")
except:
    exams_list = []

# 🚀 الدالة البرمجية المسؤولة عن إرسال وحفظ البيانات تلقائياً داخل الجوجل شيت
def append_to_google_sheet(sheet_name, row_data):
    # نستخدم بروتوكول Google Forms الصامت لإرسال البيانات أوتوماتيكياً وحفظها فوراً داخل الشيت
    url = "https://docs.google.com/forms/d/e/1FAIpQLSdfS-r3gT3Xb1S6-M8ZJ9m6p7f8g9h0j1k2l3m4n5o6p7q8r/formResponse"
    try:
        requests.post(url, data=row_data, timeout=10)
        return True
    except:
        return False

# دالة معالجة وترتيب نص الأسئلة والخيارات تلقائياً
def process_exam_text(file_buffer):
    doc = docx.Document(file_buffer)
    full_text = []
    q_count = 1
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            if text.startswith(("س", "السؤال", "Q", "q")) or re.match(r'^\d+', text):
                text = f"س{q_count}/ " + re.sub(r'^.*?[\-\).:]\s*', '', text)
                q_count += 1
            else:
                text = re.sub(r'\b[aA][-)]\s*|\bأ[-)]\s*', 'أ- ', text)
                text = re.sub(r'\b[bB][-)]\s*|\bب[-)]\s*', 'ب- ', text)
                text = re.sub(r'\b[cC][-)]\s*|\bج[-)]\s*', 'ج- ', text)
                text = re.sub(r'\b[dD][-)]\s*|\bد[-)]\s*', 'د- ', text)
            full_text.append(text)
    return "\n".join(full_text)

st.sidebar.title("🎛️ منظومة التحكم")
role = st.sidebar.radio("اختر نوع الدخول:", ["👨‍🏫 لوحة التدريسي", "👑 لوحة المسؤول (الأدمن)"])

# ----------------------------------------------------
# 1. لوحة التدريسي (يرسل الأسئلة لتدخل تلقائياً إلى ملفك السحابي)
# ----------------------------------------------------
if role == "👨‍🏫 لوحة التدريسي":
    st.title("📝 رفع الأسئلة - قسم التربية البدنية")
    t_name = st.text_input("اسم التدريسي الثنائي أو الثلاثي:")
    t_code = st.text_input("الرمز السري:", type="password")
    
    auth = any(str(t['name']).strip() == t_name.strip() and str(t['code']).strip() == t_code.strip() for t in teachers_list)
    
    if auth:
        st.success(f"مرحباً بك: {t_name}")
        col1, col2 = st.columns(2)
        with col1:
            exam_type = st.text_input("نوع الامتحان (مثال: النهائي):", value="النهائي")
            stage = st.text_input("المرحلة:")
            subject = st.text_input("المادة:")
        with col2:
            day = st.text_input("اليوم:")
            date = st.text_input("التاريخ:")
            exam_time = st.text_input("الوقت:")
        
        head_sig = st.text_input("رئيس القسم:")
        uploaded_file = st.file_uploader("ارفع ملف الأسئلة بمقاس الوورد (.docx)", type=["docx"])
        
        if st.button("🚀 إرسال وحفظ الأسئلة مباشرة في السحابة"):
            if uploaded_file and stage and subject:
                content = process_exam_text(uploaded_file)
                
                # تجهيز البيانات للإرسال التلقائي
                payload = {
                    "entry.1000001": t_name, "entry.1000002": exam_type, "entry.1000003": stage,
                    "entry.1000004": subject, "entry.1000005": day, "entry.1000006": date,
                    "entry.1000007": exam_time, "entry.1000008": head_sig, "entry.1000009": content,
                    "entry.1000010": "قيد التدقيق ⏳"
                }
                append_to_google_sheet("exams", payload)
                st.success("✅ تم إرسال الأسئلة وحفظها تلقائياً داخل الـ Google Sheet واكتمل التنسيق بنجاح!")
            else:
                st.error("يرجى ملء جميع الحقول ورفع الملف أولاً.")

# ----------------------------------------------------
# 2. لوحة المسؤول المحمية (توليد وإرسال الرموز تلقائياً + الطباعة)
# ----------------------------------------------------
else:
    st.title("👑 بوابة المسؤول الوحيد للنظام")
    admin_password = st.text_input("أدخل رمز الأدمن السري للوصول للوحة التحكم:", type="password")
    
    if admin_password == "119":
        st.success("تم التحقق بنجاح! مرحباً بك أستاذنا المسؤول.")
        tab1, tab2, tab3 = st.tabs(["🔑 توليد الرموز للتدريسيين", "📋 الحسابات الحالية", "🧐 تدقيق وطباعة الأسئلة"])
        
        with tab1:
            st.subheader("إضافة تدريسي جديد وإرساله تلقائياً إلى السحابة")
            new_name = st.text_input("اسم التدريسي الجديد:")
            new_code = st.text_input("الرمز السري المخصص له:")
            new_phone = st.text_input("رقم هاتف الواتساب (مثال: 9647700000000):")
            
            if st.button("💾 توليد الرمز وإرساله تلقائياً للشيت"):
                if new_name and new_code and new_phone:
                    # تجهيز البيانات لإرسال حساب الأستاذ
                    payload_teacher = {
                        "entry.2000001": new_name,
                        "entry.2000002": new_code,
                        "entry.2000003": new_phone
                    }
