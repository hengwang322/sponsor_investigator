# Sponsor investigator: backend

## Installation
This backend is tested on Python 3.14. To install dependencies, run:

    pip install -r requirements.txt

If you're running it on a cloud platform, chances are YouTube has blocked the IP addresses. You can supply a proxy via the environmental variables `PROXY_HTTP_URL` or `PROXY_HTTPS_URL` to bypass this. To learn more, refer to [the documentation](https://github.com/jdepoix/youtube-transcript-api#working-around-ip-bans-requestblocked-or-ipblocked-exception) of YouTube Transcript API. 


## Local Deployment
This backend can be deployed locally. The `serve.py` entrypoint uses a `bottle` web framework. To serve directly, run:

    python serve.py

To serve with Gunicorn, run:

    gunicorn --bind 127.0.0.1:8080 serve:app

To invoke locally, run:
    
    curl -XPOST "http://127.0.0.1:8080/predict" -d '{ "vid": "IYSzJmZ6b0U"}'


## AWS Lambda Deployment

To deploy it as a AWS Lambda function via the .zip method, run:

    bash build.sh

This will generate a zip archive, with dependencies bundled under `site-packages` folder. Set `PYTHONPATH` to `/var/task/site-packages` in Lambda to properly use the dependencies.