import bpy
import collections
from mido import MidiFile


mid = MidiFile('/Users/nithin/python_projects/blender_midi/midi_files/modified_Arabesque_L._66_No._1_in_E_Major.mid')

# ticks_per_beat is an attribute of the MidiFile object
ticks_per_beat = mid.ticks_per_beat

# Blender uses 24fps
frames_per_second = 24

# songKeys is a dictionary of "frame_number: [notes_list]"
songKeys = {}
# songPedals is a dicionary of "frame_number: [pedals_list]"
songPedals = {}

# processing tracks (block 8 in diagram)
for tracks in mid.tracks:
    
    time_in_seconds = 0
    tempo = 0

    for msg in tracks:
            
        # reset tempo whenever a new set_tempo message is encountered
        if msg.dict()['type'] == 'set_tempo':
            tempo = msg.dict()['tempo']
        
        # ticks elapsed from previous message is added to find the absolute
        # time in seconds, which is then converted to a frame number (integer)
        ticks_elapsed_from_the_prev_msg = msg.dict()['time']
        time_in_seconds = (1/1000000)*(tempo/ticks_per_beat)*ticks_elapsed_from_the_prev_msg+time_in_seconds
        frame = round(time_in_seconds * frames_per_second)
            
        # if note messages have 0 velocity or are note_off,
        # they are made negative to distinguish from note_on messages
        # note numbers are then appended to [notes_list]
        if msg.dict()['type'] == ('note_on' or 'note_off'):
            note = msg.dict()['note']
                
            if ((msg.dict()['velocity'] == 0) or (msg.dict()['type'] == 'note_off')):
                note = -note
                    
            songKeys[frame] = [note] + songKeys.get(frame, [])
        
        # if control messages are 64, 66, or 67 (all three pedals),
        # they are appended to [pedals_list]
        # like in [notes_list], release messages (with value <= 63) are made negative
        if (msg.dict()['type'] == 'control_change'):
            if ((msg.dict()['control'] == 64) or (msg.dict()['control'] == 66) or (msg.dict()['control'] == 67)):
                if (msg.dict()['value'] >= 64):
                    songPedals[frame] = [msg.dict()['control']] + songPedals.get(frame, [])
                elif (msg.dict()['value'] <= 63):
                    songPedals[frame] = [-1 * msg.dict()['control']] + songPedals.get(frame, [])

# at this point, songKeys and songPedals dictionaries are completed


# building frames (block 9 in diagram) using dictionaries
for frame, notes_list in songKeys.items():
    
    for note in notes_list:
        
        # for note_on messages, two frames are inserted to create the ramp
        # first with 0º rotation and second with 5º rotation
        if (note > 0):
            bpy.ops.object.select_all(action='DESELECT')
            
            bpy.context.scene.frame_set(frame)
            bpy.data.objects[str(note)].rotation_euler[0] = 0
            bpy.data.objects[str(note)].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects[str(note)].select_set(False)
            
            bpy.context.scene.frame_set(frame + 5)
            bpy.data.objects[str(note)].rotation_euler[0] = 0.0349066
            bpy.data.objects[str(note)].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects[str(note)].select_set(False)
        
        # for note_off messages, two frames are inserted to create the ramp
        # first with 5º rotation and second with 0º rotation
        else:
            bpy.ops.object.select_all(action='DESELECT')
            
            
            bpy.context.scene.frame_set(frame)
            bpy.data.objects[str(abs(note))].rotation_euler[0] = 0.0349066
            bpy.data.objects[str(abs(note))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects[str(abs(note))].select_set(False)
            
            bpy.context.scene.frame_set(frame + 5)
            bpy.data.objects[str(abs(note))].rotation_euler[0] = 0
            bpy.data.objects[str(abs(note))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects[str(abs(note))].select_set(False)
    
    # for repeats in [notes_list], only three frames are inserted to create two ramps
    # first with 5º rotation, second with 0º, and third with 5º
    positive_notes_list = [abs(val) for val in notes_list]
    repeats = [item for item, count in collections.Counter(positive_notes_list).items() if count > 1]
    for note in repeats:
      
        bpy.context.scene.frame_set(frame - 5)
        bpy.data.objects[str(abs(note))].rotation_euler[0] = 0.0349066
        bpy.data.objects[str(abs(note))].select_set(True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.data.objects[str(abs(note))].select_set(False)
            
        bpy.context.scene.frame_set(frame)
        bpy.data.objects[str(abs(note))].rotation_euler[0] = 0
        bpy.data.objects[str(abs(note))].select_set(True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.data.objects[str(abs(note))].select_set(False)
            
        bpy.context.scene.frame_set(frame + 5)
        bpy.data.objects[str(abs(note))].rotation_euler[0] = 0.0349066
        bpy.data.objects[str(abs(note))].select_set(True)
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.data.objects[str(abs(note))].select_set(False)
      
for frame, pedals_list in songPedals.items():

    # for repeats in [pedals_list], only three frames are inserted to create two ramps
    if (len(pedals_list) > 1):
        
        # if rotate up is before rotate down:
        # first rotation is 0º, second -2º, and third 0º
        if (pedals_list[0] < pedals_list[1]):
            bpy.context.scene.frame_set(frame - 5)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = 0
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
            
            bpy.context.scene.frame_set(frame)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = -0.174533
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
            
            bpy.context.scene.frame_set(frame + 5)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = 0
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
        
        # if rotate down is before rotate up:
        # first rotation is -2º, second 0º, and third -2º
        else:
            bpy.context.scene.frame_set(frame - 5)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = -0.174533
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
            
            bpy.context.scene.frame_set(frame)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = 0
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
            
            bpy.context.scene.frame_set(frame + 5)
            bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = -0.174533
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
            bpy.ops.anim.keyframe_insert_menu(type='Rotation')
            bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)

    # if [pedals_list] only has one element
    else:

        for pedal in pedals_list:

            # for pedal down messages, two frames are inserted to create the ramp
            # first with 0º rotation and second with -2º rotation
            if (pedal > 0):
                bpy.ops.object.select_all(action='DESELECT')
    
                bpy.context.scene.frame_set(frame)
                bpy.data.objects['Pedal ' + str(pedal)].rotation_euler[0] = 0
                bpy.data.objects['Pedal ' + str(pedal)].select_set(True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.data.objects['Pedal ' + str(pedal)].select_set(False)
            
                bpy.context.scene.frame_set(frame + 5)
                bpy.data.objects['Pedal ' + str(pedal)].rotation_euler[0] = -0.174533
                bpy.data.objects['Pedal ' + str(pedal)].select_set(True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.data.objects['Pedal ' + str(pedal)].select_set(False)
            
            # for pedal up messages, two frames are inserted to create the ramp
            # first with -2º rotation and second with 0º rotation
            if (pedal < 0):
                bpy.ops.object.select_all(action='DESELECT')
            
                bpy.context.scene.frame_set(frame)
                bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = -0.174533
                bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
            
                bpy.context.scene.frame_set(frame + 5)
                bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = 0
                bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)

