import json
import os
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi as yti
from logger import get_logger, get_console_log

work_dir = os.getcwd()
data_dir = os.path.join(work_dir, 'data')
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
TIMESTAMPS = os.path.join(data_dir, 'id_timestamp.json')
RAW_DATA = os.path.join(data_dir, 'raw.json')
CHECKPOINT = os.path.join(data_dir, 'checkpoint')
MAX_RETRIES = 10

logger = get_logger('main', 'scraper.log')
_ = get_console_log()


def get_timestamps():
    """Read the database & dump video id & timestamps to a json file"""
    if os.path.isfile(TIMESTAMPS):
        logger.info('Timestamp data found, skip')
    else:
        logger.info('Getting database dump...')
        raw = pd.read_csv('https://sponsor.ajay.app/database/sponsorTimes.csv')
        logger.info('Done')
        df = raw[(raw.votes >= 10) & (raw.shadowHidden == 0)
                 ][['videoID',  'startTime', 'endTime']]
        df['time'] = df.apply(lambda x: f'{x.startTime},{x.endTime}', axis=1)

        df_ts = (df
                 .groupby(['videoID'])['time']
                 .apply(';'.join)
                 .apply(lambda s: [[float(y) for y in x] for x in [i.split(',') for i in s.split(';')]])
                 .reset_index())
        with open(TIMESTAMPS, 'w') as f:
            json.dump(df_ts.to_json(), f)
        logger.info(f'Timestamp info dumped to {TIMESTAMPS}')


def get_transcripts():
    with open(TIMESTAMPS, 'r') as f:
        json_str = json.loads(f.read())
        df_ts = pd.read_json(json_str)
    if os.path.isfile(RAW_DATA):
        with open(RAW_DATA, 'r') as f:
            raw = json.loads(f.read())
    else:
        raw = dict()

    if os.path.isfile(CHECKPOINT):
        logger.info('Resume scraping from last check point.')
        with open(CHECKPOINT, 'r') as f:
            i = int(f.read())
    else:
        logger.info('Start transcript scraping')
        i = 0
    retries = 0
    while True:
        i += 1
        if retries >= 10:
            # most possibly hitting YouTube Transcript API's limit
            logger.info('Reached retry limit. Stopping...')
            break

        vid = df_ts.videoID[i]
        ts_ranges = df_ts.time[i]

        if vid in raw.keys():
            continue
        elif i == df_ts.index[-1]:
            logger.info('No more video to scrape. Stopping...')
            break
        else:
            try:
                cap = pd.DataFrame(yti.get_transcript(
                    vid, languages=['en', 'en-US', 'en-GB']))
                retries = 0
                logger.debug(f'Scraped video id {vid}')
            except:
                retries += 1
                logger.debug(f'Cannot scrape video id {vid}')
                continue

            cap['end'] = cap['start'] + cap['duration']
            cap['label'] = 0
            cap.drop(['duration'], axis=1, inplace=True)

            for ts in eval(str(ts_ranges)):
                mask = (cap.start >= ts[0]) & (cap.end <= ts[1])
                cap.loc[mask, 'label'] = 1

            raw[vid] = cap.to_json()

    logger.info('Dumping data...')
    with open(RAW_DATA, 'w') as f:
        json.dump(raw, f)
    with open(CHECKPOINT, 'w') as f:
        f.write(str(i-MAX_RETRIES))
    logger.info(f'Done. Raw data has {len(raw)} lines')
    logger.info('EXIT 0')


def main():
    get_timestamps()
    get_transcripts()


if __name__ == '__main__':
    main()
