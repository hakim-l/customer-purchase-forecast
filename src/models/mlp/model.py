import tensorflow
from tensorflow.keras.layers import (
Dense,
Embedding,
BatchNormalization,
ReLU
)

from tensorflow.keras.initializers import (
he_uniform
)

from tensorflow.keras.activations import (
relu,
selu,
gelu,
softmax
)

from tensorflow.keras.regularizers import (
L1L2
)

#%%

class MLP(tensorflow.keras.Model):
    def __init__(self,
                 numerical_input_dim,
                 categorical_input_dim,
                 output_dim
                 ):
        super().__init__()

        self.categorical_input_dim= categorical_input_dim
        self.numerical_input_dim= numerical_input_dim
        self.output_dim= output_dim

        if self.categorical_input_dim>0:
            self.embedding_layer= Embedding(categorical_input_dim,
                                            100,
                                            )

            self.batch_norm_e= BatchNormalization(axis=-1)
            self.relu_embeding= ReLU()

        self.dense_1= Dense(numerical_input_dim+50,
                            kernel_initializer= he_uniform(),
                            bias_initializer= 'zeros',
                            kernel_regularizer= L1L2()
                            )
        self.batch_norm_1= BatchNormalization()
        self.relu_1= ReLU()

        self.dense_2= Dense(numerical_input_dim+100,
                            kernel_initializer= he_uniform(),
                            bias_initializer= 'zeros',
                            kernel_regularizer= L1L2()
                            )
        self.batch_norm_2= BatchNormalization()
        self.relu_2= ReLU()

        self.dense_3= Dense(self.output_dim,
                            kernel_initializer= he_uniform(),
                            bias_initializer= 'zeros',
                            kernel_regularizer= L1L2()
                            )
        self.batch_norm_3= BatchNormalization()
        self.softmax= softmax

    def call(self, inputs, training=None, mask=None):

        if self.categorical_input_dim>0:
            x= self.embedding_layer(inputs)
            x= self.batch_norm_e(x)
            x= self.relu_embeding(x)

            x= self.dense_1(x)
            x= self.batch_norm_1(x)
            x= self.relu_1(x)

            x= self.dense_2(x)
            x= self.batch_norm_2(x)
            x= self.relu_2(x)

            x= self.dense_3(x)
            x= self.batch_norm_3(x)
            x= self.softmax(x)
        else:
            x= self.dense_1(inputs)
            x= self.batch_norm_1(x)
            x= self.relu_1(x)

            x= self.dense_2(x)
            x= self.batch_norm_2(x)
            x= self.relu_2(x)

            x= self.dense_3(x)
            x= self.batch_norm_3(x)
            x= self.softmax(x)
        # print(x.shape)
        return x