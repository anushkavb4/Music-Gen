import json
import numpy as np
from tensorflow import keras
from preprocess import SEQUENCE_LENGTH, MAPPING_PATH
import music21 as m21

class MelodyGen:

    def __init__(self, model_path = "model.h5"):

        self.model_path = model_path
        self.model = keras.models.load_model(model_path)

        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH

    def generate_melody(self, seed, num_steps, max_seq_len, temp):

        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed

        seed = [self._mappings[symbol] for symbol in seed]

        for _ in range(num_steps):
            seed = seed[-max_seq_len:]

             # one hot encode the seed
            onehot_seed = keras.utils.to_categorical(seed, num_classes = len(self._mappings))
            onehot_seed = onehot_seed[np.newaxis, ...]

            # make prediction
            probab = self.model.predict(onehot_seed)[0]
            output_int = self._sample_with_temperature(probab, temp)

            seed.append(output_int)

            output_symb = [k for k, v in self._mappings.items() if v == output_int][0]

            # check if we're at the end of the melody
            if output_symb == "/":
                break

            melody.append(output_symb)

        return melody


    def _sample_with_temperature(self, probabilities, temperature):
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))
        
        choices = range(len(probabilities))
        index = np.random.choice(choices, p= probabilities)

        return index
    
    def save_melody(self, melody, step_duration = 0.25, format = "midi", file_name = "mel.midi"):
        stream = m21.stream.Stream()

        start_symb = None
        step_counter = 1

        for i, symbol in enumerate(melody):
            if symbol != "_" or i + 1 == len(melody):
                
                if start_symb is not None:
                    quarter_dura = step_duration * step_counter

                    if start_symb == "r":
                        m21_event = m21.note.Rest(quarterLength = quarter_dura)
                    else:
                        m21_event = m21.note.Note(int(start_symb), quarterLength = quarter_dura)
                    
                    stream.append(m21_event)
                    step_counter = 1

                start_symb = symbol

            else:
                step_counter += 1
        
        stream.write(format, file_name)


if __name__ == "__main__":
    mg = MelodyGen()
    seed = "55 _ _ _ 60 _ _ _ 55 _ _ _ 55 _ "
    melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, 0.7)
    print(melody)
    mg.save_melody(melody)