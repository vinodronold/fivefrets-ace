from youtube_dl import YoutubeDL
from madmom.features.chords import CNNChordFeatureProcessor, CRFChordRecognitionProcessor
from madmom.processors import SequentialProcessor
from datetime import datetime


def download(yt_id):

    OUT_EXTENTION = 'wav'
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': OUT_EXTENTION,
        'outtmpl': 'tmp/' + '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': OUT_EXTENTION,
            'preferredquality': '128',
        }]
    }
    ydl = YoutubeDL(ydl_opts)
    with ydl:
        try:
            result = ydl.extract_info(yt_id, download=False)
            # print ('result >>> ', result)
            if (int(round(float(result['duration']))) > 480):
                yt_id = None
            else:
                ydl.download([yt_id])
        except Exception as e:
            print("Can't process yt_id = %s" % yt_id)


def extract(yt_id):
    featproc = CNNChordFeatureProcessor()
    decode = CRFChordRecognitionProcessor()
    chordrec = SequentialProcessor([featproc, decode])
    return chordrec('tmp/' + yt_id + '.wav')


print(str(datetime.now()))
print('*** TESTING ***')
print(str(datetime.now()))
download('IarsrX60bZw')
print('Chord Extract Started : ', str(datetime.now()))
prevDateTime = datetime.now()
print (extract('IarsrX60bZw')[:10])
print('Chord Extract Ended   : ', str(datetime.now()))
