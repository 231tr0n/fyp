import numpy as np
import pandas as pd
import mediapipe as mp
import os
import cv2
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import load_model

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

alphabets = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def preprocess(pathname):
	with mp_hands.Hands(
		static_image_mode=True,
		max_num_hands=1,
		min_detection_confidence=0.3) as hands:

		image = cv2.flip(cv2.imread(pathname), 1)
		result = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

		landmark_vertices_xyz = []

		if not result.multi_hand_landmarks:
			return np.zeros(63)

		for l in result.multi_hand_landmarks[0].landmark:
			landmark_vertices_xyz.append(l.x)
			landmark_vertices_xyz.append(l.y)
			landmark_vertices_xyz.append(l.z)

		return np.array(landmark_vertices_xyz)

pathname = '../input/mediapipennmodel/O-2.jpg'

arr = preprocess(pathname)
model = load_model('../input/mediapipennmodel/mediapipeNN.h5')
y_prob = model.predict(arr.reshape((1,-1)))
li = y_prob.tolist()
res = list(filter(lambda i: i > 0.9, li[0]))
if len(res) > 0:
	print(alphabets[li[0].index(res[0])])
else:
	print('')
