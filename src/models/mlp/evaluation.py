import numpy as np
import pandas as pd
import tensorflow.python.keras.callbacks
from sklearn.model_selection import train_test_split
from src.models.mlp.model import MLP

from src.models.mlp.data_generator import (
    InferenceDataGenerator,
    TrainGenerator,
    ValidationGenerator
)
import math
from tensorflow.keras.losses import (
    CategoricalCrossentropy
)

from tensorflow.keras.metrics import (
    F1Score,
    AUC
)

from tensorflow.keras.optimizers import (
    Adam
)

import os

PROJECT_PATH = os.getcwd()
DATA_PATH = os.path.join(PROJECT_PATH,
                         'data'
                         )
MODEL_PATH = os.path.join(PROJECT_PATH,
                          'models'
                          )

def format_target(df):
    y= np.concatenate(df.loc[:, 'target_array'].copy(),
                   axis=0
                   )
    return tensorflow.convert_to_tensor(y)


if __name__ == '__main__':
    train_df = pd.read_pickle(os.path.join(DATA_PATH, 'processed', 'train.pickle'))
    validation_df = pd.read_pickle(os.path.join(DATA_PATH, 'processed', 'validation.pickle'))
    test_df = pd.read_pickle(os.path.join(DATA_PATH, 'processed', 'test.pickle'))

    # print(train_df.target_array[0])
    output_dim = train_df.target_array[0][0].__len__()
    input_shape = train_df.drop(columns=['target_array']).shape[1]

    train_pipeline = InferenceDataGenerator(batch_size=32,
                                            df= train_df
                                            )
    test_pipeline = InferenceDataGenerator(batch_size=16,
                                           df= test_df
                                           )

    validation_pipeline = InferenceDataGenerator(batch_size=32,
                                                 df= validation_df
                                                 )

    x_train= train_df.loc[:, train_pipeline.x_cols].values
    y_train = format_target(train_df)

    x_val= validation_df.loc[:, validation_pipeline.x_cols].values
    y_val= format_target(validation_df)

    x_test= test_df.loc[:, test_pipeline.x_cols].copy()
    y_test= format_target(test_df)

    # print(input_shape)
    model= tensorflow.keras.models.load_model(os.path.join(MODEL_PATH,
                                                           'mlp',
                                                           'checkpoint'
                                                           )
                                              )



    train_prediction= model.predict(x_train)
    validation_prediction= model.predict(x_val)
    test_prediction= model.predict(x_test)
    auc= AUC()

    print(train_prediction.shape)

    train_auc= auc(y_train,
                   train_prediction
                   )

    validation_auc= auc(y_val,
                        validation_prediction
                        )

    test_auc= auc(y_test,
                  test_prediction
                  )

    print(f'Test AUC: {str(test_auc)}')
    print(f'Validation AUC: {str(validation_auc)}')
    print(f'Test AUC: {str(test_auc)}')