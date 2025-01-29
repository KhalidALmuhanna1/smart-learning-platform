 import streamlit as st
import sqlite3
import openai  # استيراد مكتبة openai
from PIL import Image
import pytesseract
import pdfplumber
from datetime import datetime, timedelta
import io
import base64
from streamlit.components.v1 import html

st.set_page_config(
    page_title="Smart Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


OPENAI_API_KEY = "secret"
openai.api_key = OPENAI_API_KEY

def get_gpt4_response(prompt: str) -> str:
    """
    Generates a response using OpenAI GPT-4 model.
    يعتمد على محتوى prompt المرسل.
    """
    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                # رسالة "system" تضبط أسلوب المساعد
                {"role": "system", "content": "You are a helpful assistant with broad general knowledge."},
                # رسالة المستخدم
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # تحكم في عشوائية الردود
            max_tokens=2000   # تحكم في طول الاستجابة
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


FIXED_EXAM_TIME = "09:00:00"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

lang = {
    "en": {
        "title": "Smart Learning Platform",
        "home": "🏠 Home",
        "courses": "📚 Courses",
        "schedule": "📅 Schedule",
        "assistant": "💬 Assistant",
        "exams": "📝 Exams",
        "gpa_calculator": "📊 GPA Calculator",
        "welcome": "Welcome to Smart Learning Platform",
        "no_courses": "No courses available",
        "course_name": "Course Name",
        "course_code": "Course Code",
        "add_course": "➕ Add New Course",
        "required_fields": "Please fill all required fields",
        "course_exists": "Course code already exists",
        "exam_date": "Exam Date",
        "special_instructions": "Special Instructions",
        "save_schedule": "💾 Save Schedule",
        "upload_material": "📤 Upload New Material",
        "choose_file": "Choose file (PDF or image)",
        "upload_success": "File uploaded successfully!",
        "generate_questions": "🎯 Generate Exam Questions",
        "view": "View",
        "download": "Download",
        "delete": "Delete",
        "exam_content": "Exam Content",
        "your_gpa": "Your GPA",
        "select_grade": "Select Grade",
        "credits": "Credit Hours",
        "no_materials": "No materials uploaded for this course",
        "all_files": "All files",
        "specific_file": "Specific file",
        "analysis": "Analyzing materials...",
        "generation_error": "Error generating questions",
        "file_too_big": "File size exceeds 50MB limit",
        "processing_error": "File processing error",
        "delete_confirm": "Are you sure you want to delete this?",
        "days_remaining": "Days Remaining",
        "no_exam": "No exam scheduled",
        "ask_question": "Ask your question...",
        "searching": "Searching for answer...",
        "assistant_error": "Error generating response",
        "confirm_delete": "Confirm Delete",
        "cancel_delete": "Cancel",
        "delete_confirm_course": "Delete this course and all associated data?",
        "delete_confirm_material": "Permanently delete this material?",
        "delete_confirm_exam": "Delete this exam?",
        "youtube_playlist": "YouTube Playlist Link",
        "add_playlist": "Add YouTube Playlist",
        "enter_playlist": "Enter YouTube Playlist URL"
    },
    "ar": {
        "title": "منصة التعلم الذكي",
        "home": "🏠 الرئيسية",
        "courses": "📚 المواد",
        "schedule": "📅 الجدول",
        "assistant": "💬 المساعد",
        "exams": "📝 الامتحانات",
        "gpa_calculator": "📊 حاسبة المعدل",
        "welcome": "مرحبا بكم في منصة التعلم الذكي",
        "no_courses": "لا توجد مواد متاحة",
        "course_name": "اسم المادة",
        "course_code": "كود المادة",
        "add_course": "➕ إضافة مادة جديدة",
        "required_fields": "يرجى ملء جميع الحقول المطلوبة",
        "course_exists": "كود المادة موجود مسبقا",
        "exam_date": "تاريخ الامتحان",
        "special_instructions": "تعليمات خاصة",
        "save_schedule": "💾 حفظ الجدول",
        "upload_material": "📤 رفع مادة جديدة",
        "choose_file": "اختر ملف (PDF أو صورة)",
        "upload_success": "تم رفع الملف بنجاح!",
        "generate_questions": "🎯 توليد أسئلة امتحان",
        "view": "عرض",
        "download": "تنزيل",
        "delete": "حذف",
        "exam_content": "محتوى الامتحان",
        "your_gpa": "معدلك التراكمي",
        "select_grade": "اختر الدرجة",
        "credits": "الساعات المعتمدة",
        "no_materials": "لا توجد مواد مرفوعة لهذه المادة",
        "all_files": "جميع الملفات",
        "specific_file": "ملف محدد",
        "analysis": "جار تحليل المواد...",
        "generation_error": "خطأ في توليد الأسئلة",
        "file_too_big": "حجم الملف يتجاوز 50 ميجابايت",
        "processing_error": "خطأ في معالجة الملف",
        "delete_confirm": "هل أنت متأكد من الحذف؟",
        "days_remaining": "الأيام المتبقية",
        "no_exam": "لا يوجد امتحان مجدول",
        "ask_question": "اطرح سؤالك...",
        "searching": "جار البحث عن إجابة...",
        "assistant_error": "خطأ في توليد الرد",
        "confirm_delete": "تأكيد الحذف",
        "cancel_delete": "إلغاء",
        "delete_confirm_course": "حذف هذه المادة وجميع بياناتها؟",
        "delete_confirm_material": "حذف هذه المادة بشكل دائم؟",
        "delete_confirm_exam": "حذف هذا الامتحان؟",
        "youtube_playlist": "رابط قائمة تشغيل يوتيوب",
        "add_playlist": "إضافة قائمة تشغيل يوتيوب",
        "enter_playlist": "أدخل رابط قائمة التشغيل"
    }
}

def apply_dark_theme():
    st.markdown(f"""
    <style>
    :root {{
        --primary: #2ecc71;
        --background: #121212;
        --secondary: #1e1e1e;
        --text: #ffffff;
        --accent: #3498db;
        --warning: #e74c3c;
    }}

    .stApp {{
        background: var(--background);
        color: var(--text);
        font-family: {'"Segoe UI", sans-serif' if st.session_state.get("lang", "en") == "en" else '"Noto Sans Arabic", sans-serif'};
        text-align: {'left' if st.session_state.get("lang", "en") == "en" else 'right'};
    }}

    .stSidebar {{
        background: var(--secondary) !important;
        border-right: 1px solid #333 !important;
    }}

    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background: var(--secondary) !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }}

    .stButton button {{
        background: var(--primary) !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }}

    .exam-card {{
        background: var(--secondary) !important;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--accent);
    }}

    .course-card {{
        background: var(--secondary) !important;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem;
        transition: transform 0.2s;
    }}

    .course-card:hover {{
        transform: translateY(-3px);
    }}

    .file-item {{
        background: #2a2a2a;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}

    .delete-popup {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--secondary);
        padding: 2rem;
        border-radius: 12px;
        z-index: 1000;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}

    [dir="rtl"] {{
        direction: rtl;
        text-align: right;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_db():
    return sqlite3.connect('university.db', check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        # جدول المواد (courses)
        c.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                credits INTEGER NOT NULL,
                youtube_playlist TEXT
            )
        ''')
        c.execute("PRAGMA table_info(courses)")
        columns = [col[1] for col in c.fetchall()]
        if 'instructor' in columns:
            c.execute('ALTER TABLE courses RENAME TO old_courses')
            c.execute('''
                CREATE TABLE courses (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    credits INTEGER NOT NULL,
                    youtube_playlist TEXT
                )
            ''')
            c.execute('''
                INSERT INTO courses (id, name, code, credits)
                SELECT id, name, code, credits FROM old_courses
            ''')
            c.execute('DROP TABLE old_courses')

        # جدول الامتحانات
        c.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')

        # جدول المواد المرفوعة (PDF/صور...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS course_materials (
                id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_content BLOB,
                extracted_text TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')

        # جدول الامتحانات المُولَّدة
        c.execute('''
            CREATE TABLE IF NOT EXISTS generated_exams (
                id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL,
                exam_content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')

        # إذا لم يكن الحقل موجودًا
        c.execute("PRAGMA table_info(courses)")
        columns = [col[1] for col in c.fetchall()]
        if 'youtube_playlist' not in columns:
            c.execute('ALTER TABLE courses ADD COLUMN youtube_playlist TEXT')

        conn.commit()

def localize(key):
    return lang[st.session_state.get("lang", "en")][key]

def confirmation_dialog():
    if 'pending_delete' in st.session_state:
        delete_type = st.session_state.pending_delete['type']
        item_id = st.session_state.pending_delete['id']
        st.warning(localize("delete_confirm"))
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button(localize("confirm_delete")):
                try:
                    if delete_type == 'course':
                        if delete_course(item_id):
                            st.session_state.selected_course = None
                            st.rerun()
                    elif delete_type == 'material':
                        if delete_file(item_id):
                            st.rerun()
                    elif delete_type == 'exam':
                        with get_db() as conn:
                            conn.execute("DELETE FROM generated_exams WHERE id = ?", (item_id,))
                            conn.commit()
                            st.rerun()
                finally:
                    del st.session_state.pending_delete
        with col2:
            if st.button(localize("cancel_delete")):
                del st.session_state.pending_delete
                st.rerun()

def delete_file(file_id):
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM course_materials WHERE id = ?", (file_id,))
            conn.commit()
            return True
    except Exception as e:
        st.error(f"{localize('processing_error')}: {str(e)}")
        return False

def delete_course(course_id):
    with get_db() as conn:
        try:
            conn.execute("DELETE FROM exams WHERE course_id = ?", (course_id,))
            conn.execute("DELETE FROM course_materials WHERE course_id = ?", (course_id,))
            conn.execute("DELETE FROM generated_exams WHERE course_id = ?", (course_id,))
            conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"{localize('processing_error')}: {str(e)}")
        return False

def parse_exam_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(hour=9, minute=0, second=0)

def days_until_exam(exam_date_str):
    exam_date = parse_exam_date(exam_date_str)
    now = datetime.now()
    if exam_date < now:
        return 0
    delta = exam_date - now
    return delta.days + 1 if delta.seconds > 0 else delta.days

def extract_text(file):
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                return text.strip()
        else:
            img = Image.open(file)
            img = img.convert('L')
            img = img.point(lambda x: 0 if x < 140 else 255)
            img = img.resize((img.width * 2, img.height * 2))
            custom_config = r'--oem 3 --psm 6 -l eng+ara'
            return pytesseract.image_to_string(img, config=custom_config).strip()
    except Exception as e:
        st.error(f"{localize('processing_error')}: {str(e)}")
        return ""

def save_uploaded_file(course_id, file):
    try:
        file_size = len(file.getvalue())
        if file_size > MAX_FILE_SIZE:
            st.error(localize("file_too_big"))
            return False
        extracted_text = extract_text(file) or ""
        with get_db() as conn:
            conn.execute(
                """INSERT INTO course_materials 
                (course_id, file_name, file_content, extracted_text) 
                VALUES (?, ?, ?, ?)""",
                (course_id, file.name, file.getvalue(), extracted_text)
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"{localize('processing_error')}: {str(e)}")
        return False

def show_pdf_new_window(file_bytes, file_name):
    try:
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
        pdf_html = f"""
        <script>
            function openPDF() {{
                var win = window.open();
                win.document.write(`
                    <html>
                        <head>
                            <title>{file_name}</title>
                            <style>
                                body {{ margin: 0; }}
                                iframe {{ width: 100%; height: 100vh; border: none; }}
                            </style>
                        </head>
                        <body>
                            <iframe 
                                src="data:application/pdf;base64,{base64_pdf}"
                                frameborder="0"
                            ></iframe>
                        </body>
                    </html>
                `);
            }}
            openPDF();
        </script>
        """
        st.components.v1.html(pdf_html, height=0)
    except Exception as e:
        st.error(f"{localize('processing_error')}: {str(e)}")

def handle_course_materials(conn, course_id):
    st.subheader(localize("upload_material"))
    with st.expander(localize("upload_material"), expanded=True):
        uploaded_file = st.file_uploader(
            localize("choose_file"),
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help=f"Max size: {MAX_FILE_SIZE // 1024 // 1024}MB",
            key="material_uploader"
        )
        if uploaded_file and st.button(localize("upload_success"), key="upload_btn"):
            if save_uploaded_file(course_id, uploaded_file):
                st.rerun()

    with st.expander(localize("add_playlist"), expanded=True):
        youtube_link = st.text_input(localize("youtube_playlist"), key="youtube_playlist")
        if youtube_link and st.button(localize("add_playlist"), key="add_playlist_btn"):
            with get_db() as conn:
                conn.execute(
                    "UPDATE courses SET youtube_playlist = ? WHERE id = ?",
                    (youtube_link, course_id)
                )
                conn.commit()
                st.success("✅ " + localize("upload_success"))

    st.subheader(localize("upload_material"))
    uploaded_files = conn.execute('''
        SELECT id, file_name, uploaded_at FROM course_materials 
        WHERE course_id = ?
    ''', (course_id,)).fetchall()

    if not uploaded_files:
        st.info(localize("no_materials"))
        return

    for file_ in uploaded_files:
        file_id, file_name, uploaded_at = file_
        with st.container():
            cols = st.columns([4, 1, 1, 1])
            with cols[0]:
                st.markdown(f"""
                <div class='file-item'>
                    <p>📄 {file_name}</p>
                    <small>{localize('upload_material')}: {uploaded_at}</small>
                </div>
                """, unsafe_allow_html=True)

            with cols[1]:
                file_data = conn.execute('''
                    SELECT file_content FROM course_materials 
                    WHERE id = ?
                ''', (file_id,)).fetchone()
                if st.button(localize("view"), key=f"view_{file_id}"):
                    if file_name.lower().endswith('.pdf'):
                        show_pdf_new_window(file_data[0], file_name)
                    elif file_name.lower().split('.')[-1] in ['png', 'jpg', 'jpeg']:
                        img = Image.open(io.BytesIO(file_data[0]))
                        st.image(img, caption=file_name)
                    else:
                        st.warning("Unsupported format")

            with cols[2]:
                st.download_button(
                    label=localize("download"),
                    data=io.BytesIO(file_data[0]),
                    file_name=file_name,
                    key=f"dl_{file_id}",
                    use_container_width=True
                )
            with cols[3]:
                if st.button("🗑️", key=f"file_del_{file_id}"):
                    st.session_state.pending_delete = {
                        'type': 'material',
                        'id': file_id
                    }

def main():
    init_db()
    apply_dark_theme()

    if 'selected_course' not in st.session_state:
        st.session_state.selected_course = None
    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = ""
    if 'last_uploaded' not in st.session_state:
        st.session_state.last_uploaded = None

    with st.sidebar:
        st.session_state.lang = st.selectbox("🌍 Language", ["en", "ar"], index=0)
        st.header(localize("home"))
        menu = st.radio("", [
            localize("home"),
            localize("courses"),
            localize("schedule"),
            localize("assistant"),
            localize("exams"),
            localize("gpa_calculator")
        ], label_visibility="collapsed")

    confirmation_dialog()
    conn = get_db()

    # ========== الصفحة الرئيسية ==========
    if menu == localize("home"):
        st.title(localize("welcome"))

        courses = conn.execute("SELECT id, name, code FROM courses").fetchall()
        if not courses:
            st.info(localize("no_courses"))
            return

        st.subheader(localize("courses"))
        cols = st.columns(3)
        for idx, course in enumerate(courses):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class='course-card'>
                        <h3>{course[1]}</h3>
                        <small>{course[2]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(localize("view") + f" {course[0]}", key=f"details_{course[0]}"):
                            st.session_state.selected_course = course[0]
                    with col2:
                        if st.button("🗑️", key=f"del_{course[0]}"):
                            st.session_state.pending_delete = {
                                'type': 'course',
                                'id': course[0]
                            }

        if st.session_state.selected_course:
            st.divider()
            course_info = conn.execute("SELECT name, code, credits, youtube_playlist FROM courses WHERE id = ?",
                                       (st.session_state.selected_course,)).fetchone()
            exam_info = conn.execute('''
                SELECT date, notes FROM exams 
                WHERE course_id = ?
            ''', (st.session_state.selected_course,)).fetchone()

            tab1, tab2 = st.tabs([localize("course_name"), localize("upload_material")])
            with tab1:
                st.subheader(f"{localize('course_name')} - {course_info[0]}")
                st.markdown(f"""
                <div class='exam-content'>
                    <p>{localize('course_code')}: {course_info[1]}</p>
                    <p>{localize('credits')}: {course_info[2]}</p>
                    <p>{localize('youtube_playlist')}: <a href="{course_info[3]}" target="_blank">{course_info[3]}</a></p>
                </div>
                """, unsafe_allow_html=True)

                if exam_info:
                    exam_date_str = exam_info[0]
                    days_left = days_until_exam(exam_date_str)
                    exam_date = parse_exam_date(exam_date_str)
                    st.markdown(f"""
                    <div class='exam-content'>
                        <h4>{localize('exam_content')}</h4>
                        <p>{localize('exam_date')}: {exam_date.strftime('%Y-%m-%d %I:%M %p')}</p>
                        <p>{localize('days_remaining')}: {days_left}</p>
                        <p>{localize('special_instructions')}: {exam_info[1] or localize('no_exam')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(localize("no_exam"))

            with tab2:
                handle_course_materials(conn, st.session_state.selected_course)

    elif menu == localize("courses"):
        st.title(localize("courses"))
        with st.form("course_form", clear_on_submit=True):
            cols = st.columns(3)
            with cols[0]:
                name = st.text_input(localize("course_name") + "*")
            with cols[1]:
                code = st.text_input(localize("course_code") + "*")
            with cols[2]:
                credits = st.number_input(localize("credits") + "*", min_value=1, max_value=5, value=3)

            if st.form_submit_button(localize("add_course"), use_container_width=True):
                if all([name.strip(), code.strip()]):
                    try:
                        conn.execute(
                            "INSERT INTO courses (name, code, credits) VALUES (?, ?, ?)",
                            (name.strip(), code.upper().strip(), credits)
                        )
                        conn.commit()
                        st.success("✅ " + localize("upload_success"))
                    except sqlite3.IntegrityError:
                        st.error("⚠️ " + localize("course_exists"))
                else:
                    st.warning(localize("required_fields"))

        st.subheader(localize("courses"))
        courses = conn.execute("SELECT id, name, code FROM courses").fetchall()
        cols = st.columns(3)
        for idx, course in enumerate(courses):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class='course-card'>
                        <h3>{course[1]}</h3>
                        <small>{course[2]}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(localize("view"), key=f"btn_{course[0]}"):
                            st.session_state.selected_course = course[0]
                    with col2:
                        if st.button("🗑️", key=f"del_{course[0]}"):
                            st.session_state.pending_delete = {
                                'type': 'course',
                                'id': course[0]
                            }

    elif menu == localize("schedule"):
        st.title(localize("schedule"))
        course_options = conn.execute("SELECT id, name, code FROM courses").fetchall()
        if not course_options:
            st.warning(localize("no_courses"))
            return

        with st.form("exam_form"):
            cols = st.columns([2, 1])
            with cols[0]:
                selected_course = st.selectbox(
                    localize("courses"),
                    course_options,
                    format_func=lambda x: f"{x[1]} ({x[2]})"
                )
            with cols[1]:
                exam_date = st.date_input(localize("exam_date"), min_value=datetime.today().date())

            exam_notes = st.text_area(localize("special_instructions"), height=100)
            if st.form_submit_button(localize("save_schedule"), use_container_width=True):
                full_datetime = f"{exam_date.strftime('%Y-%m-%d')} {FIXED_EXAM_TIME}"
                try:
                    conn.execute(
                        "INSERT INTO exams (course_id, date, notes) VALUES (?, ?, ?)",
                        (selected_course[0], full_datetime, exam_notes)
                    )
                    conn.commit()
                    st.success("✅ " + localize("upload_success"))
                except Exception as e:
                    st.error(f"{localize('processing_error')}: {str(e)}")

    elif menu == localize("assistant"):
        st.title(localize("assistant"))

        # 1) نجلب نصوص الـ PDF من قاعدة البيانات (اختياري إذا أردت دمجها)
        with get_db() as conn_:
            materials = conn_.execute("SELECT extracted_text FROM course_materials").fetchall()

        # 2) نجمعها (لا يزيد عن 8000 حرف)
        pdf_context = "\n".join([m[0] for m in materials if m[0]])[:8000]

        # 3) سجل المحادثات
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 4) عرض الرسائل السابقة
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


        if prompt := st.chat_input(localize("ask_question")):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)



            full_prompt = prompt  # أبسط شيء: إرسال مدخل المستخدم فقط

            with st.spinner(localize("searching")):
                try:
                    response_text = get_gpt4_response(full_prompt)
                except Exception as e:
                    response_text = f"{localize('assistant_error')}: {str(e)}"

            with st.chat_message("assistant"):
                placeholder = st.empty()
                generated_text = ""
                import time
                for word in response_text.split():
                    generated_text += word + " "
                    placeholder.markdown(generated_text)
                    time.sleep(0.02)

            st.session_state.messages.append({"role": "assistant", "content": generated_text})

    elif menu == localize("exams"):
        st.title(localize("exams"))
        st.subheader("Generate New Exam")
        courses_data = conn.execute("SELECT id, name, code FROM courses").fetchall()
        if not courses_data:
            st.warning(localize("no_courses"))
        else:
            selected_course = st.selectbox(
                "Select a course to generate the exam for:",
                courses_data,
                format_func=lambda c: f"{c[1]} ({c[2]})"
            )
            question_type = st.radio(
                "Select Question Type",
                ["Multiple Choice", "True/False", "Short Answer", "Coding Challenge"]
            )
            num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
            exam_topic = st.text_area(
                "Enter exam topic or key points:",
                help="Specify what the exam questions should focus on"
            )
            if st.button("Generate Exam"):
                materials_ = conn.execute("""
                    SELECT extracted_text
                    FROM course_materials
                    WHERE course_id = ?
                """, (selected_course[0],)).fetchall()
                context_ = "\n".join([m[0] for m in materials_ if m[0]])[:15000]
                if not context_.strip():
                    st.warning("No files found for this course. Please upload some materials first.")
                else:
                    # بناء برمبت عادي وإرسال لـ GPT-4
                    prompt_for_exam = f"""
                    You are an AI tutor helping instructors create exam questions.
                    Use the provided course materials to generate a well-structured exam.

                    ### Course Content:
                    {context_}

                    ### Exam Details:
                    - Topic: {exam_topic}
                    - Number of Questions: {num_questions}
                    - Question Type: {question_type}

                    ### Instructions:
                    - If Multiple Choice: 4 options (A, B, C, D)
                    - If True/False: Clarify correct
                    - If Short Answer: Provide expected answer
                    - If Coding: Provide example code

                    ### Generated Exam:
                    """
                    with st.spinner("Generating exam..."):
                        try:
                            exam_response = get_gpt4_response(prompt_for_exam)
                            generated_exam_content = exam_response.strip()
                            conn.execute("""
                                INSERT INTO generated_exams (course_id, exam_content)
                                VALUES (?, ?)
                            """, (selected_course[0], generated_exam_content))
                            conn.commit()
                            st.success("Exam generated and saved successfully!")
                        except Exception as e:
                            st.error(f"Error generating exam: {str(e)}")

        st.divider()
        st.subheader("Existing Exams")
        exams_ = conn.execute('''
            SELECT generated_exams.id, courses.name, generated_exams.exam_content, generated_exams.created_at 
            FROM generated_exams
            JOIN courses ON generated_exams.course_id = courses.id
            ORDER BY generated_exams.created_at DESC
        ''').fetchall()
        if not exams_:
            st.warning(localize("no_exam"))
        else:
            for exam_ in exams_:
                exam_id, course_name, content, created_at = exam_
                with st.container():
                    st.markdown(f"""
                    <div class='exam-card'>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h3>{course_name}</h3>
                            <small>{created_at}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    cols_ = st.columns([2, 1, 1])
                    with cols_[0]:
                        if st.button(f"View Exam #{exam_id}", key=f"view_{exam_id}"):
                            with st.expander(f"Exam Content - {course_name}", expanded=True):
                                st.markdown(content)
                    with cols_[1]:
                        st.download_button(
                            label=localize("download"),
                            data=content,
                            file_name=f"{course_name}_exam.txt",
                            mime="text/plain",
                            key=f"dl_{exam_id}"
                        )
                    with cols_[2]:
                        if st.button(localize("delete"), key=f"del_{exam_id}"):
                            st.session_state.pending_delete = {
                                'type': 'exam',
                                'id': exam_id
                            }

    elif menu == localize("gpa_calculator"):
        st.title(localize("gpa_calculator"))
        with get_db() as conn_:
            courses_ = conn_.execute("SELECT id, name, code, credits FROM courses").fetchall()
            if not courses_:
                st.info(localize("no_courses"))
                return
            grade_points = {
                'A+': 5.0, 'A': 4.75, 'B+': 4.5, 'B': 4.0,
                'C+': 3.5, 'C': 3.0, 'D+': 2.5, 'D': 2.0, 'F': 0.0
            }
            total_points = 0
            total_credits = 0
            for course_ in courses_:
                cols_ = st.columns([4, 2, 3])
                with cols_[0]:
                    st.markdown(f"*{course_[1]}* ({course_[2]})")
                with cols_[1]:
                    st.markdown(f"{localize('credits')}: {course_[3]}")
                with cols_[2]:
                    grade = st.selectbox(
                        localize("select_grade"),
                        options=list(grade_points.keys()),
                        key=f"grade_{course_[0]}"
                    )
                total_points += grade_points[grade] * course_[3]
                total_credits += course_[3]
            if total_credits > 0:
                gpa = total_points / total_credits
                st.markdown(f"### {localize('your_gpa')}: *{gpa:.2f}*")
                if gpa >= 3.0:
                    st.balloons()
            else:
                st.warning(localize("required_fields"))

    conn.close()

if __name__ == "__main__":
    main()
