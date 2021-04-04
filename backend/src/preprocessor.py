import io
import os
import json
import pickle
import re
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split

from logger import get_logger, get_console_log

work_dir = os.getcwd()
data_dir = os.path.join(work_dir, 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
model_dir = os.path.join(work_dir, 'model')
if not os.path.isdir(model_dir):
    os.makedirs(model_dir)

RAW = os.path.join(data_dir, 'raw.json')
TEXT_LABELS = os.path.join(data_dir, 'text_labels.json')
TOKENIZER = os.path.join(model_dir, 'tokenizer.json')
VECTORS = os.path.join(data_dir, 'wiki-news-300d-1M.vec')
EMBEDDING_MATRIX = os.path.join(data_dir, 'embedding_matrix.pkl')

logger = get_logger('main', 'preprocessor.log')
_ = get_console_log()


def extend_labels(df):
    """
    For a given row, extend the label so its length matches the number
    of tokens in the text column
    """
    text_len = len(df['text'].split(' '))
    return text_len * [df['label']]


def strip_punctuations(s):
    PUNCTUATIONS = "(!|\"|#|\$|%|&|\(|\)|\*|\+|,|-|\.|/|:|;\<|=|>|\?|@|\[|\\\\|\]|\^|_|`|\{|\||\}|~|\t|\n)+"
    s = s.replace(u'\xa0', u'')
    return re.sub("  +", " ", re.sub(PUNCTUATIONS, " ", s)).strip()


def get_text_labels():
    """
    Return a json file to contain all text and labels, where each contains full
    caption from a video, and a list of labels correspond to the length 
    of the caption
    """
    with open(RAW, 'r') as f:
        data = json.loads(f.read())

    all_text = []
    all_labels = []
    for val in data.values():
        df = pd.read_json(val)
        df.text = df.text.apply(strip_punctuations)
        text_ = ' '.join(df.text.to_list())
        all_text.append(text_)

        df['labels'] = df.apply(extend_labels, axis=1)

        labels_ = []
        for l in df.labels.to_list():
            labels_.extend(l)
        all_labels.append(labels_)

    text_labels_dict = {'text': all_text, 'labels': all_labels}

    with open(TEXT_LABELS, 'w') as f:
        json.dump(text_labels_dict, f)


def extend_labels(df):
    """
    For a given row, extend the label so its length matches the number
    of tokens in the text column
    """
    text_len = len(df['text'].split(' '))
    return text_len * [df['label']]


def strip_punctuations(s):
    PUNCTUATIONS = "(!|\"|#|\$|%|&|\(|\)|\*|\+|,|-|\.|/|:|;\<|=|>|\?|@|\[|\\\\|\]|\^|_|`|\{|\||\}|~|\t|\n)+"
    s = s.replace(u'\xa0', u'')
    return re.sub("  +", " ", re.sub(PUNCTUATIONS, " ", s)).strip()


def get_text_labels():
    """
    Return a json file to contain all text and labels, where each contains full
    caption from a video, and a list of labels correspond to the length 
    of the caption
    """
    with open(RAW, 'r') as f:
        data = json.loads(f.read())

    all_text = []
    all_labels = []
    for val in data.values():
        df = pd.read_json(val)
        df.text = df.text.apply(strip_punctuations)
        text_ = ' '.join(df.text.to_list())
        all_text.append(text_)

        df['labels'] = df.apply(extend_labels, axis=1)

        labels_ = []
        for l in df.labels.to_list():
            labels_.extend(l)
        all_labels.append(labels_)

    text_labels_dict = {'text': all_text, 'labels': all_labels}

    with open(TEXT_LABELS, 'w') as f:
        json.dump(text_labels_dict, f)


def gen_tokenizer():
    """Split the data into train & test set, and train tokenizer on train set"""
    with open(TEXT_LABELS, 'r') as f:
        data = json.loads(f.read())

    x_train, x_test, y_train, y_test = train_test_split(
        data['text'], data['labels'], test_size=0.2, random_state=42, shuffle=True)

    tokenizer = Tokenizer(num_words=10000, oov_token="OOV")
    tokenizer.fit_on_texts(x_train)

    with open(TOKENIZER, 'w') as f:
        json.dump(tokenizer.to_json(), f)


def download_vector():
    zipurl = 'https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M.vec.zip'
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(data_dir)

# version found on https://github.com/facebookresearch/fastText/issues/882, uses less RAM


def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = np.array(list(map(float, tokens[1:])))
    return data


def train_embedding():
    MAX_WORDS = 10000
    EMBEDDING_DIM = 300
    embeddings_index = load_vectors(VECTORS)

    with open(TOKENIZER) as f:
        json_obj = json.load(f)
        tokenizer = tokenizer_from_json(json_obj)

    word_index = tokenizer.word_index
    num_words = min(MAX_WORDS, len(word_index) + 1)

    embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))
    for word, i in word_index.items():
        if i >= num_words:
            continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = list(embedding_vector)
    pickle.dump(embedding_matrix, open(EMBEDDING_MATRIX, "wb"))


def main():
    if os.path.isfile(TEXT_LABELS):
        logger.info('Found text & label json file, skip')
    else:
        logger.info('Build text & label json file...')
        get_text_labels()
        logger.info('Done')

    if os.path.isfile(TOKENIZER):
        logger.info('Found tokenizer, skip')
    else:
        logger.info('Build tokenizer...')
        gen_tokenizer()
        logger.info('Done')

    if os.path.isfile(VECTORS):
        logger.info('Found vector file, skip')
    else:
        logger.info('Download vector file...')
        download_vector()
        logger.info('Done')

    if os.path.isfile(EMBEDDING_MATRIX):
        logger.info('Found embedding matrix file, skip...')
    else:
        logger.info('Start building embedding matrix...')
        train_embedding()
        logger.info(f'Done, dump to {EMBEDDING_MATRIX}')
    logger.info('EXIT 0')


if __name__ == '__main__':
    main()
