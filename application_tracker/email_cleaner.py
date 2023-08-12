
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

class EmailCleaner:

    def __init__(self,input_file,output_file) :
        self.input_file = input_file
        self.output_file = output_file
        self.df = pd.read_csv(self.input_file)
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))
        


    def add_label_column(self, label='unlabeled'):
        """
        Adds a column with a default label.
        """
        self.df['label'] = label

    def drop_column(self,column_name):

        if column_name in self.df.columns:
            self.df.drop(column_name,axis=1,inplace=True)

    def replace_nan_in_body(self):
        """
        Replaces NaN values in 'body' with values from 'snippet'.
        """ 
        self.df['body'] = self.df.apply(lambda row:row['snippet'] if pd.isna(row['body']) else row['body'],axis=1)

    
    def drop_rows_with_nan(self):

        columns_with_nan = self.df.columns[self.df.isnull().any()].tolist()

        rows_with_nan = []

        for column in columns_with_nan:

            nan_rows = self.df[self.df[column].isnull()].index.tolist()
            rows_with_nan.extend(nan_rows)
        rows_with_nan = list(set(rows_with_nan))
        self.df = self.df.drop(rows_with_nan, axis=0).reset_index(drop=True)

    def _remove_stop_words(self, text):
        tokens = text.split()  # Split the text into words
        filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]
        return ' '.join(filtered_tokens)

    def _convert_to_lower(self):
        self.df['text'] = self.df['text'].str.lower()

    def _remove_html_tags(self):
        self.df['text'] = self.df['text'].str.replace('<.*?>', '', regex=True)

    def _remove_urls(self):
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self.df['text'] = self.df['text'].str.replace(url_pattern, '', regex=True)

    def _remove_email_headers(self):
        headers_pattern = r'^(From:|To:|Subject:|Date:|CC:).*\n?'
        self.df['text'] = self.df['text'].str.replace(headers_pattern, '', regex=True, flags=re.MULTILINE)

    def _remove_special_characters(self):
        special_chars_pattern = r'[^a-zA-Z0-9 #]'
        self.df['text'] = self.df['text'].str.replace(special_chars_pattern, '', regex=True)

    def _remove_excess_characters(self):
        self.df['text'] = self.df['text'].str.replace('-+', '', regex=True)
        self.df['text'] = self.df['text'].str.replace(' +', ' ', regex=True)
        self.df['text'] = self.df['text'].str.replace('\n+', '\n', regex=True)

    def _trim_spaces(self):
        self.df['text'] = self.df['text'].str.strip()
    
    def preprocess_text(self):
        self._convert_to_lower()
        self._remove_html_tags()
        self._remove_urls()
        self._remove_email_headers()
        self._remove_special_characters()
        self._remove_excess_characters()
        self._trim_spaces()
        self.df['text'] = self.df['text'].apply(self._remove_stop_words)

    def save_cleaned_data(self):
        """
        Saves the cleaned dataframe to a specified output file.
        """
        self.df.to_csv(self.output_file, index=False)
    
    def run_cleaning_pipeline(self):
        """
        Runs the cleaning operations in sequence.
        """
        self.add_label_column()
        self.drop_column('to')
        self.replace_nan_in_body()  # Handle NaNs before concatenation
        self.df['text'] = self.df['body'] + ' ' + self.df['subject'] + ' ' + self.df['snippet']
        self.drop_column('body')
        self.drop_column('subject')
        self.drop_column('snippet')
        self.drop_rows_with_nan()
        self.preprocess_text()
        self.save_cleaned_data()

if __name__ == "__main__":
    # Initialize the cleaner with the input and output file paths
    cleaner = EmailCleaner("output_test.csv", "output_cleaned.csv")

    # Run the cleaning pipeline
    cleaner.run_cleaning_pipeline()