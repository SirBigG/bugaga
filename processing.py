import json
import logging

import gensim
import numpy as np

from operator import itemgetter

from db import Session, Engine

from models.parser import Advert

from process import UkrainianStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier

from stop_words import get_stop_words


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in set(get_stop_words('uk') + get_stop_words('ru')):
            result.append(UkrainianStemmer(token).stem_word())
    return result


def processing():
    session = Session()

    _to_train = []
    with Engine.connect() as con:
        for row in con.execute('select category, data from (select *, row_number() over (partition by category) as rownum from advert) a where rownum <=1000;'):
            if row[0] is not None:
                item = json.loads(row[1])
                _to_train.append([' '.join(set(preprocess(f'{item["title"]}. {item["description"]}'))), row[0]])

    if not _to_train:
        logging.info('No data to train')
        return

    vectorizer = TfidfVectorizer()
    _to_train = sorted(_to_train, key=itemgetter(1))
    X = vectorizer.fit_transform([i[0] for i in _to_train])

    y_train = np.zeros(len(_to_train))

    for i, j in enumerate([i[1] for i in _to_train]):
        y_train[i] = j

    modelknn = KNeighborsClassifier(n_neighbors=7)
    modelknn.fit(X, y_train)

    test_adverts = session.query(Advert).filter(Advert.category.is_(None))

    for i in test_adverts:
        item = json.loads(i.data)
        predicted_labels_knn = modelknn.predict(
            vectorizer.transform([' '.join(set(preprocess(f'{item["title"]}. {item["description"]}')))]))
        i.category = predicted_labels_knn[0]

    session.commit()
    session.close()
