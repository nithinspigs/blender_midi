# Blender MIDI

## Use

preprocess.py creates a modified MIDI file such that tempo messages are located in all tracks. The way that the MIDI file is structured, tempo change messages are often only located in the zeroth track. These messages are crucial to keeping time across tracks, so they are copied from the zeroth track to the remaining ones. This way, the tracks can be processed independently to make the animation.

To generate the animation with key rotations at the correct frame, run the contents of process_and_render_midi.py in the Python script editor of Blender. Ensure that "frames_per_second" matches what is there in Blender. Note the program assumes the key objects to have names from 21 to 108, and pedals named "Pedal 64", "Pedal 66", and "Pedal 67." There are also names for colors and other objects specific to the piano model used in the demonstration, but the naming scheme can be altered according to the Blender piano model used.

## Demonstration

https://youtu.be/WV4ji5mhwzk?si=Ta68r8vHEnrkE9kU
