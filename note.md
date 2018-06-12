sudo apt-get install python3-dev
sudo apt-get install portaudio19-dev
sudo apt-get install ffmpeg



USER GET CHORDS
    IF CHORDS AVAIBALE ?
        YES -> SEND THE CHORDS TO UI
        NO -> CREATE CHORDS (YOUTUBE ID)
                -> API GATEWAY -> LAMBDA -> PY -> YOUTUBE AUDIO EXTRACT
                                                -> CHORDS RECOGNIZE
                                                -> STORE IN DB
                                                -> SEND RESPONSE


sonic-annotator -d vamp:nnls-chroma:chordino:simplechord PiL5UTTTrxk.wav -w csv --csv-force --force
sonic-annotator -d vamp:qm-vamp-plugins:qm-barbeattracker PiL5UTTTrxk.wav -w csv --csv-force --force