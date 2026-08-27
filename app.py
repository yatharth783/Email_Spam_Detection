import streamlit as st
import joblib
import re

from preprocessing import clean_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MailGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

/* Main header */
.hero {
    padding: 25px 30px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 25px;
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 17px;
    opacity: 0.75;
}

/* Cards */
.card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 15px;
}

/* Result cards */
.safe-card {
    padding: 25px;
    border-radius: 18px;
    border: 2px solid #2e8b57;
    margin-top: 20px;
}

.danger-card {
    padding: 25px;
    border-radius: 18px;
    border: 2px solid #dc3545;
    margin-top: 20px;
}

/* Small labels */
.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 12px;
}

/* Footer */
.footer {
    text-align: center;
    opacity: 0.65;
    padding: 25px;
    font-size: 13px;
}

/* Hide default menu */
#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model():
    return joblib.load("models/spam_model.pkl")


try:
    model = load_model()
except Exception as e:
    st.error("❌ Model could not be loaded.")
    st.code(str(e))
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🛡️ MailGuard AI")

    st.caption("Intelligent Email Security System")

    st.divider()

    st.markdown("### 🔍 Detection Features")

    st.write("✅ Spam Detection")
    st.write("✅ Phishing Detection")
    st.write("✅ Confidence Analysis")
    st.write("✅ URL Detection")
    st.write("✅ Suspicious Keyword Analysis")
    st.write("✅ Email & Phone Detection")

    st.divider()

    st.markdown("### 🤖 Machine Learning")

    st.write("TF-IDF Text Features")
    st.write("Supervised Classification")

    st.divider()

    st.caption("Version 1.0")
    st.caption("AI-Based Email Security")


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🛡️ MailGuard AI
</div>

<div class="hero-subtitle">
Intelligent Email Spam & Phishing Detection System
</div>

</div>
""", unsafe_allow_html=True)


st.write(
    "Analyze an email using a machine-learning classifier "
    "and identify potentially unwanted or suspicious messages."
)


# =========================================================
# EMAIL INPUT SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📨 Email Information</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    sender = st.text_input(
        "👤 Sender",
        placeholder="sender@example.com"
    )

with col2:

    subject = st.text_input(
        "📝 Subject",
        placeholder="Enter email subject..."
    )


email_body = st.text_area(
    "💬 Email Message",
    height=250,
    placeholder="Paste the complete email message here..."
)


# =========================================================
# SAMPLE EMAILS
# =========================================================

st.markdown("##### 🧪 Quick Test")

sample1, sample2 = st.columns(2)

with sample1:

    if st.button(
        "🚨 Load Spam Example",
        use_container_width=True
    ):

        st.session_state["sender"] = "winner@unknown.com"
        st.session_state["subject"] = "Congratulations! You Won"
        st.session_state["body"] = (
            "Congratulations! You have won a $1000 prize. "
            "Click here now to claim your reward. "
            "Verify your account immediately."
        )

        st.rerun()


with sample2:

    if st.button(
        "✅ Load Genuine Example",
        use_container_width=True
    ):

        st.session_state["sender"] = "manager@company.com"
        st.session_state["subject"] = "Tomorrow's Meeting"
        st.session_state["body"] = (
            "Hi, this is a reminder about our meeting tomorrow "
            "at 10 AM. Please review the attached documents "
            "before the meeting."
        )

        st.rerun()


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.write("")

analyze = st.button(
    "🔍  ANALYZE EMAIL",
    use_container_width=True,
    type="primary"
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze:

    if (
        not sender.strip()
        and not subject.strip()
        and not email_body.strip()
    ):

        st.warning(
            "⚠️ Please enter an email subject or message."
        )

    else:

        # -------------------------------------------------
        # COMBINE INPUT
        # -------------------------------------------------

        combined_text = (
            f"Sender: {sender} "
            f"Subject: {subject} "
            f"Body: {email_body}"
        )


        # -------------------------------------------------
        # PREPROCESSING
        # -------------------------------------------------

        cleaned_text = clean_text(combined_text)


        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        prediction = model.predict(
            [cleaned_text]
        )[0]

        prediction_str = (
            str(prediction)
            .strip()
            .lower()
        )


        # -------------------------------------------------
        # PROBABILITY
        # -------------------------------------------------

        probability_dict = {}
        confidence = None

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(
                [cleaned_text]
            )[0]

            classes = model.classes_

            probability_dict = dict(
                zip(classes, probabilities)
            )

            confidence = max(probabilities) * 100


        # -------------------------------------------------
        # CLASSIFICATION
        # -------------------------------------------------

        spam_values = {
            "1",
            "spam",
            "junk",
            "phishing",
            "true"
        }

        ham_values = {
            "0",
            "ham",
            "genuine",
            "not spam",
            "legitimate",
            "false"
        }


        if prediction_str in spam_values:

            is_spam = True

        elif prediction_str in ham_values:

            is_spam = False

        else:

            if probability_dict:

                predicted_probability = probability_dict.get(
                    prediction,
                    probability_dict.get(
                        str(prediction),
                        0
                    )
                )

                is_spam = (
                    predicted_probability >= 0.5
                )

            else:

                is_spam = False


        # =================================================
        # RESULT
        # =================================================

        st.divider()

        st.markdown(
            '<div class="section-title">🔎 Security Analysis</div>',
            unsafe_allow_html=True
        )


        if is_spam:

            st.markdown("""
            <div class="danger-card">

            <h2>🚨 SPAM EMAIL DETECTED</h2>

            <p>
            The AI model identified this message as potentially
            unwanted, suspicious or malicious.
            </p>

            </div>
            """, unsafe_allow_html=True)

            threat = "HIGH RISK"

        else:

            st.markdown("""
            <div class="safe-card">

            <h2>✅ GENUINE EMAIL</h2>

            <p>
            The AI model classified this message as a legitimate
            email.
            </p>

            </div>
            """, unsafe_allow_html=True)

            threat = "LOW RISK"


        # =================================================
        # SUMMARY METRICS
        # =================================================

        st.write("")

        st.markdown(
            '<div class="section-title">📊 Detection Summary</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)


        with m1:

            if confidence is not None:

                st.metric(
                    "🎯 Confidence",
                    f"{confidence:.2f}%"
                )

            else:

                st.metric(
                    "🎯 Confidence",
                    "N/A"
                )


        with m2:

            st.metric(
                "🛡️ Threat",
                threat
            )


        with m3:

            st.metric(
                "📝 Words",
                len(combined_text.split())
            )


        with m4:

            st.metric(
                "🔗 Links",
                len(
                    re.findall(
                        r"https?://[^\s]+|www\.[^\s]+",
                        combined_text,
                        flags=re.IGNORECASE
                    )
                )
            )


        # =================================================
        # SECURITY SCAN
        # =================================================

        st.markdown(
            '<div class="section-title">🛡️ Security Scan</div>',
            unsafe_allow_html=True
        )


        urls = re.findall(
            r"https?://[^\s]+|www\.[^\s]+",
            combined_text,
            flags=re.IGNORECASE
        )


        emails = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            combined_text
        )


        phones = re.findall(
            r"\b\d{10}\b",
            combined_text
        )


        suspicious_words = [

            "urgent",
            "winner",
            "won",
            "prize",
            "reward",
            "free",
            "click",
            "claim",
            "offer",
            "money",
            "lottery",
            "password",
            "verify",
            "account",
            "bank",
            "congratulations",
            "login",
            "credit card",
            "debit card",
            "otp",
            "security alert",
            "limited time",
            "act now",
            "confirm",
            "suspended",
            "payment"

        ]


        text_lower = combined_text.lower()


        found_words = [
            word
            for word in suspicious_words
            if word in text_lower
        ]


        s1, s2, s3, s4 = st.columns(4)


        with s1:
            st.metric(
                "🔗 URLs",
                len(urls)
            )

        with s2:
            st.metric(
                "📧 Emails",
                len(emails)
            )

        with s3:
            st.metric(
                "📱 Phone Numbers",
                len(phones)
            )

        with s4:
            st.metric(
                "⚠️ Suspicious Words",
                len(found_words)
            )


        # =================================================
        # SUSPICIOUS KEYWORDS
        # =================================================

        if found_words:

            st.warning(
                "⚠️ Suspicious keywords detected: "
                + ", ".join(
                    sorted(set(found_words))
                )
            )

        else:

            st.success(
                "✅ No common suspicious keywords detected."
            )


        # =================================================
        # PROBABILITY
        # =================================================

        if probability_dict:

            st.markdown(
                '<div class="section-title">📈 Prediction Probability</div>',
                unsafe_allow_html=True
            )


            for label, probability in probability_dict.items():

                label_lower = str(label).lower()


                if label_lower in spam_values:

                    label_name = "🚨 Spam"

                elif label_lower in ham_values:

                    label_name = "✅ Genuine / Ham"

                else:

                    label_name = str(label)


                percentage = probability * 100


                st.write(
                    f"**{label_name} — "
                    f"{percentage:.2f}%**"
                )

                st.progress(
                    float(probability)
                )


        # =================================================
        # MODEL DETAILS
        # =================================================

        with st.expander("🧠 View Model Details"):

            st.write(
                "**Model Prediction:**",
                prediction
            )

            if hasattr(model, "classes_"):

                st.write(
                    "**Available Classes:**",
                    list(model.classes_)
                )

            st.write(
                "**Prediction Method:**",
                "Machine Learning Text Classification"
            )

            st.write(
                "**Text Processing:**",
                "Cleaning + Tokenization + Stopword Removal + Stemming"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div class="footer">

🛡️ <b>MailGuard AI</b> — Intelligent Email Security System

<br>

Built using Python • Scikit-learn • Streamlit • NLP

<br><br>

⚠️ AI predictions are informational and should not replace
professional email security solutions.

</div>
""", unsafe_allow_html=True)
