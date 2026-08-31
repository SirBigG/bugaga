import json
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from stop_words import get_stop_words

from .ukrainian_stemmer import UkrainianStemmer

TOKEN_RE = re.compile(r"(?:(?!\d)\w)+", re.UNICODE)
STOP_WORDS = set(get_stop_words("uk") + get_stop_words("ru"))


def preprocess(text):
    tokens = (
        token
        for token in TOKEN_RE.findall(text.lower())
        if 2 <= len(token) <= 15 and not token.startswith("_")
    )
    return [UkrainianStemmer(token).stem_word() for token in tokens if token not in STOP_WORDS]


def _advert_text(raw_data):
    item = json.loads(raw_data)
    return " ".join(set(preprocess(f"{item.get('title', '')}. {item.get('description', '')}")))


def classify(training_rows, raw_adverts):
    training = [(_advert_text(data), int(category)) for category, data in training_rows]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(text for text, _ in training)
    labels = [category for _, category in training]
    classifier = KNeighborsClassifier(n_neighbors=min(7, len(training)))
    classifier.fit(vectors, labels)
    predictions = classifier.predict(vectorizer.transform(_advert_text(data) for data in raw_adverts))
    return [int(category) for category in predictions]
