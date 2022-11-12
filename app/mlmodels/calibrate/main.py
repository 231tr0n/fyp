import os
import sys
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from keras.preprocessing import image

try:
	os.chdir(sys.argv[0].split("/main.py")[0])
except:
	print("failed to change dir")

model = load_model('model.h5')

def model_predict(img_path, model):
	img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128, 3))
	x = tf.keras.preprocessing.image.img_to_array(img)
	x = np.expand_dims(x, axis = 0)
	preds = model.predict(x)
	return preds

def predict_image(path, model):
	classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	y_prob = model_predict(path, model)
	li = y_prob.tolist()
	res = list(filter(lambda i: i > 0.95, li[0]))
	if len(res) > 0:
		return classes[li[0].index(res[0])]
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
				label = hands_results.multi_handedness[0].classification[0].label
				if len(hands_results.multi_handedness) == 1:
					if (label == 'Left'):
						array.append('Left Hand')
					else:
						array.append('Right Hand')
			prediction = predict_image(file_path, model)
			array.append(prediction)
			joined_array = ", ".join(array)
			print(joined_array)
		else:
			joined_array = 'Error'
			print(joined_array)
	else:
		break
