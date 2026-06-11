import streamlit as st
import docx
import re
import pandas as pd
from streamlit_gsheets import GSheetsConnection

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
    /* إعدادات خاصة بالطباعة لجعل الأسئلة تخرج كورقة رسمية */
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; direction: rtl; }
        [data-testid="stSidebar"] { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 🔗 رابط ملف الجوجل شيت الخاص بك مدمجاً تلقائياً هنا
# ----------------------------------------------------
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA/edit?usp=sharing"

# الاتصال الذكي والآمن بجوجل شيت مع تفادي الأخطاء
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_t = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="teachers")
    teachers_list = df_t.to_dict(orient="records")
except:
    teachers_list = [{"name": "م.د امير فاهم محسن", "code": "1234", "phone": "9647700000000"}]

try:
    df_e = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet="exams")
    exams_list = df_e.to_dict(orient="records")
except:
    exams_list = []

# دالة ذكية لترتيب وتنسيق الأسئلة والخيارات (أ، ب، ج)
def process_exam_text(file_buffer):
    doc = docx.Document(file_buffer)
    full_text = []
    q_count = 1
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            # التعرف على الأسئلة وترتيبها تلقائياً
            if text.startswith(("س", "السؤال", "Q", "q")) or re.match(r'^\d+', text):
                text = f"س{q_count}/ " + re.sub(r'^.*?[\-\).:]\s*', '', text)
                q_count += 1
            else:
                # ترتيب وتنسيق الخيارات بالتتابع
                text = re.sub(r'\b[aA][-)]\s*|\bأ[-)]\s*', 'أ- ', text)
                text = re.sub(r'\b[bB][-)]\s*|\bب[-)]\s*', 'ب- ', text)
                text = re.sub(r'\b[cC][-)]\s*|\bج[-)]\s*', 'ج- ', text)
                text = re.sub(r'\b[dD][-)]\s*|\bد[-)]\s*', 'د- ', text)
            full_text.append(text)
    return "\n".join(full_text)

st.sidebar.title("🎛️ منظومة التحكم")
role = st.sidebar.radio("اختر نوع الدخول:", ["👨‍🏫 لوحة التدريسي", "👑 لوحة المسؤول (الأدمن)"])

# ----------------------------------------------------
# 1. لوحة التدريسي (يرفع الأسئلة لترسل إليك مباشرة)
# ----------------------------------------------------
if role == "👨‍🏫 لوحة التدريسي":
    st.title("📝 رفع الأسئلة - قسم التربية البدنية")
    t_name = st.text_input("اسم التدريسي الثنائي أو الثلاثي:")
    t_code = st.text_input("الرمز السري:", type="password")
    
    auth = any(str(t['name']).strip() == t_name.strip() and str(t['code']).strip() == t_code.strip() for t in teachers_list)
    
    if auth:
        st.success(f"مرحباً بك: {t_name}")
        col
