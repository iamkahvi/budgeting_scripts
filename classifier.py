import pickle
from sklearn.feature_extraction.text import TfidfVectorizer


class CreditCardTransactionClassifier:
    def __init__(self, model_path, vectorizer_path):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)

    def preprocess(self, input_data):
        return self.vectorizer.transform(input_data)

    def predict(self, input_data):
        preprocessed_data = self.preprocess(input_data)
        return self.model.predict(preprocessed_data)


def main():
    # Create an instance of the classifier
    classifier = CreditCardTransactionClassifier("sgd_classifier.pkl", "vectorizer.pkl")

    # Make predictions using the classifier
    input_data = [
        "NOODLEBOX - SHELBOURNE",
        "BOLD BUTCHERY & GRILL",
    ]
    predictions = classifier.predict(input_data)
    print(predictions)


if __name__ == "__main__":
    main()
