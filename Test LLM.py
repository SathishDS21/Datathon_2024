import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_model(excel_file_path, model_output_dir):
    data = pd.read_excel(excel_file_path)

    summaries = data['summary']
    categories = data['category']

    label_encoder = LabelEncoder()
    encoded_categories = label_encoder.fit_transform(categories)  # Convert categories to numerical values

    vectorizer = TfidfVectorizer(max_features=5000)  # Limit the vocabulary size to 5000 most common words
    X = vectorizer.fit_transform(summaries)

    X_train, X_test, y_train, y_test = train_test_split(X, encoded_categories, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    if not os.path.exists(model_output_dir):
        os.makedirs(model_output_dir)

    model_path = os.path.join(model_output_dir, 'text_classifier_model.pkl')
    vectorizer_path = os.path.join(model_output_dir, 'vectorizer.pkl')
    label_encoder_path = os.path.join(model_output_dir, 'label_encoder.pkl')

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(label_encoder, label_encoder_path)

    print(f"Model, vectorizer, and label encoder saved to {model_output_dir}")

training_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Training Data/Training data.xlsx"
output_directory = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM"

train_model(training_file_path, output_directory)
