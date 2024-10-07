import pandas as pd
import joblib
import os

def categorize_new_data(excel_file_path, model_dir, output_file):
    model_path = os.path.join(model_dir, 'text_classifier_model.pkl')
    vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
    label_encoder_path = os.path.join(model_dir, 'label_encoder.pkl')

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    label_encoder = joblib.load(label_encoder_path)

    data = pd.read_excel(excel_file_path)

    if 'summary' not in data.columns:
        raise ValueError("The input Excel file must contain a 'summary' column.")

    summaries = data['summary']

    X_new = vectorizer.transform(summaries)

    predictions = model.predict(X_new)

    predicted_categories = label_encoder.inverse_transform(predictions)

    data['Predicted Category'] = predicted_categories
    data.to_excel(output_file, index=False)

    print(f"Categorized data saved to {output_file}")


new_data_file_path = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/Scrapping Output data/Data_syndicate.xlsx"
output_directory = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM"
output_categorized_file = "/Users/sathishm/Documents/TSM Folder/Datathon Stage 2/LLM Output data/Datathon1.xlsx"

categorize_new_data(new_data_file_path, output_directory, output_categorized_file)
