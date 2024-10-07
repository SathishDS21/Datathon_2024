import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Function to train a model based on the provided Excel data
def train_model(excel_file_path, model_output_dir):
    # Step 1: Read the Excel file
    data = pd.read_excel(excel_file_path)

    # Assuming the Excel sheet has two columns: 'summary' and 'category'
    # 'summary' is the text (20-word summaries) and 'category' is the target variable
    summaries = data['summary']
    categories = data['category']

    # Step 2: Preprocess the labels using LabelEncoder
    label_encoder = LabelEncoder()
    encoded_categories = label_encoder.fit_transform(categories)  # Convert categories to numerical values

    # Step 3: Preprocess the text data using TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=5000)  # Limit the vocabulary size to 5000 most common words
    X = vectorizer.fit_transform(summaries)

    # Step 4: Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, encoded_categories, test_size=0.2, random_state=42)

    # Step 5: Train a Logistic Regression model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Step 6: Evaluate the model on the test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Step 7: Save the trained model, vectorizer, and label encoder
    if not os.path.exists(model_output_dir):
        os.makedirs(model_output_dir)

    model_path = os.path.join(model_output_dir, 'text_classifier_model.pkl')
    vectorizer_path = os.path.join(model_output_dir, 'vectorizer.pkl')
    label_encoder_path = os.path.join(model_output_dir, 'label_encoder.pkl')

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(label_encoder, label_encoder_path)

    print(f"Model, vectorizer, and label encoder saved to {model_output_dir}")

# Example usage
training_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Training Data/Training data.xlsx"
output_directory = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM"

# Call the function to train and save the model
train_model(training_file_path, output_directory)