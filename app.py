import streamlit as st
import docx
import re

st.set_page_config(page_title="نظام إدارة امتحانات قسم الرياضة", layout="wide")

# تصميم الواجهة ودعم اللغة العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, input, label, select, button, textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: RTL !important;
        text-align: right !important;
    }
    .stButton button { width: 100%; font-weight: bold; }
    .main-header {
        text-align: center !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #000000;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# الذاكرة المؤقتة للنظام
if 'teachers' not in st.session_state:
    st.session_state['teachers'] = [{"name": "م.د امير فاهم محسن", "code": "1234", "phone": "9647700000000"}]
if 'exams' not in st.session_state:
    st.session_state['exams'] = []

def process_exam_text(file_buffer):
    doc = docx.Document(file_buffer)
    full_text = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            text = re.sub(r'\b[aA][-)]\s*', 'أ- ', text)
            text = re.sub(r'\b[bB][-)]\s*', 'ب- ', text)
            text = re.sub(r'\b[cC][-)]\s*', 'ج- ', text)
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
    
    auth = any(t['name'] == t_name and t['code'] == t_code for t in st.session_state['teachers'])
    
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
        uploaded_file = st.file_uploader("ارفع ملف الأسئلة (.docx)", type=["docx"])
        
        if st.button("إرسال الأسئلة لرئاسة القسم"):
            if uploaded_file:
                content = process_exam_text(uploaded_file)
                st.session_state['exams'].append({
                    "teacher": t_name, "exam_type": exam_type, "stage": stage,
                    "subject": subject, "day": day, "date": date, "time": exam_time,
                    "head": head_sig, "content": content, "status": "قيد التدقيق ⏳"
                })
                st.info("تم إرسال الأسئلة بنجاح إلى رئيس القسم.")

# ----------------------------------------------------
# 2. لوحة المسؤول المحمية (الأدمن الوحيد)
# ----------------------------------------------------
else:
    st.title("👑 بوابة المسؤول الوحيد للنظام")
    
    # حقل التحقق من الرمز السري للأدمن لحماية البيانات
    admin_password = st.text_input("أدخل رمز الأدمن السري للوصول للوحة التحكم:", type="password")
    
    if admin_password == "119":
        st.success("تم التحقق بنجاح! مرحباً بك أستاذنا المسؤول.")
        
        tab1, tab2 = st.tabs(["🔑 توليد الرموز للتدريسيين", "🧐 تدقيق الأسئلة والموافقة"])
        
        with tab1:
            st.subheader("إضافة تدريسي جديد وتوليد رمز دخول له")
            new_name = st.text_input("اسم التدريسي الجديد:")
            new_code = st.text_input("الرمز السري المخصص له:")
            new_phone = st.text_input("رقم هاتف الواتساب (مثال: 9647700000000):")
            if st.button("حفظ وتوليد الحساب"):
                if new_name and new_code and new_phone:
                    st.session_state['teachers'].append({"name": new_name, "code": new_code, "phone": new_phone})
                    st.success(f"تم توليد حساب بنجاح للتدريسي {new_name}")
                else:
                    st.error("يرجى ملء كافة الحقول أولاً.")
                
        with tab2:
            if not st.session_state['exams']:
                st.info("لا توجد ملفات أسئلة معلقة حالياً.")
            for idx, exam in enumerate(st.session_state['exams']):
                t_phone = next((t['phone'] for t in st.session_state['teachers'] if t['name'] == exam['teacher']), "")
                with st.expander(f"📋 أسئلة مادة ({exam['subject']}) - التدريسي: {exam['teacher']} | {exam['status']}"):
                    st.markdown(f"""
                    <div class="main-header">
                        <h4>الجامعة الاسلامية - كلية التربية – قسم التربية البدنية وعلوم الرياضة</h4>
                        <h5>أسئلة امتحان {exam['exam_type']} العام الدراسي 2025 – 2026 م</h5>
                        <p>المرحلة: {exam['stage']} &nbsp;&nbsp;|&nbsp;&nbsp; المادة: {exam['subject']}</p>
                        <p>اليوم: {exam['day']} &nbsp;&nbsp;|&nbsp;&nbsp; التاريخ: {exam['date']} &nbsp;&nbsp;|&nbsp;&nbsp; الوقت: {exam['time']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    edited_text = st.text_area("تعديل نص الأسئلة والخيارات مباشرة:", exam['content'], height=200, key=f"ed_{idx}")
                    st.session_state['exams'][idx]['content'] = edited_text
                    
                    st.write(f"**مدرس المادة:** {exam['teacher']} | **رئيس القسم:** {exam['head']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ موافقة واعتماد للطباعة", key=f"ap_{idx}"):
                            st.session_state['exams'][idx]['status'] = "تمت الموافقة ✅"
                            st.success("تم اعتماد الأسئلة بنجاح.")
                    with c2:
                        if t_phone:
                            st.markdown(f'<a href="https://wa.me/{t_phone}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer; width:100%;">💬 مراسلة التدريسي عبر واتساب</button></a>', unsafe_allow_html=True)
    
    elif admin_password != "":
        st.error("الرمز السري غير صحيح! لا تملك صلاحية الوصول بصفتك مسؤول.")