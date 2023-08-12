import joblib
import re
import pandas as pd
import os

class EmailClassifier:
    MODEL_PATH = os.path.join(os.path.dirname(__file__),'..', 'data', 'logistic_regression_model_latest_12.joblib')
    VECTORIZER_PATH = os.path.join(os.path.dirname(__file__),'..', 'data', 'tfidf_vectorizer_latest_12.joblib')

    def __init__(self,input_file,output_file) :
        self.input_file = input_file
        self.output_file = output_file
        self.df = pd.read_csv(self.input_file)
        self.lr = self.load_model(EmailClassifier.MODEL_PATH)
        self.tfidf_vectorizer = self.load_model(EmailClassifier.VECTORIZER_PATH)

    @staticmethod
    def load_model(path):
        print("Loading model from:", path)
        return joblib.load(path)

    def predict(self):

        unlabeled_vectors = self.tfidf_vectorizer.transform(self.df['text'])
        predictions = self.lr.predict(unlabeled_vectors)
        self.df['predicted_label'] = predictions
        self.df.loc[self.df['label'] == 'unlabeled', 'label'] = predictions


    def save_predictions(self):
        self.df.to_csv(self.output_file, index=False)

if __name__ == "__main__":
    # Initialize the cleaner with the input and output file paths
    classifier = EmailClassifier("output_cleaned.csv", "output_predicted.csv")

    # Run the cleaning pipeline
    classifier.predict()
    classifier.save_predictions()