import os
import json
import music21 as m21
from tensorflow import keras
import numpy as np

KERN_DATASET_PATH = "D:\\deutschl\\erk"
SAVE_DIR = "dataset"
SINGLE_FILE_DATASET = "file_dataset"
MAPPING_PATH = "mapping.json"
SEQUENCE_LENGTH = 64
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

    # get interval for transposition and transpose
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    transposed_song = song.transpose(interval)
    return transposed_song

def encode_song(song, time_step = 0.25):

    encoded_song = []
    for event in song.flat.notesAndRests:
        # might have to replace flat with flatten
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi #60
        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        # convert note/rest into time seies notation
        steps = int(event.duration.quarterLength/time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song

def preprocess(dataset_path):
    pass

    # load the songs
    print("Loading songs...")
    songs = load_songs(dataset_path)
    print(f"Loaded {len(songs)} songs.")

    for i, song in enumerate(songs):
    # filter songs that do not have acceptable durations
        if not has_acc_duration(song, ACCEPTABLE_DURATIONS):
            continue
    # transpose songs to C maj/A min
        song = transpose(song)

    # encode songs with music time series representation
        encoded_song = encode_song(song)
    # save songs to text file
        save_path = os.path.join(SAVE_DIR, str(i))
        with open(save_path, "w") as fp:
           fp.write(encoded_song) 
        return song

def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song


def create_single(dataset_path, file_dataset_path, sequence_length):
    new_song_delimeter = "/ " * sequence_length
    songs = ""

    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs = songs + song + " " + new_song_delimeter

    songs = songs[:-1]
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)
    return songs

def create_mapping(songs, mapping_path):
    mappings = {}
    # storing all the symbols (in some sense) - cutting repeeated ones
    songs = songs.split()
    vocabulary = list(set(songs))

    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i
    
    with open(mapping_path, "w") as fp:
        json.dump(mappings, fp, indent = 4)

def convert_songs(songs):
    int_songs = []

    # load mappings 
    with open(MAPPING_PATH, "r") as fp:
        mappings = json.load(fp)
        
    # strings to list
    songs = songs.split()

    # map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])

    return int_songs

def generating_training_seq(sequence_length):
    
    songs = load(SINGLE_FILE_DATASET)
    int_songs = convert_songs(songs)

    inputs =[]
    targets = []
    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])

    vocab_size = len(set(int_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes = vocab_size)
    targets = np.array(targets)

    return inputs, targets

def main():
    preprocess(KERN_DATASET_PATH)
    songs = create_single(SAVE_DIR, SINGLE_FILE_DATASET, SEQUENCE_LENGTH)
    create_mapping(songs, MAPPING_PATH)
    inputs, targets= generating_training_seq(SEQUENCE_LENGTH)
    a = 1

if __name__ == "__main__":
    main()
