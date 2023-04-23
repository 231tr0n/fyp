import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import cv2
from tensorflow.keras.models import load_model
import numpy as np
import mediapipe as mp
import spellchecker
from collections import Counter

spell_checker = spellchecker.SpellChecker()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

alphabets = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
model = load_model('model1.h5')

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

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    model_complexity = 0,
    min_detection_confidence = 0.5,
) as hands:
    word = ''
    temp_word = ''
    underscore_counter = 0
    while cap.isOpened():
        success, aimage = cap.read()
        prediction = '_'
        if not success:
            continue
        image = aimage.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        results = hands.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            coordinates = [process_results(results, aimage)]
            coordinates = np.array(coordinates)
            probabilities = model.predict(coordinates, verbose = 0)
            plist = probabilities.tolist()
            res = list(filter(lambda i: i > 0.9, plist[0]))
            if len(res) > 0:
                prediction = alphabets[plist[0].index(res[0])]
            else:
                prediction = '_'
                underscore_counter += 1
            if underscore_counter >= 20:
                temp_word = ''
                underscore_counter = 0
                print("Temp word cleared")
            if len(temp_word) == 30:
                temp1 = Counter(temp_word)
                temp1 = max(temp1, key = temp1.get)
                word += str(temp1)
                temp_word = ''
                print("Temp Word:", word)
            else:
                if prediction != "_":
                    temp_word += prediction
        else:
            underscore_counter += 1
        image = cv2.putText(image, prediction, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('test', image)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    corrected_word = spell_checker.correction(word)
    print("Correct word:", corrected_word)
