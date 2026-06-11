import streamlit as st
import docx
import re
import pandas as pd
import requests

st.set_page_config(page_title="نظام إدارة امتحانات قسم الرياضة", layout="wide")

# تنسيق الواجهة بالكامل لتدعم اللغة العربية من اليمين إلى اليسار والطباعة
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
    .logo-img { max-width: 100px; margin-bottom: 10px; }
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; direction: rtl; }
        [data-testid="stSidebar"] { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# الـ ID الثابت لملف الشيت الخاص بك
SHEET_ID = "1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA"

TEACHERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=teachers"
EXAMS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=exams"

def get_table_data(url):
    try:
        # تلافي مشاكل التخزين المؤقت لقراءة الأسماء فوراً
        return pd.read_csv(url, index_col=False).to_dict(orient="records")
    except:
        return []

teachers_list = get_table_data(TEACHERS_URL)
exams_list = get_table_data(EXAMS_URL)

# دالة إرسال البيانات السحابية المطورة والمؤمنة ضد أخطاء الاتصال
def send_to_google_sheet(payload):
    try:
        # جلب الرابط من الـ Secrets
        script_url = st.secrets["SCRIPT_URL"]
        
        # محاولة الإرسال بالطريقة الأولى (POST JSON)
        headers = {"Content-Type": "application/json"}
        res = requests.post(script_url, json=payload, timeout=15)
        if "Success" in res.text or res.status_code == 200:
            return True
            
        # محاولة احتياطية ثانية في حال كان الـ Script يتوقع Params عادية
        res_backup = requests.post(script_url, params=payload, timeout=15)
        if "Success" in res_backup.text or res_backup.status_code == 200:
            return True
    except Exception as e:
        pass
    return False

# دالة معالجة نصوص الوورد
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
# 1. لوحة التدريسي
# ----------------------------------------------------
if role == "👨‍🏫 لوحة التدريسي":
    st.title("📝 رفع الأسئلة - قسم التربية البدنية")
    t_name = st.text_input("اسم التدريسي الثنائي أو الثلاثي:")
    t_code = st.text_input("الرمز السري:", type="password")
    
    auth = False
    if t_name and t_code:
        for t in teachers_list:
            db_name = str(t.get('name', '')).strip()
            db_code = str(t.get('code', '')).split('.')[0].strip()
            
            if db_name == t_name.strip() and db_code == t_code.strip():
                auth = True
                break
                
    if auth:
        st.success(f"مرحباً بك أستاذ: {t_name}")
        exam_type = st.text_input("نوع الامتحان:", value="النهائي")
        stage_field = st.text_input("المرحلة الدراسية:")
        subject_field = st.text_input("المادة العلمية:")
        day_field = st.text_input("اليوم:")
        date_field = st.text_input("التاريخ:")
        time_field = st.text_input("الوقت المحدد:")
        head_sig = st.text_input("رئيس القسم:")
        uploaded_file = st.file_uploader("ارفع ملف الأسئلة بمقاس الوورد (.docx)", type=["docx"])
        
        if st.button("🚀 إرسال وحفظ الأسئلة مباشرة في السحابة"):
            if uploaded_file and stage_field and subject_field:
                content = process_exam_text(uploaded_file)
                
                exam_payload = {
                    "sheet": "exams", "teacher": t_name, "exam_type": exam_type, "stage": stage_field,
                    "subject": subject_field, "day": day_field, "date": date_field, "time": time_field,
                    "head": head_sig, "content": content, "status": "قيد التدقيق ⏳"
                }
                
                if send_to_google_sheet(exam_payload):
                    st.success("✅ تم إرسال وحفظ الأسئلة تلقائياً داخل الـ Google Sheet بنجاح!")
                    st.balloons()
                else:
                    st.error("❌ حدث خطأ أثناء الاتصال بالسحابة، يرجى التحقق من إعداد الرابط البرمجي في Secrets.")
            else:
                st.error("يرجى ملء جميع الحقول ورفع ملف الأسئلة أولاً.")
    elif t_name != "" or t_code != "":
        st.error("❌ الاسم أو الرمز السري غير متطابق مع البيانات المسجلة في السحابة! يرجى التأكد من كتابته بدقة.")

# ----------------------------------------------------
# 2. لوحة المسؤول
# ----------------------------------------------------
else:
    st.title("👑 بوابة المسؤول الوحيد للنظام")
    admin_password = st.text_input("أدخل رمز الأدمن السري للوصول للوحة التحكم:", type="password")
    
    if admin_password == "119":
        st.success("تم التحقق بنجاح! مرحباً بك أستاذنا المسؤول.")
        tab1, tab2, tab3 = st.tabs(["🔑 توليد الرموز للتدريسيين", "📋 الحسابات الحالية", "🧐 تدقيق وطباعة الأسئلة"])
        
        with tab1:
            st.subheader("إضافة تدريسي جديد وتوليد رمز دخول له")
            new_name = st.text_input("اسم التدريسي الجديد:")
            new_code = st.text_input("الرمز السري المخصص له:")
            new_phone = st.text_input("رقم هاتف الواتساب (مثال: 9647700000000):")
            
            if st.button("💾 توليد الرمز وإرساله تلقائياً للشيت"):
                if new_name and new_code and new_phone:
                    teacher_payload = {
                        "sheet": "teachers", "name": new_name, "code": new_code, "phone": new_phone
                    }
                    if send_to_google_sheet(teacher_payload):
                        st.success(f"✅ تم توليد الحساب للتدريسي {new_name} وحُفظ تلقائياً في ملف الـ Google Sheet!")
                        st.balloons()
                    else:
                        st.error("❌ عذراً، لم يتم إرسال البيانات. تأكد من تفعيل الرابط البرمجي في الـ Secrets بشكل صحيح.")
                else:
                    st.error("يرجى ملء كافة الحقول أولاً.")
                
        with tab2:
            st.subheader("قائمة التدريسيين المسجلين حالياً في ملفك:")
            if teachers_list:
                st.dataframe(pd.DataFrame(teachers_list))
            else:
                st.info("لا توجد بيانات مسجلة حالياً.")
                
        with tab3:
            if not exams_list:
                st.info("لا توجد ملفات أسئلة مسجلة حالياً في ورقة الـ exams داخل الشيت.")
            else:
                for idx, exam in enumerate(exams_list):
                    with st.expander(f"📋 أسئلة مادة ({exam.get('subject', 'غير محدد')}) - التدريسي: {exam.get('teacher', 'غير محدد')}"):
                        content_text = exam.get('content', 'لا يوجد محتوى')
                        st.markdown(f"""
                        <div class="print-area">
                            <div class="main-header">
                                <img class="logo-img" src="https://i.imgur.com/v8bS6mR.png" alt="شعار الجامعة الإسلامية"><br>
                                <h3 style="margin:5px; color:black;">الجامعة الإسلامية - كلية التربية</h3>
                                <h4 style="margin:5px; color:black;">قسم التربية البدنية وعلوم الرياضة</h4>
                                <h5 style="margin:5px; color:black;">أسئلة امتحان {exam.get('exam_type', 'النهائي')}</h5>
                                <hr style="border:1px solid black; margin:10px 0;">
                                <table style="width:100%; text-align:right; border-collapse:collapse; color:black; font-weight:bold;">
                                    <tr>
                                        <td>المرحلة: {exam.get('stage', '-')}</td>
                                        <td>المادة: {exam.get('subject', '-')}</td>
                                        <td>الوقت: {exam.get('time', '-')}</td>
                                    </tr>
                                    <tr>
                                        <td>اليوم: {exam.get('day', '-')}</td>
                                        <td>التاريخ: {exam.get('date', '-')}</td>
                                        <td>رئيس القسم: {exam.get('head', '-')}</td>
                                    </tr>
                                </table>
                            </div>
                            <div style="white-space: pre-wrap; font-size:18px; padding:15px; border:1px solid #ccc; border-radius:5px; background:#fff; color:black; line-height:1.8; text-align:right;">
{content_text}
                            </div>
                            <br>
                            <p style="text-align:left; font-weight:bold; color:black; padding-left:20px;">مدرس المادة: {exam.get('teacher', '-')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown('<button onclick="window.print()" style="width:100%; font-weight:bold; background-color:#ff9a00; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">🖨️ طباعة ورقة الأسئلة هذه فوراً</button>', unsafe_allow_html=True)
    elif admin_password != "":
        st.error("الرمز السري غير صحيح!")
