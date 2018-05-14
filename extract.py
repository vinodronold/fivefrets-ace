from datetime import datetime
from sys import argv
import json
import os

OUT_FILE_PATH = 'tmp/'
OUT_DUMP_PATH = 'out/'
OUT_FILE_EXT = 'wav'
MAX_SONG_DURATION = 480
#   Ids 0-11 encode major chords starting with root 'A', 12-23 minor chords.
#   Id 24 represents 'N', the no-chord class.
CHORD_LBL_ID = {"A:min": 0,
                "A#:min": 1,
                "B:min": 2,
                "C:min": 3,
                "C#:min": 4,
                "D:min": 5,
                "D#:min": 6,
                "E:min": 7,
                "F:min": 8,
                "F#:min": 9,
                "G:min": 10,
                "G#:min": 11,
                "A:maj": 12,
                "A#:maj": 13,
                "B:maj": 14,
                "C:maj": 15,
                "C#:maj": 16,
                "D:maj": 17,
                "D#:maj": 18,
                "E:maj": 19,
                "F:maj": 20,
                "F#:maj": 21,
                "G:maj": 22,
                "G#:maj": 23,
                "N": 24}


def download(youtube_id):
    from youtube_dl import YoutubeDL
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': OUT_FILE_EXT,
        'outtmpl': OUT_FILE_PATH + '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': OUT_FILE_EXT,
            'preferredquality': '192',
        }]
    }
    ydl = YoutubeDL(ydl_opts)
    with ydl:
        try:
            result = ydl.extract_info(youtube_id, download=False)
            duration = int(round(float(result['duration'])))
            if (duration > MAX_SONG_DURATION):
                raise ValueError(
                    'Cannot Extract Chords: Duration more than {MAX_SONG_DURATION}')
            else:
                ydl.download([youtube_id])
                return result['title']

        except Exception as e:
            print("Can't process yt_id = %s" % youtube_id)
            print(e)


def get_beat_processor():
    print('START BEAT PROCESSOR   >> ', str(datetime.now()))
    from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
    from madmom.processors import SequentialProcessor
    print('BEAT PROCESSOR         >> ', str(datetime.now()))
    return SequentialProcessor(
        [RNNBeatProcessor(), DBNBeatTrackingProcessor(fps=100)])


def get_chords_processor():
    print('START CHORDS PROCESSOR >> ', str(datetime.now()))
    from madmom.features.chords import CNNChordFeatureProcessor, CRFChordRecognitionProcessor
    from madmom.processors import SequentialProcessor
    print('CHORDS PROCESSOR       >> ', str(datetime.now()))
    return SequentialProcessor(
        [CNNChordFeatureProcessor(), CRFChordRecognitionProcessor()])


def process_beats_and_chords(youtube_id):
    print('START PROCESS          >> ', str(datetime.now()))
    from madmom.processors import ParallelProcessor
    processMulti = ParallelProcessor([], num_threads=2)
    processMulti.append(get_beat_processor())
    processMulti.append(get_chords_processor())
    print('BEAT PROCESS           >> ', str(datetime.now()))
    return processMulti.process(OUT_FILE_PATH + youtube_id + '.' + OUT_FILE_EXT)


def sync_beats_and_chords(beats_and_chords):
    print('START SYNCING          >> ', str(datetime.now()))
    return [
        {b: CHORD_LBL_ID[c]}
        for b in beats_and_chords[0]
        for (start, end, c) in beats_and_chords[1]
        if (b >= start and b < end)
    ]


### MAIN ###

try:
    IN_YOUTUBE_ID = argv[1]
except Exception as e:
    print('Provide Youtube ID')
    raise

if IN_YOUTUBE_ID:
    print('IN_YOUTUBE_ID          >> ', IN_YOUTUBE_ID)
    print('STARTING EXTRACT       >> ', str(datetime.now()))
    song_title = download(IN_YOUTUBE_ID)
    print('END DOWNLOAD           >> ', str(datetime.now()))
    print('START BEAT SYNC CHORD  >> ', str(datetime.now()))
    beat_synced_chords = sync_beats_and_chords(
        process_beats_and_chords(IN_YOUTUBE_ID))
    print('END BEAT SYNC CHORD    >> ', str(datetime.now()))
    print('END EXTRACT            >> ', str(datetime.now()))
    OUT_DATA = {
        'youtube_id': IN_YOUTUBE_ID,
        'title': song_title,
        'chords': beat_synced_chords
    }
    OUT_FILE = OUT_DUMP_PATH + IN_YOUTUBE_ID + '.json'
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, 'w') as outfile:
        json.dump(OUT_DATA, outfile)

else:
    raise ValueError('Youtube ID is blank')

print(OUT_DATA)
