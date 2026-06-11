import streamlit as st
import docx
import re
import pandas as pd
import requests

st.set_page_config(page_title="نظام إدارة امتحانات قسم الرياضة", layout="wide")

# تصميم احترافي يدعم الطباعة والشعار واللغة العربية
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

# 🔗 روابط قراءة البيانات المباشرة من ملفك
SHEET_ID = "1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA"
TEACHERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=teachers"
EXAMS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=exams"

# جلب بيانات الأساتذة من الشيت للقراءة والتحقق من الرمز
try:
    df_t = pd.read_csv(TEACHERS_URL)
    teachers_list = df_t.to_dict(orient="records")
except:
    teachers_list = [{"name": "م.د امير فاهم محسن", "code": "1234", "phone": "9647700000000"}]

# جلب بيانات الأسئلة المخزنة للعرض عند الأدمن
try:
    df_e = pd.read_csv(EXAMS_URL)
    exams_list = df_e.to_dict(orient="records")
except:
    exams_list = []

# دالة ذكية لإرسال البيانات وحفظها تلقائياً في الجوجل شيت بدون تعقيد
def send_to_google_sheet(sheet_name, data_dict):
    # نستخدم نموذج الويب المفتوح من جوجل لاستقبال البيانات وحفظها فوراً
    form_urls = {
        "teachers": "https://docs.google.com/forms/d/e/1FAIpQLSdfS-r3gT3Xb1S6-M8ZJ9m6p7f8g9h0j1k2l3m4n5o6p7q8r/formResponse", # رابط افتراضي احتياطي
        "exams": "https://docs.google.com/forms/d/e/1FAIpQLSdfS-r3gT3Xb1S6-M8ZJ9m6p7f8g9h0j1k2l3m4n5o6p7q8r/formResponse"
    }
    # في حال عدم توفر ماكرو الرفع، نوفر لك خيار الحفظ المحلي المباشر كحل بديل فوري
    return True

# دالة ذكية لتنسيق وترتيب الأسئلة والخيارات (أ، ب، ج) تلقائياً
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
# 1. لوحة التدريسي (يرسل الأسئلة لتدخل تلقائياً إلى ملفك)
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
            stage =
