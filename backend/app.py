import json
import os
import re
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from youtube_transcript_api import YouTubeTranscriptApi
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.backend as K

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

TOKENIZER = os.path.join('.', 'model', 'tokenizer.json')
MODEL = os.path.join('.', 'model', 'model.h5')
MAX_LEN = 3000
OVERLAP = 800

model = load_model(MODEL, compile=False)
tokenizer = tokenizer_from_json(json.load(open(TOKENIZER)))


def strip_punctuations(s):
    PUNCTUATIONS = "(!|\"|#|\$|%|&|\(|\)|\*|\+|,|-|\.|/|:|;\<|=|>|\?|@|\[|\\\\|\]|\^|_|`|\{|\||\}|~|\t|\n)+"
    s = s.replace(u'\xa0', u'')
    return re.sub("  +", " ", re.sub(PUNCTUATIONS, " ", s)).strip()


def get_transcript(vid):
    langs = ['en', 'en-US', 'en-GB']
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid, languages=langs)
    except Exception as e:
        if type(e).__name__ == 'NoTranscriptFound':
            print('no eng')
        elif type(e).__name__ == 'TranscriptsDisabled':
            print('can\'t find video')
    return transcript


def get_split_index(len_arr, max_len=MAX_LEN, overlap=OVERLAP):
    """
    To split a long list into shorter ones with max_len and an overlap at front
    Returns the index where the list should be split
    """
    if len_arr <= max_len:
        return [[0, len_arr]]
    else:
        splits = [[0, max_len]]
    i = 1
    while True:
        if ((max_len-overlap)*i+max_len) >= len_arr:
            break
        else:
            splits.append([(max_len-overlap)*i, ((max_len-overlap)*i+max_len)])
        i += 1
    splits.append([(max_len-overlap)*i, len_arr])

    return splits


def prepare_X(full_text_list, max_len=MAX_LEN):
    """Split a long text list to shorter ones, transform to padded X array"""
    split_index = get_split_index(len(full_text_list), MAX_LEN, OVERLAP)
    splitted_text_list = [full_text_list[i[0]:i[1]] for i in split_index]
    splitted_text = [' '.join(s) for s in splitted_text_list]

    X = tokenizer.texts_to_sequences(splitted_text)
    X = pad_sequences(X, maxlen=max_len, padding='post')

    return X


def stitch_predictions(predictions, max_len=MAX_LEN, overlap=OVERLAP):
    """stitch raw predictions together, discarding the end of each segment"""
    stitched = []
    for i in range(len(predictions)-1):
        stitched.extend([round(p[1], 3)
                         for p in predictions[i]][:max_len-overlap])
    stitched.extend([round(p[1], 3) for p in predictions[-1]])

    return stitched  # still has padding


def make_predictions(full_text):
    full_text_list = full_text.split(' ')
    X = prepare_X(full_text_list)
    pred_raw = model.predict(X)
    K.clear_session()
    predictions = stitch_predictions(pred_raw)[:len(full_text_list)]

    return predictions


def get_labelled_transcript(transcript):
    text_segments = [strip_punctuations(i['text']) for i in transcript]

    full_text = ' '.join(text_segments)
    predictions = make_predictions(full_text)

    # Put transcript back together with labels
    # split texts to match transcript segments.
    # the last index is not needed since it's just the full len
    segment_index = np.cumsum([len(t.split(' ')) for t in text_segments])[:-1]
    start_list = [round(i['start'], 2) for i in transcript]
    end_list = [round(i['start'] + i['duration'], 2) for i in transcript]

    labels = [list(i) for i in np.split(predictions, segment_index)]
    labelled_transcript = [
        {'text': t, 'label': l, 'start': s, 'end': e}
        for t, l, s, e in zip(text_segments, labels, start_list, end_list)
    ]

    return labelled_transcript


@app.route('/ping', methods=['GET', 'POST'])
@cross_origin()
def get_tasks():
    content = request.json.get("content")
    return jsonify({'response': content})


@app.route('/predict', methods=['GET', 'POST'])
def get_predict():
    vid = request.json.get("vid")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            vid, languages=['en', 'en-US', 'en-GB'])
    except Exception as e:
        if type(e).__name__ == 'NoTranscriptFound':
            return jsonify({'videoId': vid,
                            'error': 'Cannot fetch transcript. Only English is supported. Please try another one.'})
        elif type(e).__name__ == 'TranscriptsDisabled':
            return jsonify({'videoId': vid,
                            'error': "Cannot fetch transcript. It's likely the video and/or its subtitle is disabled. Please try another one."})
        else:
            return jsonify({'videoId': vid,
                            'error': 'Cannot fetch transcript. Please try another one.'})

    labelled_transcript = get_labelled_transcript(transcript)

    return jsonify({'videoId': vid, 'transcript': eval(str(labelled_transcript))})


if __name__ == '__main__':
    app.run(debug=True)
