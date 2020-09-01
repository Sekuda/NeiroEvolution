import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from keras.layers import Input, Dense
from keras.models import Model

# pip3.exe install --upgrade https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.12.0-py3-none-any.whl

def get_dataset(range_=1000, seed_=2020):
    np.random.seed(seed_)
    df = pd.DataFrame(columns=['x1', 'x2', 'x3', 'y'])
    df.x1 = (np.random.rand(range_) * 1000).astype(int)
    df.x2 = (np.random.rand(range_) * 1000).astype(int)
    df.x3 = (np.random.rand(range_) * 1000).astype(int)
    df.y = df[['x1', 'x2', 'x3']].sum(axis=1)
    return df


df_train = get_dataset(2000)
df_test  = get_dataset(100, seed_=2019)

# print(f"Train shape: {df_train.shape} \nTest shape: {df_test.shape}")
print("Train shape:", df_train.shape ,"\nTest shape:", df_test.shape)

df_train.head()

df_train.max()


def nn_model():
    inputs = Input(shape=(3,))
    output_1 = Dense(1)(inputs)
    predictions = Dense(1)(output_1)

    model = Model(inputs, predictions)
    return model


nn1 = nn_model()

nn1.summary()

nn1.compile(optimizer='adam', loss='mean_squared_error')
nn1.fit(df_train[['x1','x2','x3']].values/3000,
       df_train[['y']].values/3000,
       batch_size=3,
       epochs=6,
       verbose=1,
       validation_data=(df_test[['x1','x2','x3']].values/3000, df_test[['y']].values/3000),
       shuffle=True
      )

df_test['prediction'] = (nn1.predict(df_test[['x1','x2','x3']].values/3000, batch_size=100) * 3000).round().astype('int')
df_test.head()


mean_squared_error(df_test.y, df_test.prediction)


def predict_summ(x1, x2, x3):
    df = pd.DataFrame(columns=['x1', 'x2', 'x3'])

    df.x1 = [x1]
    df.x2 = [x2]
    df.x3 = [x3]

    prediction = (nn1.predict(df[['x1', 'x2', 'x3']].values, batch_size=100)).round().astype('int')

    return prediction[0][0]


prediction = predict_summ(1000000, 20, 3)
print(prediction)