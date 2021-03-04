import mido
from pprint import pprint
import sys
#mid = MidiFile('./mary_had_a_little_lamb.mid')
mid = mido.MidiFile('./Arabesque_L._66_No._1_in_E_Major.mid') # Block: 0 (Read MIDI File)

#
# We will create a modified midifile. Tracks > 0 will be modified. So create a new midifile and start with the original Track 0
#

modified_mid = mido.MidiFile()
modified_mid.tracks.append(mid.tracks[0])

ticks_per_beat = mid.ticks_per_beat                         # Block 0: Find the ticks_per_beat
print ("Ticks Per Beat:{}\n".format(ticks_per_beat))
frames_per_second = 24

# song is a dictionary of "frame_number: notes_list"
song = {}
# tempo_ticks_and_messages is a list [(total_actual_ticks, tempo_msg), (..,..) ...]   
# ticks_and_messages is a list of [(total_actual_ticks, any_msg), (.. , ..) ...]
# track_ticks_and_messages is a dictionary of "track_number => ticks_and_messages"
#   1.  Extract the 'set_tempo' messages from Track 0
#   2.  'Merge' them with the messages for other tracks... in the order of the ticks 
#   3.  'Adjust' the 'time' value on the set_tempo message so that
#
#           TOTAL_TICKS_AT_THAT_SET_TEMPO_MESSAGE - TOTAL_TICKS_AT_THE_PREVIOUS_TRACK_MESSAGE = 'time' value    <<<<<<< tempo message
#           TOTAL_TICKS_AT_THE_NEXT_TRACK_MESSAGE - TOTAL_TICKS_AT_THAT_SET_TEMPO_MESSAGE = 'time' value    <<<<<<< next track message

#  actual_total_ticks  message

#(8800, <message note_on channel=0 note=73 velocity=92 time=9>),
#(8800, <meta message set_tempo tempo=517242 time=40>),   <<<<<<< set_tempo message added from track 0

#(8800, <meta message set_tempo tempo=517242 time=0>),    <<<<<<< time = '8800 - 8800'


#
#   3.  Write out a new midi file
track_ticks_and_messages = {}
tempo_ticks_and_messages = []

print ("Number of Tracks : {}\n".format(len(mid.tracks)))
for track_number, messages in enumerate(mid.tracks):
  total_actual_ticks, ticks_and_messages = 0, []
  for msg in messages:
    ticks_to_wait_from_the_prev_message = msg.dict()['time']
    total_actual_ticks = ticks_to_wait_from_the_prev_message  + total_actual_ticks
    ticks_and_messages.append((total_actual_ticks, msg))
    if track_number == 0 and msg.dict()['type'] == 'set_tempo':       # Block 4 (Process Track 0) Capture the Tempo Messages
      tempo_ticks_and_messages.append((total_actual_ticks, msg))      # Block 4 (Process Track 0) Build a map of {total_ticks : message}

  if (track_number == 0):
    print ("Collecting tempo messages from the Track# : {}".format(track_number))
    print ("Total Number of Tempo Changes in Track#0 : {}\n".format(len(tempo_ticks_and_messages)))
  else:   # Block 5 (Update Tracks > 0)
    print ("Initial number of messages in Track# {} : {}".format(track_number, len(messages)))
    print ("Inserting Tempo Messages into Track Number : {}".format(track_number))
    for total_actual_tempo_ticks, tempo_msg in tempo_ticks_and_messages:    # Block 5 (loop through tempo messages found from track 0)
      for i in range(len(ticks_and_messages)-1):
        i_ticks, i_msg = ticks_and_messages[i]
        i_plus_1_ticks, i_plus_1_msg = ticks_and_messages[i+1]
        if total_actual_tempo_ticks == i_ticks:     # Block 5 (Insert the tempo message)
          new_msg = mido.MetaMessage('set_tempo', tempo = tempo_msg.dict()['tempo'], time=0)
          ticks_and_messages.insert(i,(total_actual_tempo_ticks, new_msg))
          break
        elif total_actual_tempo_ticks > i_ticks and total_actual_tempo_ticks < i_plus_1_ticks:  # Block 5 (Insert the tempo message and modify the next

          ticks_and_messages.remove(ticks_and_messages[i+1])  # Block 5 (Insert the tempo message and modify the 'time_to_wait' for the next message)

          new_time_1 = total_actual_tempo_ticks - i_ticks   # Block 5 (We need to keep the overall time to not change)
          new_msg_1 = mido.MetaMessage('set_tempo', tempo = tempo_msg.dict()['tempo'], time=new_time_1)

          new_time_2 = i_plus_1_ticks - total_actual_tempo_ticks
          new_msg_2_data = i_plus_1_msg.dict()
          new_msg_2_data['time'] = new_time_2
          new_msg_2 = mido.Message.from_dict(new_msg_2_data)

          ticks_and_messages.insert(i+1,(total_actual_tempo_ticks, new_msg_1))
          ticks_and_messages.insert(i+2,(i_plus_1_ticks, new_msg_2))
          break

    modified_track = mido.MidiTrack()
    for ticks, msg in ticks_and_messages:
      modified_track.append(msg)
    modified_mid.tracks.append(modified_track)
    print ("Final number of messages in Track# {} : {}\n".format(track_number, len(modified_track)))  # Confirm no loss of messages

modified_mid.save('modified_Arabesque_L._66_No._1_in_E_Major.mid')  # Block 6 (Save the modified MIDI file for use by Blender)


print ("Length of the original midi file : {}".format(mid.length))      # Confirmation. Quality check
print ("Length of the modified midi file : {}\n".format(modified_mid.length)) # Confirmation. Quality check



