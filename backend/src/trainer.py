import pickle
import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding, SpatialDropout1D, TimeDistributed, Bidirectional
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import optimizers
from tensorflow.keras.initializers import Constant
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ReduceLROnPlateau
from logger import get_logger, get_console_log

work_dir = os.getcwd()
data_dir = os.path.join(work_dir, 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
model_dir = os.path.join(work_dir, 'model')
if not os.path.isdir(model_dir):
    os.makedirs(model_dir)

TEXT_LABELS = os.path.join(data_dir, 'text_labels.json')
EMBEDDING_MATRIX = os.path.join(data_dir, 'embedding_matrix.pkl')
TOKENIZER = os.path.join(model_dir, 'tokenizer.json')
MODEL_FILE = os.path.join(model_dir, 'model.h5')

MAX_LEN = 3000
OVERLAP = 800

logger = get_logger('main', 'trainer.log')
_ = get_console_log()


def get_split_index(len_arr, max_len, overlap):
    if len_arr <= max_len:
        return [[0, len_arr]]
    else:
        splits = [[0, max_len]]
        i = 1
        while True:
            if ((max_len-overlap)*i+max_len) >= len_arr:
                break
            else:
                splits.append(
                    [(max_len-overlap)*i, ((max_len-overlap)*i+max_len)])
            i += 1
        splits.append([(max_len-overlap)*i, len_arr])

        return splits


def reshape_data(x, y, max_len, overlap):
    """Splice x and y sequences into chunks of max_len
    with overlap. Return padded array.
    """

    x_shaped = []
    y_shaped = []

    for i in range(len(x)):
        if len(x) != len(y):
            continue
        elif len(x) < 5:
            continue
        else:
            x_arr = x[i]
            y_arr = y[i]
            len_arr = len(x_arr)

            splits = get_split_index(len_arr, max_len, overlap)
            split_x = [np.array(x_arr[split[0]:split[1]],
                                dtype='float64') for split in splits]
            split_y = [np.array(y_arr[split[0]:split[1]],
                                dtype='float64') for split in splits]
            x_shaped.extend(split_x)
            y_shaped.extend(split_y)

    x_shaped = pad_sequences(x_shaped, padding="post", maxlen=max_len)
    y_shaped = pad_sequences(y_shaped, padding="post", maxlen=max_len)

    return x_shaped, y_shaped


def prepare_data():
    with open(TEXT_LABELS, 'r') as f:
        data = pd.DataFrame(json.loads(f.read()))
    with open(TOKENIZER) as f:
        json_obj = json.load(f)
        tokenizer = tokenizer_from_json(json_obj)

    tokenized_x = tokenizer.texts_to_sequences(data.text.values)
    x_train, x_test, y_train, y_test = train_test_split(
        tokenized_x,
        data.labels.values,
        test_size=0.2,
        random_state=42,
        shuffle=True)

    x_train, y_train = reshape_data(
        x_train, y_train, max_len=MAX_LEN, overlap=OVERLAP)

    x_test, y_test = reshape_data(
        x_test, y_test, max_len=MAX_LEN, overlap=OVERLAP)

    return x_train, x_test, y_train, y_test


def build_model():
    embedding_matrix = pickle.load(open(EMBEDDING_MATRIX, "rb"))
    embedding = Embedding(input_dim=10000,
                          output_dim=300,
                          embeddings_initializer=Constant(embedding_matrix),
                          input_length=MAX_LEN,
                          mask_zero=True,
                          trainable=False)

    model = Sequential()
    model.add(embedding)
    model.add(SpatialDropout1D(0.30))
    model.add(Bidirectional(LSTM(128,
                                 dropout=0.2,
                                 return_sequences=True,
                                 recurrent_dropout=0,
                                 activation='tanh',
                                 recurrent_activation='sigmoid')))
    model.add(TimeDistributed(Dense(2, activation="softmax")))

    return model


def main():
    logger.info('Prepare data...')
    x_train, x_test, y_train, y_test = prepare_data()
    weight = (y_train.shape[0] * y_train.shape[1]) / y_train.sum()
    train_weight_sample = y_train * weight + 1
    test_weight_sample = y_test * weight + 1
    y_train = to_categorical(y_train, 2)
    y_test = to_categorical(y_test, 2)
    logger.info('Done')

    logger.info('Start training model')
    model = build_model()
    adam = optimizers.Adam(learning_rate=5e-5)
    model.compile(loss="binary_crossentropy",
                  optimizer=adam,
                  metrics=["accuracy"],
                  sample_weight_mode="temporal")
    reduce_lr = ReduceLROnPlateau(monitor='val_loss',
                                  factor=0.2,
                                  patience=3,
                                  min_lr=1e-8,
                                  verbose=1)
    history = model.fit(x_train,
                        y_train,
                        validation_split=0.1,
                        epochs=25,
                        sample_weight=train_weight_sample,
                        batch_size=32,
                        verbose=1,
                        callbacks=[reduce_lr])
    test_loss, test_accuracy = model.evaluate(
        x_test,
        y_test,
        batch_size=32,
        sample_weight=test_weight_sample)
    val_accuracy = history.history['val_accuracy'][-1]
    val_loss = history.history['val_loss'][-1]
    logger.info('Training finished')
    logger.info(f'Val loss:{val_loss:.4f}, accuracy:{val_accuracy:.4f}')
    logger.info(f'Test loss:{test_loss:.4f}, accuracy:{test_accuracy:.4f}')

    model.save(MODEL_FILE)
    logger.info(f'Dump model to {MODEL_FILE}')


if __name__ == '__main__':
    main()
