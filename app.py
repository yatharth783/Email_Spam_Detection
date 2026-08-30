import streamlit as st
import joblib
import re
from preprocessing import clean_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Email Security Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* ================= APP ================= */

    .stApp {
        background-color: #080d18;
    }

    .block-container {
        max-width: 1350px;
        padding-top: 28px;
        padding-bottom: 20px;
    }

    /* ================= HEADER ================= */

    h1 {
        font-size: 34px !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        margin-bottom: 0 !important;
    }

    .stCaption {
        color: #7f8da3 !important;
    }

    /* ================= INPUTS ================= */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] {
        background-color: #0d1524 !important;
        border: 1px solid #263449 !important;
        border-radius: 10px !important;
    }

    input,
    textarea {
        color: #f8fafc !important;
    }

    label {
        color: #b8c4d6 !important;
        font-weight: 600 !important;
    }

    /* ================= BUTTON ================= */

    .stButton > button {
        width: 100%;
        height: 48px;
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    /* ================= METRICS ================= */

    div[data-testid="stMetric"] {
        background-color: #0d1524;
        border: 1px solid #263449;
        border-radius: 12px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #7f8da3 !important;
        font-size: 11px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 21px !important;
        font-weight: 700 !important;
    }

    /* ================= TABS ================= */

    button[data-baseweb="tab"] {
        color: #8b99ad !important;
        font-weight: 600 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #60a5fa !important;
    }

    /* ================= ALERTS ================= */

    div[data-testid="stAlert"] {
        border-radius: 10px !important;
    }

    /* ================= PROGRESS ================= */

    div[data-testid="stProgress"] > div {
        background-color: #182235 !important;
    }

    /* ================= FOOTER ================= */

    footer {
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


model = load_model()


# =========================================================
# HEADER
# =========================================================

st.title("🛡️ Email Security Analyzer")

st.caption(
    "AI-powered spam detection and email threat analysis"
)

st.write("")


# =========================================================
# MAIN WORKSPACE
# =========================================================

left, right = st.columns(
    [1.05, 0.95],
    gap="large"
)


# =========================================================
# LEFT SIDE — EMAIL INPUT
# =========================================================

with left:

    st.subheader("📨 Email Details")

    sender = st.text_input(
        "Sender Email",
        placeholder="example@gmail.com"
    )

    subject = st.text_input(
        "Email Subject",
        placeholder="Enter email subject..."
    )

    email_body = st.text_area(
        "Email Body",
        height=260,
        placeholder="Paste the complete email content here..."
    )

    st.write("")

    analyze = st.button(
        "🔍  ANALYZE EMAIL",
        use_container_width=True
    )


# =========================================================
# RIGHT SIDE — THREAT ASSESSMENT
# =========================================================

with right:

    st.subheader("🎯 Threat Assessment")

    if not analyze:

        st.info(
            "Enter the email details and click "
            "**Analyze Email** to start the security scan."
        )

        st.write("")

        st.caption("AI ENGINE STATUS")

        st.success("● ONLINE")

        st.caption(
            "Ready to analyze email content"
        )

    else:

        if not subject.strip() and not email_body.strip():

            st.warning(
                "⚠️ Please enter an email subject or email body."
            )

        else:

            # -------------------------------------------------
            # COMBINE EMAIL
            # -------------------------------------------------

            combined_text = f"{subject} {email_body}"

            cleaned_text = clean_text(
                combined_text
            )


            # -------------------------------------------------
            # MODEL PREDICTION
            # -------------------------------------------------

            prediction = model.predict(
                [cleaned_text]
            )[0]

            probabilities = model.predict_proba(
                [cleaned_text]
            )[0]

            classes = model.classes_

            probability_dict = dict(
                zip(classes, probabilities)
            )

            confidence = max(
                probabilities
            ) * 100


            # -------------------------------------------------
            # THREAT RESULT
            # -------------------------------------------------

            if str(prediction) == "1":

                st.error(
                    "🚨 SPAM EMAIL DETECTED"
                )

                st.caption(
                    "High-risk email detected by the AI classifier."
                )

                threat = "HIGH RISK"

            else:

                st.success(
                    "✅ GENUINE EMAIL"
                )

                st.caption(
                    "No spam classification detected by the AI model."
                )

                threat = "LOW RISK"


            # -------------------------------------------------
            # RESULT METRICS
            # -------------------------------------------------

            st.write("")

            a, b = st.columns(2)

            with a:

                st.metric(
                    "AI Confidence",
                    f"{confidence:.2f}%"
                )

            with b:

                st.metric(
                    "Threat Level",
                    threat
                )

            st.write("")

            st.caption("Model Confidence")

            st.progress(
                float(confidence / 100)
            )


# =========================================================
# SECURITY ANALYSIS
# =========================================================

if analyze and (
    subject.strip() or email_body.strip()
):

    # =====================================================
    # URL DETECTION
    # =====================================================

    urls = re.findall(
        r"https?://\S+|www\.\S+",
        combined_text,
        flags=re.IGNORECASE
    )


    # =====================================================
    # EMAIL ADDRESS DETECTION
    # =====================================================

    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        combined_text
    )


    # =====================================================
    # PHONE NUMBER DETECTION
    # =====================================================

    phones = re.findall(
        r"\b\d{10}\b",
        combined_text
    )


    # =====================================================
    # SUSPICIOUS KEYWORDS
    # =====================================================

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
        "congratulations"
    ]

    found_words = sorted(
        set(
            word
            for word in suspicious_words
            if word in combined_text.lower()
        )
    )


    # =====================================================
    # WORD COUNT
    # =====================================================

    word_count = len(
        combined_text.split()
    )


    # =====================================================
    # SECURITY OVERVIEW
    # =====================================================

    st.write("")

    st.subheader("🔐 Security Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "🔗 URLs",
            len(urls)
        )

    with c2:

        st.metric(
            "📧 Emails",
            len(emails)
        )

    with c3:

        st.metric(
            "📱 Phones",
            len(phones)
        )

    with c4:

        st.metric(
            "⚠️ Indicators",
            len(found_words)
        )

    with c5:

        st.metric(
            "📝 Words",
            word_count
        )


    # =====================================================
    # TABS
    # =====================================================

    st.write("")

    overview_tab, security_tab, probability_tab = st.tabs(
        [
            "📋 Overview",
            "🛡️ Security Checks",
            "📊 Probability"
        ]
    )


    # =====================================================
    # OVERVIEW TAB
    # =====================================================

    with overview_tab:

        st.write("")

        if str(prediction) == "1":

            st.warning(
                "⚠️ This email contains characteristics "
                "commonly associated with spam."
            )

        else:

            st.success(
                "✓ The email appears legitimate according "
                "to the trained classification model."
            )

        st.write("")

        st.write("**Email Information**")

        info1, info2 = st.columns(2)

        with info1:

            st.caption("Sender")

            st.write(
                sender
                if sender
                else "Not provided"
            )

        with info2:

            st.caption("Subject")

            st.write(
                subject
                if subject
                else "Not provided"
            )


    # =====================================================
    # SECURITY CHECKS TAB
    # =====================================================

    with security_tab:

        st.write("")

        if urls:

            st.warning(
                f"🔗 {len(urls)} URL(s) detected in the email."
            )

        else:

            st.success(
                "✓ No URLs detected."
            )


        if emails:

            st.info(
                f"📧 {len(emails)} email address(es) detected."
            )


        if phones:

            st.info(
                f"📱 {len(phones)} phone number(s) detected."
            )


        st.write("")

        if found_words:

            st.warning(
                "⚠️ Suspicious keywords detected:"
            )

            st.write(
                ", ".join(found_words)
            )

        else:

            st.success(
                "✓ No common suspicious keywords detected."
            )


    # =====================================================
    # PROBABILITY TAB
    # =====================================================

    with probability_tab:

        st.write("")

        for label, probability in probability_dict.items():

            if str(label) == "1":

                label_name = "🚨 Spam"

            else:

                label_name = "✅ Genuine / Ham"

            percentage = probability * 100

            st.write(
                f"**{label_name}** — "
                f"{percentage:.2f}%"
            )

            st.progress(
                float(probability)
            )


# =========================================================
# FOOTER
# =========================================================

st.write("")

st.caption(
    "🛡️ Email Security Analyzer  •  "
    "AI Spam Detection  •  "
    "Python + Scikit-learn + Streamlit"
)