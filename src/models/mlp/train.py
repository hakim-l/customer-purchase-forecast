import numpy as np
import pandas as pd
import tensorflow.python.keras.callbacks
from sklearn.model_selection import train_test_split
from src.models.mlp.model import MLP
from src.models.mlp.data_generator import (
    TestGenerator,
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

if __name__ == '__main__':
    train_df = pd.read_pickle(os.path.join(DATA_PATH, 'processed', 'train.pickle'))
    # print(train_df.target_array[0])
    output_dim = train_df.target_array[0][0].__len__()
    input_shape = train_df.drop(columns=['target_array']).shape[1]

    train_pipeline = TrainGenerator(batch_size=32)
    test_pipeline = TestGenerator(batch_size=16)
    validation_pipeline = ValidationGenerator(batch_size=32)

    model = MLP(numerical_input_dim=train_df.drop(columns=['target_array']).shape[1],
                categorical_input_dim=0,
                output_dim=output_dim
                )

    # print(input_shape)
    model.build(input_shape=(None, input_shape))

    model.compile(loss=CategoricalCrossentropy(),
                  metrics=AUC(),
                  optimizer=Adam(),
                  run_eagerly=True
                  )

    model_checkpoint= tensorflow.keras.callbacks.ModelCheckpoint(
        os.path.join(MODEL_PATH,
                     'mlp',
                     'checkpoint'
                     ),
        monitor= 'vall_loss',
        verbose= 0,
        save_best_only=False,
        save_weights_only= False,
        mode='auto',
        save_freq='epoch',
        options=None,
        initial_value_threshold=None,
    )

    tensorboard_callback= tensorflow.keras.callbacks.TensorBoard(os.path.join(MODEL_PATH,
                                                                              'mlp',
                                                                              'logs'
                                                                              ),
                                                                 histogram_freq=1
                                                                 )

    early_stopping= tensorflow.keras.callbacks.EarlyStopping(monitor='val_loss',
                                             patience=1)

    model.fit(train_pipeline,
              epochs=200,
              validation_data=validation_pipeline,
              callbacks=[model_checkpoint,tensorboard_callback,early_stopping]
              )
