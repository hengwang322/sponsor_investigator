import json

from app import predict_video
from bottle import default_app, request, response, route, run


@route('/predict', method='OPTIONS')
def predict_options():
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
    response.set_header('Access-Control-Allow-Headers',
                        'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token')
    response.status = 200
    return {}


@route('/predict', method='POST')
def predict():
    response.set_header('Access-Control-Allow-Origin', '*')

    body = request.body.read().decode('utf-8')
    vid = json.loads(body).get('vid')
    return predict_video(vid)


app = default_app()

if __name__ == '__main__':
    run(host='127.0.0.1', port=8080)
