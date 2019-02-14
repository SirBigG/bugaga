import json

import pandas as pd
import gensim

from db import Session

from models.parser import Advert


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(token)
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
