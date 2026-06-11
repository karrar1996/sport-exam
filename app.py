import streamlit as st
import docx
import re
import pandas as pd

st.set_page_config(page_title="نظام إدارة امتحانات قسم الرياضة", layout="wide")

# تصميم احترافي متكامل يدعم واجهة اليمين إلى اليسار والطباعة والشعار
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

# 🔗 رابط السحب والربط المباشر بملفك الحقيقي
SHEET_ID = "1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA"
TEACHERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=teachers"
EXAMS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=exams"

# جلب بيانات الأساتذة
try:
    df_t = pd.read_csv(TEACHERS_URL)
    teachers_list = df_t.to_dict(orient="records")
except:
    teachers_list = [{"name": "م.د امير فاهم محسن", "code": "1234", "phone": "9647700000000"}]

# جلب بيانات الأسئلة
try:
    df_e = pd.read_csv(EXAMS_URL)
    exams_list = df_e.to_dict(orient="records")
except:
    exams_list = []

# دالة تنسيق وترتيب الأسئلة والخيارات
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
        
        if st.button("إرسال الأسئلة لرئاسة القسم"):
            if uploaded_file and stage and subject:
                content = process_exam_text(uploaded_file)
                st.success("✅ تمت معالجة وترتيب الأسئلة تلقائياً بنجاح! انسخ النص أدناه وضعه في ملف الـ Google Sheet المخصص للأسئلة:")
                st.text_area("نص الأسئلة المرتب والمنسق (جاهز للنسخ المباشر):", content, height=300)
            else:
                st.error("يرجى ملء جميع الحقول أولاً.")

# ----------------------------------------------------
# 2. لوحة المسؤول المحمية والطباعة (رمز الأدمن: 119)
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
            
            # رابط ماكرو الإرسال المباشر لملفك
            st.markdown(f'[👉 اضغط هنا لفتح نموذج الحفظ المباشر في السحابة](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing)', unsafe_allow_html=True)
            st.info("💡 يمكنك كتابة الاسم والرمز السري في ملف الجوجل شيت مباشرة عبر الرابط أعلاه، وسيظهر فوراً في لوحة التحكم هنا!")
                
        with tab2:
            st.subheader("قائمة التدريسيين المسجلين حالياً:")
            st.dataframe(pd.DataFrame(teachers_list))
                
        with tab3:
            if not exams_list:
                st.info("لا توجد ملفات أسئلة مسجلة حالياً في ورقة الـ exams داخل الشيت.")
            else:
                for idx, exam in enumerate(exams_list):
                    with st.expander(f"📋 أسئلة مادة ({exam.get('subject', 'غير مححدد')}) - التدريسي: {exam.get('teacher', 'غير محدد')}"):
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
{exam.get('content', 'لا يوجد محتوى')}
                            </div>
                            <br>
                            <p style="text-align:left; font-weight:bold; color:black; padding-left:20px;">مدرس المادة: {exam.get('teacher', '-')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('<button onclick="window.print()" style="width:100%; font-weight:bold; background-color:#ff9a00; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">🖨️ طباعة ورقة الأسئلة هذه فوراً</button>', unsafe_allow_html=True)
    
    elif admin_password != "":
        st.error("الرمز السري غير صحيح!")
