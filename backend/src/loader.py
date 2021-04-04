import os
import json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

TOKENIZER = os.path.join('.', 'model', 'tokenizer.json')
MODEL = os.path.join('.', 'model', 'model.h5')
MAX_LEN = 3000
OVERLAP = 800

model = load_model(MODEL, compile=False)
tokenizer = tokenizer_from_json(json.load(open(TOKENIZER)))
