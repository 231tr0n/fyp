import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model

try:
	os.chdir(sys.argv[0].split("/main.py")[0])
except:
	print("failed to change dir")

model = load_model('model.h5')
alphabets = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def process_results(results, image):
	def transformation(value, max_value, min_value):
		value -= min_value
		value /= max_value - min_value
		value *= 100
		return int(value) / 100

	def get_coordinates(results, index, img_height, img_width):
		coordinates = []
		if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > index:
			hand_landmarks = results.multi_hand_landmarks[index]
			max_x_value = 1
			min_x_value = 9999
			max_y_value = 1
			min_y_value = 9999
			for pid, landmark in enumerate(hand_landmarks.landmark):
				cx, cy = int(landmark.x * img_width), int(landmark.y * img_height)
				if cx > max_x_value:
					max_x_value = cx
				if cy > max_y_value:
					max_y_value = cy
				if cx < min_x_value:
					min_x_value = cx
				if cy < min_y_value:
					min_y_value = cy
				coordinates.append(cx)
				coordinates.append(cy)
			for i in range(0, len(coordinates), 2):
				coordinates[i] = transformation(coordinates[i], max_x_value, min_x_value)
				coordinates[i + 1] = transformation(coordinates[i + 1], max_y_value, min_y_value)
		else:
			for i in range(42):
				coordinates.append(0)
		return coordinates

	img_height, img_width, _ = image.shape
	hand_coordinates = []
	if results.multi_hand_landmarks:
		if len(results.multi_hand_landmarks) == 2:
			if results.multi_handedness[0].classification[0].label == 'Left':
				hand_coordinates += get_coordinates(results, 0, img_height, img_width)
				hand_coordinates += get_coordinates(results, 1, img_height, img_width)
			else:
				hand_coordinates += get_coordinates(results, 1, img_height, img_width)
				hand_coordinates += get_coordinates(results, 0, img_height, img_width)
		else:
			if results.multi_handedness[0].classification[0].label == 'Left':
				hand_coordinates += get_coordinates(results, 0, img_height, img_width)
				hand_coordinates += get_coordinates(results, 100, img_height, img_width)
			else:
				hand_coordinates += get_coordinates(results, 100, img_height, img_width)
				hand_coordinates += get_coordinates(results, 0, img_height, img_width)
	else:
		hand_coordinates += get_coordinates(results, 100, img_height, img_width)
		hand_coordinates += get_coordinates(results, 100, img_height, img_width)
	return hand_coordinates

def model_predict(results, model, alphabets, image):
	arr = []
	if not results.multi_hand_landmarks:
		return '_'
	else:
		arr = [process_results(results, image)]
		arr = np.array(arr)
		y_prob = model.predict(arr, verbose = 0)
		li = y_prob.tolist()
		res = list(filter(lambda i: i > 0.9, li[0]))
		if len(res) > 0:
				return alphabets[li[0].index(res[0])]
		else:
				return '_'

hands = mp.solutions.hands.Hands(static_image_mode = True, max_num_hands = 2, min_detection_confidence = 0.5, model_complexity = 0)
# face = mp.solutions.face_detection.FaceDetection(model_selection = '0', min_detection_confidence = 0.5)

print('Ready')
while True:
	res = str(input())
	file_path = res.strip()
	if (file_path != 'Exit'):
		if os.path.exists(file_path):
			array = []
			image = cv2.flip(cv2.imread(file_path), 1)
			imaged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			# face_results = face.process(imaged)
			hands_results = hands.process(imaged)
			# if not face_results.detections:
				# array.append('Face')
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
			prediction = model_predict(hands_results, model, alphabets, image)
			array.append(prediction)
			joined_array = ", ".join(array)
			print(joined_array)
		else:
			joined_array = 'Error'
			print(joined_array)
	else:
		break
