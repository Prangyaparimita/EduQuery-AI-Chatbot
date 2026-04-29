from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import sqlite3
import numpy as np

# =========================
# 🔹 MEMORY
# =========================
current_course = None
awaiting_course_for = None   # "fees" when waiting for user to reply with course name

# =========================
# 🔹 TRAINING DATA
# =========================
training_sentences = [
    # fees
    "fees details", "what is fee", "tell me fees", "fee structure", "how much fees",
    "fee for mca", "mca fees", "btech fees", "mba fees", "bba fees",
    "cost of course", "tuition fee", "total fees", "course fee",
    # exam
    "exam schedule", "exam date", "when is exam", "test schedule", "exam timing",
    "when are exams", "exam timetable", "examination details", "upcoming exams",
    # placement
    "placement details", "job opportunities", "placement support", "companies visiting",
    "placement record", "campus placement", "hiring companies", "job after course",
    "placement percentage", "placement statistics",
    # admission
    "admission process", "how to apply", "apply now", "admission details",
    "registration process", "how do i get admission", "admission open",
    "eligibility for admission", "application form", "enroll now",
]

training_labels = [
    "fees","fees","fees","fees","fees",
    "fees","fees","fees","fees","fees",
    "fees","fees","fees","fees",
    "exam","exam","exam","exam","exam",
    "exam","exam","exam","exam",
    "placement","placement","placement","placement",
    "placement","placement","placement","placement",
    "placement","placement",
    "admission","admission","admission","admission",
    "admission","admission","admission",
    "admission","admission","admission",
]

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(training_sentences)
model = MultinomialNB(alpha=0.1)
model.fit(X, training_labels)

# =========================
# 🔹 DB RESPONSE
# =========================
def get_db_response(intent):
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response FROM responses WHERE LOWER(intent)=?",
            (intent.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception:
        return None

# =========================
# 🔹 COURSE DETECTION
# =========================
def detect_course(text):
    t = text.lower().strip()
    if "mca" in t:
        return "MCA"
    if "btech" in t or "b.tech" in t or "b tech" in t:
        return "B.Tech"
    if "mba" in t:
        return "MBA"
    if "bba" in t:
        return "BBA"
    return None

# =========================
# 🔹 KEYWORD INTENT
# =========================
def keyword_intent(text):
    t = text.lower()
    fee_keywords       = ["fee", "fees", "cost", "tuition", "charges", "price", "how much"]
    exam_keywords      = ["exam", "test", "schedule", "timetable", "date", "examination"]
    placement_keywords = ["placement", "job", "hiring", "recruit", "company", "companies", "campus", "career"]
    admission_keywords = ["admission", "apply", "register", "enroll", "application", "eligibility", "join"]
    mode_keywords      = ["mode", "type of course", "learning mode", "study mode"]
    course_keywords    = ["mca", "btech", "b.tech", "mba", "bba", "b tech"]
    greeting_keywords  = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    bye_keywords       = ["bye", "goodbye", "exit", "quit", "see you"]

    if any(k in t for k in bye_keywords):       return "bye"
    if any(k in t for k in greeting_keywords):  return "greeting"
    if any(k in t for k in course_keywords) and not any(k in t for k in fee_keywords + exam_keywords + placement_keywords + admission_keywords):
        return "course_select"
    if any(k in t for k in mode_keywords):      return "course_mode"
    if any(k in t for k in fee_keywords):       return "fees"
    if any(k in t for k in exam_keywords):      return "exam"
    if any(k in t for k in placement_keywords): return "placement"
    if any(k in t for k in admission_keywords): return "admission"
    return None

# =========================
# 🔹 INTENT DETECTION
# =========================
def detect_intent(text):
    intent = keyword_intent(text)
    if intent:
        return intent
    vec = vectorizer.transform([text])
    probs = model.predict_proba(vec)[0]
    max_prob = np.max(probs)
    if max_prob < 0.40:
        return "default"
    return model.classes_[np.argmax(probs)]

# =========================
# 🔹 CONSTANTS
# =========================
fee_map = {
    "MCA":    ("MCA",    "₹4,00,000"),
    "B.Tech": ("B.Tech", "₹6,00,000"),
    "MBA":    ("MBA",    "₹5,00,000"),
    "BBA":    ("BBA",    "₹3,00,000"),
}

# This tag tells index.html to append the Request Callback button
CALLBACK_TAG = "##CALLBACK##"

def fee_response(course):
    name, amount = fee_map[course]
    return (
        f"💰 <b>{name} Fee Structure</b><br><br>"
        f"Total Fee: <b>{amount}</b> (for full program)<br>"
        f"📌 EMI options available.<br><br>"
        f"For further clarification, our support team can contact you."
        + CALLBACK_TAG
    )

# =========================
# 🔹 MAIN RESPONSE FUNCTION
# =========================
def get_response(user_input):
    global current_course, awaiting_course_for

    if not user_input or not user_input.strip():
        return "Please type a message!"

    text = user_input.strip()

    # ── Waiting for course name after "Fees" was asked ──
    if awaiting_course_for == "fees":
        course = detect_course(text)
        if course:
            current_course = course
            awaiting_course_for = None
            return fee_response(course)
        # If user typed a different intent (exam, hi, bye, etc.) — escape the wait state
        other_intent = keyword_intent(text)
        if other_intent and other_intent not in ("fees", "course_select"):
            awaiting_course_for = None
            # fall through to normal intent handling below
        else:
            return (
                "Please type your course name:<br>"
                "🎓 <b>MCA</b> &nbsp;|&nbsp; <b>B.Tech</b> &nbsp;|&nbsp; <b>MBA</b> &nbsp;|&nbsp; <b>BBA</b>"
            )

    intent = detect_intent(text)

    # ── Greetings ──
    if intent == "greeting":
        current_course = None
        awaiting_course_for = None
        return (
            "👋 Hello! I am <b>EduQuery AI</b> 🤖<br><br>"
            "I can help you with:<br>"
            "🎓 <b>Courses</b> – MCA, B.Tech, MBA, BBA<br>"
            "💰 <b>Fees</b><br>"
            "📋 <b>Admissions</b><br>"
            "📅 <b>Exam Schedule</b><br>"
            "💼 <b>Placements</b><br>"
            "🖥 <b>Course Mode</b> (Online / Regular / Distance)<br><br>"
            "What would you like to know?"
        )

    # ── Bye ──
    if intent == "bye":
        current_course = None
        awaiting_course_for = None
        return "Goodbye! 👋 Feel free to come back anytime. Best of luck! 😊"

    # ── Course Selection ──
    if intent == "course_select":
        course = detect_course(text)
        if course:
            current_course = course
            return (
                f"You selected <b>{current_course}</b> 🎓<br><br>"
                "What would you like to know?<br>"
                "👉 Fees &nbsp;|&nbsp; 👉 Admission &nbsp;|&nbsp; 👉 Exam &nbsp;|&nbsp; 👉 Placement"
            )
        return (
            "Please choose a course:<br>"
            "🎓 <b>MCA</b> &nbsp;|&nbsp; <b>B.Tech</b> &nbsp;|&nbsp; <b>MBA</b> &nbsp;|&nbsp; <b>BBA</b>"
        )

    # ── Course Mode ──
    if intent == "course_mode":
        return (
            "We offer three modes of learning:<br><br>"
            "🎓 <b>Regular</b> – Traditional campus-based learning<br>"
            "💻 <b>Online</b> – Live + recorded classes from anywhere<br>"
            "📚 <b>Distance</b> – Self-paced, flexible learning"
        )

    # ── Fees ──
    if intent == "fees":
        # Course mentioned directly in this message (e.g. "fee for btech")
        course = detect_course(text)
        if course:
            current_course = course
            awaiting_course_for = None
            return fee_response(course)
        # Course was selected earlier in THIS conversation (awaiting_course_for flow)
        # Only use memory if it was set during this session flow — always ask otherwise
        awaiting_course_for = "fees"
        return (
            "Sure! Please tell me which course you are asking about:<br>"
            "🎓 <b>MCA</b> &nbsp;|&nbsp; <b>B.Tech</b> &nbsp;|&nbsp; <b>MBA</b> &nbsp;|&nbsp; <b>BBA</b>"
        )

    # ── Exam ──
    if intent == "exam":
        db_resp = get_db_response("exam")
        if db_resp:
            return db_resp
        return (
            "📅 <b>Exam Schedule</b><br><br>"
            "Semester exam schedules are published on the student portal 2 weeks before exams.<br>"
            "📌 Please visit your university portal or contact the exam cell for exact dates."
        )

    # ── Placement ──
    if intent == "placement":
        db_resp = get_db_response("placement")
        if db_resp:
            return db_resp + CALLBACK_TAG
        return (
            "💼 <b>Placement Support</b><br><br>"
            "✅ Dedicated placement cell<br>"
            "✅ Top companies visit campus every year<br>"
            "✅ Resume building &amp; interview prep sessions<br>"
            "✅ Strong alumni network<br><br>"
            "📌 Contact the placement office for company-specific records.<br><br>"
            "For further details, our support team can contact you."
            + CALLBACK_TAG
        )

    # ── Admission ──
    if intent == "admission":
        db_resp = get_db_response("admission")
        if db_resp:
            return db_resp + CALLBACK_TAG
        return (
            "📋 <b>Admission Process</b><br><br>"
            "1️⃣ Fill the online application form<br>"
            "2️⃣ Upload required documents<br>"
            "3️⃣ Pay the registration fee<br>"
            "4️⃣ Appear for counseling / entrance test (if applicable)<br>"
            "5️⃣ Confirm your seat<br><br>"
            "📌 Visit the admission portal or call the admission helpline for more details.<br><br>"
            "Need help? Our support team can contact you."
            + CALLBACK_TAG
        )

    # ── Default ──
    awaiting_course_for = None  # always clear stuck state on unrecognized input
    return (
        "🤔 I'm not sure I understood that.<br><br>"
        "I can help you with:<br>"
        "💰 <b>Fees</b> &nbsp;|&nbsp; 📋 <b>Admissions</b> &nbsp;|&nbsp; "
        "📅 <b>Exams</b> &nbsp;|&nbsp; 💼 <b>Placements</b> &nbsp;|&nbsp; 🖥 <b>Course Mode</b><br><br>"
        "Need help? Our support team can contact you."
        + CALLBACK_TAG
    )
