import streamlit as st
import joblib
import re
from preprocessing import clean_text


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Email Security Analyzer",
    page_icon="📧",
    layout="wide"
)


# ==========================================
# LOAD MODEL
# ==========================================

@st.cache_resource
def load_model():
    return joblib.load("models/spam_model.pkl")


model = load_model()


# ==========================================
# HEADER
# ==========================================

st.title("📧 Email Security Analyzer")

st.markdown("### 🤖 AI-Powered Spam & Phishing Detection")

st.write(
    "Analyze an email and detect whether it is "
    "**Spam** or **Genuine (Ham)** using Machine Learning."
)

st.divider()


# ==========================================
# EMAIL INFORMATION
# ==========================================

col1, col2 = st.columns(2)

with col1:
    sender = st.text_input(
        "👤 Sender Email",
        placeholder="example@gmail.com"
    )

with col2:
    subject = st.text_input(
        "📝 Email Subject",
        placeholder="Enter email subject..."
    )


# ==========================================
# EMAIL BODY
# ==========================================

email_body = st.text_area(
    "💬 Email Body",
    height=280,
    placeholder="Paste the complete email content here..."
)

st.write("")


# ==========================================
# ANALYZE BUTTON
# ==========================================

analyze = st.button(
    "🔍 Analyze Email",
    use_container_width=True
)


# ==========================================
# ANALYSIS
# ==========================================

if analyze:

    if (
        not sender.strip()
        and not subject.strip()
        and not email_body.strip()
    ):
        st.warning(
            "⚠️ Please enter sender email, subject or email body."
        )

    else:

        # ==================================
        # COMBINE EMAIL DATA
        # ==================================

        combined_text = (
            f"Sender: {sender} "
            f"Subject: {subject} "
            f"Body: {email_body}"
        )


        # ==================================
        # CLEAN TEXT
        # ==================================

        cleaned_text = clean_text(combined_text)


        # ==================================
        # MODEL PREDICTION
        # ==================================

        prediction = model.predict([cleaned_text])[0]

        prediction_str = str(prediction).strip().lower()


        # ==================================
        # PROBABILITY
        # ==================================

        confidence = None
        probability_dict = {}

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(
                [cleaned_text]
            )[0]

            classes = model.classes_

            probability_dict = dict(
                zip(classes, probabilities)
            )

            confidence = max(probabilities) * 100


        # ==================================
        # SPAM / HAM VALUES
        # ==================================

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


        # ==================================
        # DETERMINE RESULT
        # ==================================

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

                is_spam = predicted_probability >= 0.5

            else:

                is_spam = False


        # ==================================
        # RESULT
        # ==================================

        st.divider()

        st.subheader("🔍 Analysis Result")


        if is_spam:

            st.error("🚨 SPAM EMAIL DETECTED")

            st.warning(
                "This email shows characteristics commonly "
                "associated with spam or potentially malicious messages."
            )

            threat = "🔴 HIGH RISK"

        else:

            st.success("✅ GENUINE EMAIL")

            st.info(
                "This email appears to be a legitimate message."
            )

            threat = "🟢 LOW RISK"


        # ==================================
        # DETECTION SUMMARY
        # ==================================

        st.subheader("📊 Detection Summary")

        m1, m2, m3 = st.columns(3)


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
                "🛡️ Threat Level",
                threat
            )


        with m3:

            word_count = len(
                combined_text.split()
            )

            st.metric(
                "📝 Word Count",
                word_count
            )


        # ==================================
        # EMAIL SECURITY CHECKS
        # ==================================

        st.subheader("🛡️ Email Security Checks")


        # URLs
        urls = re.findall(
            r"https?://[^\s]+|www\.[^\s]+",
            combined_text,
            flags=re.IGNORECASE
        )


        # Email addresses
        emails = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            combined_text
        )


        # Phone numbers
        phones = re.findall(
            r"\b\d{10}\b",
            combined_text
        )


        # ==================================
        # SUSPICIOUS KEYWORDS
        # ==================================

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


        # ==================================
        # SECURITY METRICS
        # ==================================

        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "🔗 URLs",
                len(urls)
            )


        with c2:

            st.metric(
                "📧 Email Addresses",
                len(emails)
            )


        with c3:

            st.metric(
                "📱 Phone Numbers",
                len(phones)
            )


        with c4:

            st.metric(
                "⚠️ Suspicious Words",
                len(found_words)
            )


        # ==================================
        # SUSPICIOUS KEYWORDS
        # ==================================

        if found_words:

            st.write(
                "**⚠️ Suspicious Keywords Found:**"
            )

            st.write(
                ", ".join(
                    sorted(set(found_words))
                )
            )

        else:

            st.write(
                "✅ No common suspicious keywords detected."
            )


        # ==================================
        # PROBABILITY BREAKDOWN
        # ==================================

        if probability_dict:

            st.subheader(
                "📈 Prediction Probability"
            )


            for label, probability in probability_dict.items():

                label_lower = str(label).lower()


                if label_lower in spam_values:

                    label_name = "🚨 Spam"

                elif label_lower in ham_values:

                    label_name = "✅ Genuine / Ham"

                else:

                    label_name = str(label)


                st.write(
                    f"**{label_name}: "
                    f"{probability * 100:.2f}%**"
                )

                st.progress(
                    float(probability)
                )


        # ==================================
        # MODEL DETAILS
        # ==================================

        with st.expander("🔧 Model Details"):

            st.write(
                "**Raw Model Prediction:**",
                prediction
            )

            st.write(
                "**Model Classes:**",
                list(model.classes_)
                if hasattr(model, "classes_")
                else "Not available"
            )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "⚠️ This system is an AI-based classifier and should "
    "not be considered a replacement for professional email security tools."
)
