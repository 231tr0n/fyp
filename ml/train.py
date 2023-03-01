import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

train_data = pd.read_csv('train.csv')
train_data = train_data.sample(frac = 1).reset_index(drop = True)
test_data = pd.read_csv('test.csv')
test_data = test_data.sample(frac = 1).reset_index(drop = True)

train_y = train_data.pop('character')
train_x = train_data
test_y = test_data.pop('character')
test_x = test_data

print()
print(train_y.iloc[:,].value_counts().describe())
print(test_y.iloc[:,].value_counts().describe())
print()

train_y_encoded = pd.get_dummies(train_y, prefix = 'target')
test_y_encoded = pd.get_dummies(test_y, prefix = 'target')

model = Sequential()
model.add(Dense(126, input_shape = (84,), activation = 'relu'))
model.add(Dense(168, activation = 'relu'))
model.add(Dense(126, activation = 'relu'))
model.add(Dense(84, activation = 'relu'))
model.add(Dense(42, activation = 'relu'))
model.add(Dense(36, activation = 'softmax'))

print()
print(model.summary())
print()

model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

history = model.fit(train_x, train_y_encoded, epochs = 10, batch_size = 10, verbose = 1)

plt.plot(history.history['loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

_, accuracy = model.evaluate(test_x, test_y_encoded)
print()
print('Accuracy: %.2f' % (accuracy * 100))
print()

model.save('model.h5')
