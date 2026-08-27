import re
import nltk

nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

stop_words = set(
    stopwords.words("english")
)

stemmer = PorterStemmer()


def clean_text(text):

    text = str(text).lower()

    text = re.sub(
        r"<.*?>",
        " ",
        text
    )

    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    text = re.sub(
        r"\S+@\S+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    words = text.split()

    words = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)