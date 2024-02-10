import math
import tensorflow
import numpy as np
from tensorflow.keras.utils import Sequence
import os
import yaml
import pandas as pd

PROJECT_PATH = os.getcwd()
DATA_PATH = os.path.join(PROJECT_PATH,
                         'data'
                         )
from tensorflow.keras.layers import (
    Reshape,
    Dense,
    Embedding,
    BatchNormalization,
    Flatten
)

from tensorflow.keras.activations import (
    relu, gelu, selu
)

from tensorflow.keras.initializers import (
    he_uniform,
    glorot_uniform
)


# %%
class TrainGenerator(Sequence):
    def __init__(self, batch_size):
        super().__init__()
        self.batch_size = batch_size
        self.train_df = pd.read_pickle(os.path.join(DATA_PATH,
                                                    'processed',
                                                    'train.pickle'
                                                    )
                                       )
        self.y_cols = 'target_array'
        self.x_cols = self.train_df.drop(columns=[self.y_cols]).columns.to_list()
        self.n = self.train_df.shape[0]
        self.shuffle= True

    def __len__(self):
        return math.ceil(self.n /self.batch_size)

    def read_dataset(self):
        return

    def __getitem__(self, index):
        start = index * self.batch_size
        end = min([start + self.batch_size, self.n])
        batch_data = self.train_df.loc[index:end, :].reset_index(drop=True)

        X = batch_data.loc[:, self.x_cols].copy()
        y = np.concatenate(batch_data.loc[:, self.y_cols].copy(),
                           axis=0
                           )
        y = tensorflow.convert_to_tensor(y)
        # print(y.shape)
        return tensorflow.convert_to_tensor(X.values), y

    def on_epoch_end(self):
        if self.shuffle:
            self.train_df = self.train_df.sample(frac=1).reset_index(drop=True)
        return


# %%

class ValidationGenerator(Sequence):
    def __init__(self, batch_size):
        super().__init__()
        self.batch_size = batch_size
        self.validation_df = pd.read_pickle(os.path.join(DATA_PATH,
                                                         'processed',
                                                         'validation.pickle'
                                                         )
                                            ).reset_index(drop=True)
        self.y_cols = 'target_array'
        # print(self.validation_df.columns)
        self.x_cols = self.validation_df.drop(columns=[self.y_cols]).columns.to_list()
        self.n = self.validation_df.shape[0]
        self.shuffle= True

    def __len__(self):
        return math.ceil(self.n /self.batch_size)

    def __getitem__(self, index):
        start = index * self.batch_size
        end = min([start + self.batch_size, self.n])
        batch_data = self.validation_df.loc[index:end, :].reset_index(drop=True)

        X = batch_data.loc[:, self.x_cols].copy()
        y = np.concatenate(batch_data.loc[:, self.y_cols].copy(),
                           axis=0
                           )
        y = tensorflow.convert_to_tensor(y)
        # print(y.shape)
        return tensorflow.convert_to_tensor(X.values), y

    def on_epoch_end(self):
        if self.shuffle:
            self.validation_df = self.validation_df.sample(frac=1).reset_index(drop=True)
        return


# %%

class InferenceDataGenerator(Sequence):
    def __init__(self, batch_size,df):
        super().__init__()
        self.df = df
        self.batch_size = batch_size
        self.y_cols = 'target_array'
        self.x_cols = self.df.drop(columns=[self.y_cols]).columns.to_list()
        self.shuffle= False
        self.n= df.shape[0]

    def __len__(self):
        return math.ceil(self.n /self.batch_size)

    def __getitem__(self, index):
        start = index * self.batch_size
        end = min([start + self.batch_size, self.n])
        batch_data = self.df.loc[index:end, :].reset_index(drop=True)

        X = batch_data.loc[:, self.x_cols].copy()
        return tensorflow.convert_to_tensor(X.values)

    def on_epoch_end(self):
        if self.shuffle:
            self.df = self.df.sample(frac=1).reset_index(drop=True)
        return
