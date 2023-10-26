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
    for i, beat_time in enumerate(beat_times):
        start_time = beat_time
        # Find the stop time which is the smallest fraction of a second lesser than the next beat time
        stop_time = beat_times[i + 1] - 0.000001 if i < len(beat_times) - 1 else beat_time  # Subtract a small epsilon to avoid floating-point precision issues
        
        # Find the corresponding bar and beat number
        bar_number = i // 4 + 1  # Assuming 4 beats in a bar
        beat_number = i % 4 + 1
        
        # Find the chord for the current beat
        chord = None
        for chord_start, chord_stop, chord_name in chords:
            if chord_start <= beat_time <= chord_stop:
                chord = chord_name
                break
        
        # Add the synchronized data to the result list
        results.append((start_time, stop_time, f'Bar {bar_number}', f'Beat {beat_number}', chord))
    # print(f'Result: {results}')
    
    with open('chords_Hotel_California_BT_autochord.lab', 'w') as acf:
        for chord in chords:
            acf.write(f'{chord[0]}\t{chord[1]}\t{chord[2]}\n')

    with open('chords_Hotel_California_BT.lab', 'w') as bsf:
        for result in results:
            bsf.write(f'{result[0]}\t{result[1]}\t{result[2]}\t{result[3]}\t{result[4]}\n')