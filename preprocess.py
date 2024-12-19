import os
import music21 as m21


KERN_DATASET_PATH = "D:\\deutschl\\test"
ACCEPTABLE_DURATIONS = [
    0.25, 
    0.5,
    0.75,
    1.0,
    1.5,
    2,
    3,
    4
]

# kern, MIDI -> m21 -> kern, MIDI (what is m21 used for - conversion among other things)

def load_songs(dataset_path):
    songs = []
    # go through all files in dataset - load with music21

    for path, subdir, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "krn":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

def has_acc_duration(song, acc_duration):
    for note in song.flat.notesAndRests: #filters only notes and rests
        if note.duration.quarterLength not in acc_duration:
            return False
    return True

def transpose(song):
    # get key from song
    parts = song.getElementsByClass(m21.stream.Part)
    measure_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measure_part0[0][4]

    # estimate key using m21
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    print(key)

    # get interval for transposition and transpose
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    transposed_song = song.transpose(interval)

def preprocess(dataset_path):
    pass

    # load the songs
    print("Loading songs...")
    songs = load_songs(dataset_path)
    print(f"Loaded {len(songs)} songs.")

    for song in songs:
    # filter songs that do not have acceptable durations
        if not has_acc_duration(song, ACCEPTABLE_DURATIONS):
            continue
    # transpose songs to C maj/A min

    # encode songs with music time series representation

    # save songs to text file

if __name__ == "__main__":

    songs = load_songs(KERN_DATASET_PATH)
    print(f"Loaded {len(songs)} songs.")
    song = songs[0]

    print(f"Has acceptable duration? {has_acc_duration(song, ACCEPTABLE_DURATIONS)}")

    transposed_song = transpose(song)
    song.show()
    transposed_song.show()

