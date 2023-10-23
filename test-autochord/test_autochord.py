import modal

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
    # create chords.lab and save the output in it

    chords = test_autochord.remote()
    with open('chords_Hotel_California_autochord.lab', 'w') as f:
        for chord in chords:
            f.write(f'{chord[0]}\t{chord[1]}\t{chord[2]}\n')