import pandas as pd
import numpy as np
import pandas_ta as ta
from sklearn.preprocessing import MinMaxScaler
import logging
import matplotlib.pyplot as plt


# NOTES: We are currenlty assuming that all values are present in the excel file:
# the data is continous. TO ADD: check for discontnous data and find a replacement strategy.


class ETL:
    def __init__(self):
        print('created')

    def Load_Clean_Data(self, input_file_path, interval='1d'):
        try:
            # second row is column names
            df = pd.read_csv(input_file_path, header=1)
            col_list = ['unix_start_datetime', 'start_date', 'symbol', 'open',
                        'high', 'low', 'close', 'base_volume', 'quote_volume', 'num_trades']
            df.columns = col_list
            df["interval"] = interval
            df.dropna(subset=['symbol', 'unix_start_datetime', 'open','close', 'high', 'low', 'base_volume'], inplace=True)
            return df.copy()
        except Exception as e:
            logging.error('Failed to load and clean data: \n' + str(e))

    def Add_TI_Data(self, df, k=14, d=3, cols= ['ti_stoch_kd','ti_MACD']):
        try:
            # add technical indicators
            # adds 2 columns "STOCHk_14_3_3","STOCHd_14_3_3"
            df.ta.stoch(high='high', low='low', close='close',k=k, d=d, fillna=True, append=True)
            MACD = ta.macd(df['close'])
            df['MACD'] = MACD['MACD_12_26_9']
            df['MACDs'] = MACD['MACDs_12_26_9']
            df = df.rename(columns={"STOCHk_14_3_3": "STOCHk", "STOCHd_14_3_3": "STOCHd"})
            #Normalize data
            norm_kd=[0,0]
            norm_macd=[0,0]
            for index, row in df.iloc[2:].iterrows():
                # KD line normalization
                if (df.at[index - 1,'STOCHk'] < df.at[index - 1,'STOCHd'] and row['STOCHk'] < row['STOCHd']):
                    if (20 >= df.at[index - 2,'STOCHk'] and 20 >= df.at[index - 1,'STOCHk'] and 25 <= row['STOCHk']):
                        norm_kd.append(1.5)
                    elif (20 < df.at[index - 2,'STOCHk'] < 80 or 20 < df.at[index - 1,'STOCHk'] < 80 or 20 < row['STOCHk'] < 80):
                        norm_kd.append(1)
                    else:
                        norm_kd.append(0)
                elif (df.at[index - 1,'STOCHk'] > df.at[index - 1,'STOCHd'] and row['STOCHk'] > row['STOCHd']):
                    if (80 <= df.at[index - 2,'STOCHk'] and 80 <= df.at[index - 1,'STOCHk'] and 75 >= row['STOCHk']):
                        norm_kd.append(-1.5)
                    elif (20 < df.at[index - 1,'STOCHk'] < 80 or 20 < df.at[index - 1,'STOCHk'] < 80 or 20 < row['STOCHk'] < 80):
                        norm_kd.append(-1)
                    else:
                        norm_kd.append(0)
                else:
                    norm_kd.append(0)

                # MACD Norlmalization
                if (df.at[index - 1,'MACD'] < df.at[index - 1,'MACDs'] and row['MACDs'] < row['MACD']):
                    norm_macd.append(1)
                elif (df.at[index - 1,'MACD'] > df.at[index - 1,'MACDs'] and row['MACDs'] > row['MACD']):
                    norm_macd.append(-1)
                else:
                    norm_macd.append(0)
            # print(df.shape[0])
            # print(len(norm_kd))
            # print(len(norm_macd))
            df[cols[0]]= norm_kd
            df[cols[1]]= norm_macd#test
            return df
        except Exception as e:
            logging.ERROR('Failed to add TI data: \n' + str(e))

    def Add_Label(self, df, window_size=5, alpha=0.005,cols_to_normalize= ['open','high', 'low', 'close', 'base_volume', 'quote_volume', 'num_trades']):
        try:
            #first normalize the ohlcv data
            # cols_to_normalize = ['open','high', 'low', 'close', 'base_volume', 'quote_volume', 'num_trades']
            df_norm = self.normalize_ohlcv_data(df,cols_to_normalize)
            for col in cols_to_normalize:
                df[col]= df_norm[col]
            #Create Labels: 2 types of label, a) short term b) daily
            ma_minus = df['close'].rolling(window=window_size).mean()
            ma_plus = ma_minus.shift(-(window_size-1))
            n=5
            resultA = []
            resultB = []
            for i in range(ma_plus.shape[0]):
                #NOTE: bull, bear flat or buy sell hold
                #TODO: what
                tempA = "up" if (ma_plus[i]-ma_minus[i]) > (ma_minus[i]*alpha) else "down" if (ma_plus[i]-ma_minus[i]) < (-ma_minus[i]*alpha) else "flat"
                resultA.append(tempA)
                if(i==(ma_plus.shape[0] -1)):
                    resultB.append('flat')
                else:
                    tempB= "up" if (df.loc[i+1,"close"]- df.loc[i,"close"]) > (df.loc[i,"close"]*alpha) else "down" if (df.loc[i+1,"close"]-  df.loc[i,"close"]) < (-df.loc[i,"close"]*alpha) else "flat"
                    resultB.append(tempB)
            df['result_A'] = resultA
            df['result_B'] = resultB
            #Drop all NA value
            df = df.drop(range(33)) #TODO: make dynamic
            return df
        except Exception as e:
            logging.error('Failed to add labels to data: \n' + str(e))
            return
    def create_tensor_with_sequence(self,df,output_list,sequence_length=14):
        #code to convert to 3d vector
        # Create a copy of the original data
        data_seq = df.copy()
        # Create new columns for each day of historical data
        for i in range(1, sequence_length + 1):
            for col in df.columns:
                if(col in output_list):
                    continue
                data_seq[f'{col}_lag{i}'] = df[col].shift(i)
        # Drop rows with missing values
        data_seq.dropna(inplace=True)
        return data_seq

    #Note we have created TI columns
    def normalize_ohlcv_data(self, df,cols_to_normalize):
        scaler = MinMaxScaler()
        scaler.fit(df[cols_to_normalize])
        df_norm = scaler.transform(df[cols_to_normalize])
        df_norm = pd.DataFrame(df_norm, columns=cols_to_normalize)
        return df_norm

    def visualizeValidation(self, history):
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
    def getPredictionData(self,y_pred):
        binary_2d = np.zeros_like(y_pred)
        # loop through each row of probs_2d
        # loop through each row of probs_2d
        for i in range(y_pred.shape[0]):
            # set values above 0.35 to 1, and below to 0
            temp = []
            isAdded = False
            for val in y_pred[i]:
                if val > 0.35:
                    if not isAdded:
                        temp.append(1)
                        isAdded = True
                    elif val >= max(temp):
                        temp = [0 for _ in range(len(temp))]
                        temp.append(1)
                    else:
                        temp.append(0)
                else:
                    temp.append(0)
                    isAdded = False
            binary_2d[i] = np.array(temp)
        return binary_2d
