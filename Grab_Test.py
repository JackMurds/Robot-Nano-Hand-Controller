import sys
import json
from os.path import expandvars
from time import sleep

hamsa_dir = expandvars("$HOME/python/src/hamsa/src/hamsa")
gesture_list_dir = expandvars("$HOME/python/src")

sys.path.append(hamsa_dir)
sys.path.append(gesture_list_dir)

from hamsa import poses as Poses
from hamsa import hand as hand

motor_fn = [hand.wiggle_pinky, hand.curl_pinky, hand.wiggle_ring, hand.curl_ring, hand.wiggle_middle, hand.curl_middle, hand.wiggle_index, hand.curl_index, hand.wiggle_thumb, hand.curl_thumb]

finger_list = ["PINKY", "RING", "MIDDLE", "INDEX", "THUMB"]

def Pose_Options(lists):
	gesture_list = lists["poses"]
	misc_list = lists["misc"]
	print(f"Pose options: {gesture_list} \nOther options: {misc_list} \n")

def Control_Finger(i, data):
	print("\nNow controlling", finger_list[i], "finger")
	motor_pos = data[i*2:i*2+2]
	
	if i != 4:
		x_diff = 0.2
		y_diff = 0.05
	else:
		x_diff = -0.05
		y_diff = -0.05
		
	while True:
		pos_change = input("")
		if (pos_change.count('d') > 0) & (pos_change.count('d') == len(pos_change)): #Right
			motor_pos[0] += x_diff * float(pos_change.count('d'))
		elif (pos_change.count('a') > 0) & (pos_change.count('a') == len(pos_change)): #Left
			motor_pos[0] -= x_diff * float(pos_change.count('a'))
		elif (pos_change.count('w') > 0) & (pos_change.count('w') == len(pos_change)): #Up
			motor_pos[1] += y_diff * float(pos_change.count('w'))
		elif (pos_change.count('s') > 0) & (pos_change.count('s') == len(pos_change)): #Down
			motor_pos[1] -= y_diff * float(pos_change.count('s'))
		elif pos_change.lower() == 'save':
			return motor_pos
		elif pos_change.lower() == 'exit':
			return 'exit'
		elif pos_change.lower() == 'q': #Switch to left finger
			return 'q'
		elif pos_change.lower() == 'e': #Switch to right finger
			return 'e'
		
		for j in range(0,2):
			if motor_pos[j] > 1.0:
				motor_pos[j] = 1.0
			elif motor_pos[j] < 0.0:
				motor_pos[j] = 0.0
			
		motor_fn[i*2](motor_pos[0], 0)
		motor_fn[i*2+1](motor_pos[1], 0)
		data[i*2:i*2+2] = motor_pos
		sleep(0.75)
		
def Model_Pose(key):
	for i in range(0, 10):
		motor_fn[i](json_list[key][i], 0)
		sleep(0.1)
		
def Custom_Pose(data):
	named = False
	while named == False:
		new_pose = input("\nInput the name of the new pose \n")
		if (new_pose in data['poses']) and ((new_pose not in data['poses'][:5]) and (new_pose not in data['misc']) and (new_pose != "misc") and (new_pose != "poses")):
			overwrite = input("This pose already exists. Would you like to edit? (y/n)")
			if overwrite == "y":
				named = True
				Model_Pose(new_pose)
		elif (new_pose in data['poses'][:5]) or (new_pose in data['misc']) or (new_pose == "poses") or (new_pose == "misc"):
			print("Cannot overwrite preset!")
		else:
			named = True
			data[new_pose] = [0.6, 1.0, 0.5, 1.0, 0.45, 1.0, 0.5, 1.0, 0.0, 1.0]
	sleep(1)
	print("Input 'SAVE' to store motor position")
	i = 0
	while True:
		output = Control_Finger(i, data[new_pose])
		if output == 'exit':
			del data[new_pose]
			print("\n")
			return
		elif output == 'q':
			i -= 1
			if i < 0:
				i = 4
		elif output == 'e':
			i += 1
			if i > 4:
				i = 0
		elif isinstance(output, list):
			if new_pose not in data['poses']:
				data['poses'].append(new_pose)
			with open(f'{gesture_list_dir}/gesture.json', 'w') as f:
				json.dump(data, f, indent=0)
			print("Saved new pose\n")
			return
	

move_time = 0
delay = 1
startup = True

try:
	Poses.idle(move_time)
	sleep(delay)
	while True:
		with open(f'{gesture_list_dir}/gesture.json', 'r') as f:
			json_list = json.load(f)
		if startup == True:
			Pose_Options(json_list)
			startup = False
		
		hand_pose = input("Enter pose \n")
		if hand_pose == 'fist':
			Poses.fist(move_time)
		elif hand_pose == 'stop':
			Poses.idle(move_time)
		elif hand_pose == 'ok':
			Poses.ok(move_time)
		elif hand_pose == 'two':
			Poses.peace(move_time)
		elif hand_pose == 'one':
			Poses.pan(move_time)
		elif hand_pose == 'help':
			Pose_Options(json_list)
			continue
		elif hand_pose == 'create':
			Custom_Pose(json_list)
		elif hand_pose == 'erase':
			hand_pose = input("\nWhich pose would you like to erase?")
			for _, key in enumerate(json_list):
				if key == hand_pose and ((hand_pose not in json_list['poses'][:5]) and (hand_pose not in json_list['misc']) and (hand_pose != "misc") and (hand_pose != "poses")):
					confirm = input(f"Are you sure you wish to erase {hand_pose}? (y/n)")
					if confirm == "y":
						new_list = json_list
						new_list['poses'].remove(hand_pose)
						del new_list[hand_pose]
						with open(f'{gesture_list_dir}/gesture.json', 'w') as f:
							json.dump(new_list, f, indent=0)
						del new_list
						print(hand_pose, "data has been erased\n")
						break
				elif (hand_pose in json_list['poses'][:5]) or (hand_pose in json_list['misc']) or (hand_pose == "poses") or (hand_pose == "misc"):
					print("Cannot overwrite preset!")
					break
		else:
			for _, key in enumerate(json_list):
				if key == hand_pose:
					Model_Pose(key)
					break
			if hand_pose not in json_list:
				print("Invalid Operation")
			
		sleep(delay)
        
		if hand_pose in json_list['poses']:
			input("\n--Hit ENTER to stop--\n\n")  
			
		Poses.idle(0)
	        
except KeyboardInterrupt:
	Poses.idle(0)

