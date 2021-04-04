# Sponsor investigator: backend

## Scrape the data

To get raw, labelled data, run the following script in the backend directory:

    python ./src/scraper.py

This will get the database dump from the [SponsorBlock](https://sponsor.ajay.app) project
to get the sponsor timestamp, and use the `youtube_transcript_api` package to scrape the transcript
of each video. The output will be a json file that contains the raw text file & timestamp.

Note you will likely to run into rate limit at some point when scraping the transcripts. The python script will stop
after 10 consecutive failed attempts and write a `checkpoint` file. You can resume scraping after waiting for
some time and/or change your ip.

## Preprocess the data

To clean the transcript and prepare tokenizer and the embedding layer, run the following script in the backend directory:

    python ./src/preprocessor.py

Note in this step the script will download and unzip the pre-trained word vectors file from fastText, which will occupy ~2.1 GB of local storage.

## Train the model

To start training, run the following script in the backend directory:

    python ./src/trainer.py

## Deployment

This backend is meant for used as a AWS Lambda function. To start, build a docker image based on the Lambda base Python image,
run the following script in the backend directory:

    docker build -t sponsor-backend .

Then you can run the image locally via:

    docker run -p 9000:8080 sponsor-backend:latest

And the lambda function can be invoked locally like this:

    curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{ "vid": "IYSzJmZ6b0U"}'
