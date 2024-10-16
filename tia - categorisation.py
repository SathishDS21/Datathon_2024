
import pandas as pd
import joblib
import os


# Function to load the model, vectorizer, and label encoder, and categorize new data
def categorize_new_data(excel_file_path, model_dir, output_file):
    # Step 1: Load the trained model, vectorizer, and label encoder
    model_path = os.path.join(model_dir, 'text_classifier_model.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
    label_encoder_path = os.path.join(model_dir, 'label_encoder.pkl')

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    label_encoder = joblib.load(label_encoder_path)

    # Step 2: Read the new data (only the summaries) from the Excel file
    data = pd.read_excel(excel_file_path)

    if 'summary' not in data.columns:
        raise ValueError("The input Excel file must contain a 'summary' column.")

    summaries = data['summary']

    # Step 3: Preprocess the new summaries using the loaded vectorizer
    X_new = vectorizer.transform(summaries)

    # Step 4: Make predictions using the loaded model
    predictions = model.predict(X_new)

    # Step 5: Convert the numerical predictions back to original categories using the label encoder
    predicted_categories = label_encoder.inverse_transform(predictions)

    # Step 6: Save the predictions to a new Excel file
    data['Predicted Category'] = predicted_categories
    data.to_excel(output_file, index=False)

    print(f"Categorized data saved to {output_file}")


# Example usage
new_data_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_syndicate.xlsx"
output_directory = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM"
output_categorized_file = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM Output data/Datathon1.xlsx"

# Categorize new summaries
categorize_new_data(new_data_file_path, output_directory, output_categorized_file)