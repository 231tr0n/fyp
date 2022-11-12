import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model

try:
	os.chdir(sys.argv[0].split("/main.py")[0])
except:
	print("failed to change dir")

model = load_model('model.h5')
alphabets = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def model_predict(results, model, alphabets):
	arr = []
	if not results.multi_hand_landmarks:
		return '_'
	else:
		if len(results.multi_hand_landmarks) == 1:
			if results.multi_handedness[0].classification[0].label == 'left':
				for i in results.multi_hand_landmarks[0].landmark:
					arr.append(i.x)
					arr.append(i.y)
					arr.append(i.z)
				for i in range(63):
					arr.append(0)
			else:
				for i in range(63):
					arr.append(0)
				for i in results.multi_hand_landmarks[0].landmark:
					arr.append(i.x)
					arr.append(i.y)
					arr.append(i.z)
		else:
			if not results.multi_handedness[0].classification[0].label == results.multi_handedness[1].classification[0].label:
				if results.multi_handedness[0].classification[0].label == 'left':
					for i in results.multi_hand_landmarks[0].landmark:
						arr.append(i.x)
						arr.append(i.y)
						arr.append(i.z)
					for i in results.multi_hand_landmarks[1].landmark:
						arr.append(i.x)
						arr.append(i.y)
						arr.append(i.z)
				else:
					for i in results.multi_hand_landmarks[1].landmark:
						arr.append(i.x)
						arr.append(i.y)
						arr.append(i.z)
					for i in results.multi_hand_landmarks[0].landmark:
						arr.append(i.x)
						arr.append(i.y)
						arr.append(i.z)
			else:
				return '_'
		arr = np.array(arr)
		y_prob = model.predict(arr.reshape((1, -1)), verbose = 0)
		li = y_prob.tolist()
		res = list(filter(lambda i: i > 0.75, li[0]))
		if len(res) > 0:
				return alphabets[li[0].index(res[0])]
		else:
				return '_'

hands = mp.solutions.hands.Hands(static_image_mode = True, max_num_hands = 2, min_detection_confidence = 0.5)
face = mp.solutions.face_detection.FaceDetection(model_selection = '0', min_detection_confidence = 0.5)

print('Ready')
while True:
	res = str(input())
	file_path = res.strip()
	if (file_path != 'Exit'):
		if os.path.exists(file_path):
			array = []
			image = cv2.flip(cv2.imread(file_path), 1)
			imaged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			face_results = face.process(imaged)
			hands_results = hands.process(imaged)
			if not face_results.detections:
				array.append('Face')
			if not hands_results.multi_handedness:
				array.append('Right Hand')
				array.append('Left Hand')
			else:
				if len(hands_results.multi_handedness) == 1:
					label = hands_results.multi_handedness[0].classification[0].label
					if (label == 'Left'):
						array.append('Left Hand')
					else:
						array.append('Right Hand')
			prediction = model_predict(hands_results, model, alphabets)
			array.append(prediction)
			joined_array = ", ".join(array)
			print(joined_array)
		else:
			joined_array = 'Error'
			print(joined_array)
	else:
		break
