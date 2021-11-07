import bpy
import collections
from mido import MidiFile
from pprint import pprint


mid = MidiFile('/Users/nithin/python_projects/blender_midi/midi_files/modified_Arabesque_L._66_No._1_in_E_Major.mid')

ticks_per_beat = mid.ticks_per_beat

frames_per_second = 24

# songKeys is a dictionary of "frame_number: notes_list"
songKeys = {}
# songPedals is a dicionary of "frame_number: [control_number, value]"
songPedals = {}

tempo = 0;
for tracks in mid.tracks:
    
    time_in_seconds = 0

    for msg in tracks:   
        
        if msg.dict()['type'] == 'set_tempo':
            tempo = msg.dict()['tempo']   
        ticks_elapsed_from_the_prev_msg = msg.dict()['time']
        time_in_seconds = (1/1000000)*(tempo/ticks_per_beat)*ticks_elapsed_from_the_prev_msg+time_in_seconds
        frame = round(time_in_seconds * frames_per_second)
            
        if msg.dict()['type'] == ('note_on' or 'note_off'):
            note = msg.dict()['note']  
            if ((msg.dict()['velocity'] == 0) or (msg.dict()['type'] == 'note_off')):
                note = -note       
            songKeys[frame] = [note] + songKeys.get(frame, [])
            songKeys[frame].sort()
                     
        if (msg.dict()['type'] == 'control_change'):
            if ((msg.dict()['control'] == 64) or (msg.dict()['control'] == 66) or (msg.dict()['control'] == 67)):
                if (msg.dict()['value'] >= 64):
                    songPedals[frame] = [msg.dict()['control']] + songPedals.get(frame, [])
                elif (msg.dict()['value'] <= 63):
                    songPedals[frame] = [-1 * msg.dict()['control']] + songPedals.get(frame, [])
                songPedals[frame].sort()


def noteAnim(frameOffset, rotationVal, materialVal):   
    bpy.context.scene.frame_set(myFrame + frameOffset)
    bpy.data.objects[str(abs(note))].rotation_euler[0] = rotationVal
    bpy.data.objects[str(abs(note))].select_set(True)
    
    if (bpy.data.objects[str(abs(note))].scale[2] < 0.09):
        bpy.data.materials.get("Glossy White-Red " + str(abs(note))).node_tree.nodes.get("Mix Shader").inputs['Fac'].default_value = materialVal
        bpy.data.objects[str(abs(note))].select_set(True)
        bpy.data.materials.get("Glossy White-Red " + str(abs(note))).node_tree.nodes.get("Mix Shader").inputs['Fac'].keyframe_insert('default_value', frame = myFrame + frameOffset)
    elif (bpy.data.objects[str(abs(note))].scale[2] > 0.09):
        bpy.data.materials.get("Glossy Black-Red " + str(abs(note))).node_tree.nodes.get("Mix Shader").inputs['Fac'].default_value = materialVal
        bpy.data.objects[str(abs(note))].select_set(True)
        bpy.data.materials.get("Glossy Black-Red " + str(abs(note))).node_tree.nodes.get("Mix Shader").inputs['Fac'].keyframe_insert('default_value', frame = myFrame + frameOffset)
    
    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
    bpy.data.objects[str(abs(note))].select_set(False)
        
def pedalAnim(frameOffset, rotationVal, materialVal):
    bpy.context.scene.frame_set(myFrame + frameOffset)
    bpy.data.objects['Pedal ' + str(abs(pedal))].rotation_euler[0] = rotationVal
    bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(True)
    
    bpy.data.materials.get("Metallic Gold + Glossy Red " + str(abs(pedal))).node_tree.nodes.get("Mix Shader").inputs['Fac'].default_value = materialVal
    bpy.data.objects[str(abs(pedal))].select_set(True)
    bpy.data.materials.get("Metallic Gold + Glossy Red " + str(abs(pedal))).node_tree.nodes.get("Mix Shader").inputs['Fac'].keyframe_insert('default_value', frame = myFrame + frameOffset)
        
    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
    bpy.data.objects['Pedal ' + str(abs(pedal))].select_set(False)
    

for myFrame, notes_list in songKeys.items():
    
    for note in notes_list:
        
        if (note > 0):
            bpy.ops.object.select_all(action='DESELECT')
            noteAnim(0, 0, 0)
            noteAnim(5, 0.0349066, 1)      
        else:
            bpy.ops.object.select_all(action='DESELECT')
            noteAnim(0, 0.0349066, 1)
            noteAnim(5, 0, 0)
                     
    positive_notes_list = [abs(val) for val in notes_list]
    repeats = [item for item, count in collections.Counter(positive_notes_list).items() if count > 1]
    for note in repeats:
        bpy.ops.object.select_all(action='DESELECT')
        noteAnim(-5, 0.0349066, 1)
        noteAnim(0, 0, 0)    
        noteAnim(5, 0.0349066, 1)    
      
for myFrame, pedals_list in songPedals.items():

    if (len(pedals_list) > 1):
        if (pedals_list[0] < pedals_list[1]):
            bpy.ops.object.select_all(action='DESELECT')
            pedalAnim(-5, 0, 0)
            pedalAnim(0, -0.174533, 1)
            pedalAnim(5, 0, 0)           
        else:
            bpy.ops.object.select_all(action='DESELECT')
            pedalAnim(-5, -0.174533, 1)
            pedalAnim(0, 0, 0)
            pedalAnim(5, -0.174533, 1);
    else:
        for pedal in pedals_list:
            if (pedal > 0):
                bpy.ops.object.select_all(action='DESELECT')
                pedalAnim(0, 0, 0)
                pedalAnim(5, -0.174533, 1)            
            if (pedal < 0):
                bpy.ops.object.select_all(action='DESELECT')
                pedalAnim(0, -0.174533, 1)
                pedalAnim(5, 0, 0)
                
