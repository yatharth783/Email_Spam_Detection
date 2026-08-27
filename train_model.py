import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from preprocessing import clean_text


# ==========================================
# CONFIGURATION
# ==========================================

DATA_PATH = "data/spam.csv"
MODEL_PATH = "models/spam_model.pkl"


# ==========================================
# LOAD DATASET
# ==========================================

print("\n--- Loading Dataset ---")

df = pd.read_csv(
    DATA_PATH,
    sep="\t",
    encoding="utf-8",
    low_memory=False
)

print("Dataset Shape:", df.shape)


# ==========================================
# REQUIRED COLUMNS
# ==========================================

required_columns = [
    "subject",
    "body_plain",
    "from_address",
    "label"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column '{column}' not found."
        )


# ==========================================
# SELECT COLUMNS
# ==========================================

df = df[
    [
        "subject",
        "body_plain",
        "from_address",
        "label"
    ]
].copy()


# ==========================================
# CLEAN MISSING VALUES
# ==========================================

df["subject"] = df["subject"].fillna("")
df["body_plain"] = df["body_plain"].fillna("")
df["from_address"] = df["from_address"].fillna("")


# ==========================================
# LABEL CLEANING
# ==========================================

df["label"] = (
    df["label"]
    .astype(str)
    .str.strip()
)


# ==========================================
# REMOVE INVALID LABELS
# ==========================================

df = df[
    df["label"].isin(["0", "1"])
].copy()


# ==========================================
# REMOVE DUPLICATES
# ==========================================

df = df.drop_duplicates(
    subset=[
        "subject",
        "body_plain",
        "from_address"
    ]
)


print("\nDataset after cleaning:", df.shape)


# ==========================================
# CLASS DISTRIBUTION
# ==========================================

print("\n--- Class Distribution ---")
print(df["label"].value_counts())


# ==========================================
# CREATE COMBINED EMAIL TEXT
# ==========================================

df["raw_text"] = (
    "sender " +
    df["from_address"].astype(str) +
    " subject " +
    df["subject"].astype(str) +
    " body " +
    df["body_plain"].astype(str)
)


# ==========================================
# CLEAN TEXT
# ==========================================

print("\n--- Cleaning Emails ---")

df["clean_text"] = df["raw_text"].apply(
    clean_text
)


# ==========================================
# FEATURES AND TARGET
# ==========================================

X = df["clean_text"]
y = df["label"]


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# MODEL PIPELINE
# ==========================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=100000,
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=True,
            strip_accents="unicode"
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            C=2.0
        )
    )
])


# ==========================================
# TRAIN
# ==========================================

print("\n--- Training Model ---")

model.fit(
    X_train,
    y_train
)

print("Training completed!")


# ==========================================
# EVALUATION
# ==========================================

print("\n--- Evaluating Model ---")

y_pred = model.predict(X_test)


# ==========================================
# ACCURACY
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n====================================")
print("MODEL PERFORMANCE")
print("====================================")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ==========================================
# CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Genuine / Ham",
            "Spam"
        ]
    )
)


# ==========================================
# CONFUSION MATRIX
# ==========================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)


print("\n====================================")
print("MODEL SAVED SUCCESSFULLY")
print("====================================")

print(
    f"Saved at: {MODEL_PATH}"
)

print("\nModel Classes:")
print(model.classes_)