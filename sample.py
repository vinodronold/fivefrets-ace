from youtube_dl import YoutubeDL
from madmom.features.chords import CNNChordFeatureProcessor, CRFChordRecognitionProcessor
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
from madmom.processors import SequentialProcessor, ParallelProcessor
from datetime import datetime
from subprocess import check_call
from pydub import AudioSegment
from math import ceil


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
            'preferredquality': '192',
        }]
    }
    ydl = YoutubeDL(ydl_opts)
    with ydl:
        try:
            result = ydl.extract_info(yt_id, download=False)
            duration = int(round(float(result['duration'])))
            print('dur: ', duration)
            if (duration > 480):
                yt_id = None
            else:
                ydl.download([yt_id])
                split(yt_id, duration)
        except Exception as e:
            print("Can't process yt_id = %s" % yt_id)
            print(e)


def split(yt_id, dur):
    fiveParts = int(ceil((dur / 10) * 1000))
    print('fiveParts: ', fiveParts)
    audio_file = AudioSegment.from_file('tmp/' + yt_id + '.wav', format="wav")
    for i, chunk in enumerate(audio_file[::fiveParts]):
        with open('tmp/' + yt_id + "-%s.wav" % i, "wb") as f:
            chunk.export(f, format="wav")


def arrange(beatAndChords):
    print('*** ARRANGING ***')
    beats = beatAndChords[0]
    chords = beatAndChords[1]
    print('beats', beats[:5])
    print('chords', chords[:5])
    # LIST comprehension
    return [(b, c) for b in beats for (start, end, c) in chords if (b >= start and b < end)]


def extract(yt_id):
    beats = SequentialProcessor(
        [RNNBeatProcessor(), DBNBeatTrackingProcessor(fps=100)])
    chordrec = SequentialProcessor(
        [CNNChordFeatureProcessor(), CRFChordRecognitionProcessor()])
    processMulti = ParallelProcessor([])
    processMulti.append(beats)
    processMulti.append(chordrec)
    beatSync = SequentialProcessor([processMulti, arrange])
    return beatSync('tmp/' + yt_id + '-0.wav')
    # return ParallelProcessor([chordrec('tmp/' + yt_id + '-0.wav'),
    #                           chordrec('tmp/' + yt_id + '-1.wav'),
    #                           chordrec('tmp/' + yt_id + '-2.wav'),
    #                           chordrec('tmp/' + yt_id + '-3.wav'),
    #                           chordrec('tmp/' + yt_id + '-4.wav'),
    #                           chordrec('tmp/' + yt_id + '-5.wav'),
    #                           chordrec('tmp/' + yt_id + '-6.wav'),
    #                           chordrec('tmp/' + yt_id + '-7.wav'),
    #                           chordrec('tmp/' + yt_id + '-8.wav'),
    #                           chordrec('tmp/' + yt_id + '-9.wav')], num_threads=2)

    # CNNChordRecognition -v single tmp/IarsrX60bZw.wav -o ~/p/fivefrets-ace/tmp/chords.txt -j 2
    # result = check_call([
    #     'CNNChordRecognition',
    #     'single',
    #     'tmp/IarsrX60bZw.wav',
    #     '-o', 'tmp/chords.txt'
    # ])
    # return result


print(str(datetime.now()))
print('*** TESTING ***')
print(str(datetime.now()))
download('IarsrX60bZw')
# tmp_file = open('tmp\chords_CNN.txt', 'w')
print('Chord Extract Started : ', str(datetime.now()))
# prevDateTime = datetime.now()
print(extract('IarsrX60bZw'))
# extracted_Chords = extract('IarsrX60bZw')
print('Chord Extract Ended   : ', str(datetime.now()))
# print(extracted_Chords)
# tmp_file.close()
