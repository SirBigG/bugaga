import json
import logging

import pandas as pd
import gensim
import numpy as np

from operator import itemgetter

from db import Session

from models.parser import Advert

from process import UkrainianStemmer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(UkrainianStemmer(token).stem_word())
    return result


def process_data():
    session = Session()
    adverts = session.query(Advert).all()
    _to_pandas = list()
    for i in adverts:
        item = json.loads(i.data)
        _to_pandas.append(f'{item["title"]}. {item["description"]}')

    bad_words = ["цена", "продам", "телефону", "вага", "місяців", "года", "суточный", "суточные", "возможна",
                 "якщо", "ціна", "після", "високої", "домашні", "року", "весом", "номер", "показать", "маса", "мають",
                 "продажа", "месяца", "возраст", "породы", "ответить", "также", "менее", "следует", "учитывать",
                 "данный", "очень", "вывоз", "робочих", "доставка", "также", "можно", "приймаємо", "заказ",
                 "отличаются", "лежаки", "набирают", "конце", "месяцев", "после", "новой"]
    df = pd.DataFrame(data={"text": _to_pandas})
    to_dictionary = list()
    for i in range(0, len(df)):
        item = set(preprocess(df.iloc[i][0]))
        item = list(item)
        for j in item:
            if j in bad_words:
                item.remove(j)
        df.iloc[i][0] = item
        to_dictionary.append(item)
    dictionary = gensim.corpora.Dictionary(to_dictionary)

    bow_corpus = list()
    for i in range(0, len(df)):
        bow_corpus.append(dictionary.doc2bow(df.iloc[i][0]))

    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=500, id2word=dictionary, passes=2, workers=2)

    # import pdb; pdb.set_trace()
    for idx, topic in lda_model.print_topics(-1):
        print('Topic: {} \nWords: {}'.format(idx, topic))


def processing():
    session = Session()

    adverts = session.query(Advert).filter(Advert.category.isnot(None))
    _to_train = []
    for i in adverts:
        item = json.loads(i.data)
        _to_train.append([' '.join(set(preprocess(f'{item["title"]}. {item["description"]}'))), i.category])

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