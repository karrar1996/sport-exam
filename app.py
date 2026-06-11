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
    GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1es1v2CvHlmt8uHYnw9mzqBKF8k8VijGE2s5jMdT-PlA/edit?usp=sharing"
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; direction: rtl; }
        [data-testid="stSidebar"] { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# ⚠️ ضع رابط ملف الجوجل شيت الخاص بك هنا بين علامتي الاقتباس
# ----------------------------------------------------
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wM87G7K3A6zO9Z8P7F3I_gIuxq36Y2vG0wV1Zp6D4YI/edit?usp=sharing"

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
                new_exam = {
                    "teacher": t_name, "exam_type": exam_type, "stage": stage,
                    "subject": subject, "day": day, "date": date, "time": exam_time,
                    "head": head_sig, "content": content, "status": "قيد التدقيق ⏳"
                }
                exams_list.append(new_exam)
                try:
                    conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="exams", data=pd.DataFrame(exams_list))
                    st.success("✅ تم إرسال الأسئلة بنجاح إلى رئيس القسم وحفظها سحابياً.")
                except:
                    st.warning("تم الحفظ محلياً، يرجى التأكد من صلاحيات كتابة الجوجل شيت.")
            else:
                st.error("يرجى ملء جميع الحقول ورفع الملف أولاً.")

# ----------------------------------------------------
# 2. لوحة المسؤول المحمية والطباعة (رمز الأدمن: 119)
# ----------------------------------------------------
else:
    st.title("👑 بوابة المسؤول الوحيد للنظام")
    admin_password = st.text_input("أدخل رمز الأدمن السري للوصول للوحة التحكم:", type="password")
    
    if admin_password == "119":
        st.success("تم التحقق بنجاح! مرحباً بك أستاذنا المسؤول.")
        tab1, tab2 = st.tabs(["🔑 توليد الرموز للتدريسيين", "🧐 تدقيق وطباعة الأسئلة"])
        
        with tab1:
            st.subheader("إضافة تدريسي جديد وتوليد رمز دخول له")
            new_name = st.text_input("اسم التدريسي الجديد:")
            new_code = st.text_input("الرمز السري المخصص له:")
            new_phone = st.text_input("رقم هاتف الواتساب (مثال: 9647700000000):")
            if st.button("حفظ وتوليد الحساب"):
                if new_name and new_code and new_phone:
                    teachers_list.append({"name": new_name, "code": new_code, "phone": new_phone})
                    try:
                        conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="teachers", data=pd.DataFrame(teachers_list))
                        st.success(f"تم حفظ التدريسي {new_name} بنجاح في السحابة.")
                    except:
                        st.error("خطأ في الاتصال بالسحابة.")
                else:
                    st.error("يرجى ملء كافة الحقول أولاً.")
                
        with tab2:
            if not exams_list:
                st.info("لا توجد ملفات أسئلة مرسلة حالياً من التدريسيين.")
            for idx, exam in enumerate(exams_list):
                t_phone = next((t['phone'] for t in teachers_list if str(t['name']).strip() == str(exam['teacher']).strip()), "")
                
                with st.expander(f"📋 أسئلة مادة ({exam['subject']}) - التدريسي: {exam['teacher']} | {exam['status']}"):
                    
                    # نموذج المعاينة والطباعة الرسمي مع الشعار بدقة عالية
                    exam_container = st.container()
                    with exam_container:
                        st.markdown(f"""
                        <div class="print-area">
                            <div class="main-header">
                                <img class="logo-img" src="https://i.imgur.com/v8bS6mR.png" alt="شعار الجامعة الإسلامية"><br>
                                <h3 style="margin:5px; color:black;">الجامعة الإسلامية - كلية التربية</h3>
                                <h4 style="margin:5px; color:black;">قسم التربية البدنية وعلوم الرياضة</h4>
                                <h5 style="margin:5px; color:black;">أسئلة امتحان {exam['exam_type']} العام الدراسي 2025 – 2026 م</h5>
                                <hr style="border:1px solid black; margin:10px 0;">
                                <table style="width:100%; text-align:right; border-collapse:collapse; color:black; font-weight:bold;">
                                    <tr>
                                        <td>المرحلة: {exam['stage']}</td>
                                        <td>المادة: {exam['subject']}</td>
                                        <td>الوقت: {exam['time']}</td>
                                    </tr>
                                    <tr>
                                        <td>اليوم: {exam['day']}</td>
                                        <td>التاريخ: {exam['date']}</td>
                                        <td>رئيس القسم: {exam['head']}</td>
                                    </tr>
                                </table>
                            </div>
                            <div style="white-space: pre-wrap; font-size:18px; padding:15px; border:1px solid #ccc; border-radius:5px; background:#fff; color:black; line-height:1.8; text-align:right;">
{exam['content']}
                            </div>
                            <br>
                            <p style="text-align:left; font-weight:bold; color:black; padding-left:20px;">مدرس المادة: {exam['teacher']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # أزرار التحكم والطباعة الخاصة بك كمسؤول
                    edited_text = st.text_area("تعديل نص الأسئلة إن وجد خطأ:", exam['content'], height=150, key=f"ed_{idx}")
                    if edited_text != exam['content']:
                        exams_list[idx]['content'] = edited_text
                        conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="exams", data=pd.DataFrame(exams_list))
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("✅ موافقة واعتماد للطباعة", key=f"ap_{idx}"):
                            exams_list[idx]['status'] = "تمت الموافقة ✅"
                            conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="exams", data=pd.DataFrame(exams_list))
                            st.success("تم اعتماد الأسئلة.")
                    with c2:
                        # زر الطباعة السحري
                        st.markdown('<button onclick="window.print()" style="width:100%; font-weight:bold; background-color:#ff9a00; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">🖨️ طباعة الأسئلة فوراً</button>', unsafe_allow_html=True)
                    with c3:
                        if t_phone:
                            st.markdown(f'<a href="https://wa.me/{t_phone}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer; width:100%;">💬 مراسلة التدريسي</button></a>', unsafe_allow_html=True)
    
    elif admin_password != "":
        st.error("الرمز السري غير صحيح! لا تملك صلاحية الوصول بصفتك مسؤول.")
