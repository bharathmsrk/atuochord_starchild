import modal
import librosa
import os

stub = modal.Stub(
    "import-autochord",
    image=modal.Image.debian_slim()
    .pip_install("autochord"),
)

# stub = modal.Stub("test-autochord")

if stub.is_inside():
    import autochord

@stub.function(mounts=[modal.Mount.from_local_dir(".", remote_path="/root/test_autochord")])
def test_autochord():
    return autochord.recognize('test_autochord/Hotel_California.wav')

chord_mapping = {
    'C:maj': 1, 'C:min': 2,
    'C#:maj': 3, 'C#:min': 4,
    'Db:maj': 3, 'Db:min': 4,
    'D:maj': 5, 'D:min': 6,
    'D#:maj': 7, 'D#:min': 8,
    'Eb:maj': 7, 'Eb:min': 8,
    'E:maj': 9, 'E:min': 10,
    'F:maj': 11, 'F:min': 12,
    'F#:maj': 13, 'F#:min': 14,
    'Gb:maj': 13, 'Gb:min': 14,
    'G:maj': 15, 'G:min': 16,
    'G#:maj': 17, 'G#:min': 18,
    'Ab:maj': 17, 'Ab:min': 18,
    'A:maj': 19, 'A:min': 20,
    'A#:maj': 21, 'A#:min': 22,
    'Bb:maj': 21, 'Bb:min': 22,
    'B:maj': 23, 'B:min': 24
}

@stub.local_entrypoint()
def main():
    # current_directory = os.getcwd()
    # print("Current Working Directory:", current_directory)

    # Find the tempo and beat times in the song
    x, sr = librosa.load('./Hotel_California.wav')
    tempo, beat_times = librosa.beat.beat_track(y=x, sr=sr, start_bpm=60, units='time')
    # print(tempo)
    # print(beat_times)

    # create chords.lab and save the output in it
    chords = test_autochord.remote()
    # print(chords)

    # Iterate through beat_times and chords to synchronize them
    results = []
    # for i, beat_time in enumerate(beat_times):
    #     start_time = beat_time
    #     # Find the stop time which is the smallest fraction of a second lesser than the next beat time
    #     stop_time = beat_times[i + 1] - 0.000001 if i < len(beat_times) - 1 else beat_time  # Subtract a small epsilon to avoid floating-point precision issues
        
    #     # Find the corresponding bar and beat number
    #     bar_number = i // 4 + 1  # Assuming 4 beats in a bar
    #     beat_number = i % 4 + 1
        
    #     # Find the chord for the current beat
    #     chord = None
    #     for chord_start, chord_stop, chord_name in chords:
    #         if chord_start <= beat_time <= chord_stop:
    #             chord = chord_name
    #             break
        
    #     # Add the synchronized data to the result list
    #     results.append((start_time, stop_time, f'Bar {bar_number}', f'Beat {beat_number}', chord))
    # print(f'Result: {results}')

    # Iterate through beat_times and chords to synchronize them based on quarter notes (4 parts in a beat)
    for i, beat_time in enumerate(beat_times):
        # Split each beat into 4 parts (quarter notes)
        for j in range(4):
            # Calculate start and stop times for the quarter note
            start_time = beat_time + (j * (1 / 4) * (beat_times[i + 1] - beat_time)) if i < len(beat_times) - 1 else beat_time  # Calculate quarter note start time
            stop_time = start_time + (1 / 4) * (beat_times[i + 1] - beat_time) if i < len(beat_times) - 1 else beat_time  # Calculate quarter note stop time
            
            # Find the corresponding bar, beat, and quarter note number
            bar_number = i // 4 + 1  # Assuming 4 beats in a bar
            beat_number = (i % 4) + 1  # Beat number within the bar
            quarter_note_number = j + 1  # Quarter note number
            
            # Find the chord for the current quarter note
            chord = None
            for chord_start, chord_stop, chord_name in chords:
                if chord_start <= start_time <= chord_stop:
                    chord = chord_name
                    break

            chord = None
            for chord_start, chord_stop, chord_name in chords:
                if chord_start <= beat_time <= chord_stop:
                    chord = chord_mapping.get(chord_name, 0)  # Map chord to integer, default to 0 if not found
                    break
            
            # Add the synchronized data to the result list
            results.append((start_time, stop_time, f'Bar {bar_number}', f'Beat {beat_number}', f'Quarter {quarter_note_number}', chord))
    
    with open('chords_Hotel_California_BT_autochord.lab', 'w') as acf:
        for chord in chords:
            acf.write(f'{chord[0]}\t{chord[1]}\t{chord[2]}\n')

    with open('chords_Hotel_California_BT.lab', 'w') as bsf:
        for result in results:
            bsf.write(f'{result[0]}\t{result[1]}\t{result[2]}\t{result[3]}\t{result[4]}\t{result[5]}\n')