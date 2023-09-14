#final
import pandas as pd
import numpy as np
import pandas_ta as ta
import DataProcessing
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Activation, Flatten, TimeDistributed, RepeatVector, Permute, Multiply, Lambda,Bidirectional
from keras import backend as K

import matplotlib.pyplot as plt

dataProcess = DataProcessing.ETL()
df = dataProcess.Load_Clean_Data('./historical_data/Binance_ETHUSDT_d.csv','1d')

# cols= ['ti_stoch_kd','ti_MACD']
cols= ['ti_stoch_kd']
cols_to_normalize = ['open','high', 'low', 'close', 'base_volume'] # removed num_trades
df = dataProcess.Add_TI_Data(df, cols=cols)
df= dataProcess.Add_Label(df,cols_to_normalize=cols_to_normalize)

#important: reverse the order and Reset the index to start from 0
df= df[::-1]
df.reset_index(drop=True, inplace=True)

#removed time ('unix_start_datetime')
x_cols = cols_to_normalize+cols
labels = ['result_A','result_B']
tensor_temp= df[x_cols+labels]
sequence_num= 14 # also called timesteps
tensor = dataProcess.create_tensor_with_sequence(tensor_temp,labels,sequence_num)
#note we have 2 labels, one for daily(B) another for shortterm (A) => shorterm>daily
#y1= df['result_A']
X= tensor.loc[:,~tensor.columns.isin(labels)]
y2= tensor['result_B']
y = y2.replace({'up': 1, 'down': -1, 'flat':0})
y = to_categorical(y, num_classes=3)
print(y)
# split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
# 3d tensor conversion , further split training data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, shuffle=False)
X_train = X_train.to_numpy().reshape(X_train.shape[0],sequence_num+1,len(x_cols))
X_test = X_test.to_numpy().reshape(X_test.shape[0],sequence_num+1,len(x_cols))
X_val = X_val.to_numpy().reshape(X_val.shape[0],sequence_num+1,len(x_cols))

# model = Sequential([
#     Bidirectional(LSTM(units=128, return_sequences=True, input_shape=(sequence_num+1,len(x_cols)))),
#     Dropout(0.5),
#     Bidirectional(LSTM(64)),
#     Dropout(0.5),
#     Dense(units=1, activation='tanh'),
#     Flatten()
#     ,Activation('softmax')
#     ,RepeatVector(128)
#     ,Permute([2, 1])
#     ,Multiply()
#     ,Lambda(lambda x: K.sum(x, axis=1))
#     ,Dense(3,activation='softmax')])


model = Sequential([
Bidirectional(LSTM(units=82, return_sequences=True, input_shape=(sequence_num+1,len(x_cols)))),
Dropout(0.3),
Bidirectional(LSTM(units=64, return_sequences=True)),
Dropout(0.5),
Bidirectional(LSTM(units=32)),
Dropout(0.7),
Dense(3,activation='softmax')])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=24)
print('Sequential model performance:')
#NOTE: We can add an embedding layer in another implementation
loss, accuracy = model.evaluate(X_test,y_test)


# Plot training and validation accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

# Plot training and validation loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

# Evaluate model on test data

# Plot testing accuracy and loss
plt.bar(['Test Loss', 'Test Accuracy'], [loss, accuracy])
plt.title('Model Testing Results')
plt.ylabel('Metric Value')
plt.show()