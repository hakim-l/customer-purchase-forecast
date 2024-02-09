import numpy as np
import pandas as pd
import dotenv
import os
# from sdv.single_table import GaussianCopulaSynthesizer
import pickle
import yaml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

dotenv.load_dotenv()

PROJECT_PATH = os.getcwd()
DATA_PATH = os.path.join(PROJECT_PATH,
                         'data'
                         )
MODEL_PATH = os.path.join(PROJECT_PATH,
                          'models'
                          )

with open(os.path.join(PROJECT_PATH, 'config.yml'), 'r') as infile:
    config = yaml.safe_load(infile)
    infile.close()
del infile


def load_dataset(DATA_PATH: str):
    # assume that my_folder contains many CSV files
    import pandas as pd
    synthetic_data = pd.read_pickle(DATA_PATH)
    customers = synthetic_data['customers'].copy()
    customer_interactions = synthetic_data['customer_interactions'].copy()
    purchase_history = synthetic_data['purchase_history'].copy()
    purchase_history['n_purchase'] = 1
    product_details = synthetic_data['product_details'].copy()

    return customers, customer_interactions, purchase_history, product_details


def calculate_purchase_per_customer(purchase_history: pd.DataFrame):
    purchase_pivot = purchase_history.pivot_table(index=['customer_id',
                                                         'purchase_date'
                                                         ],
                                                  columns='category',
                                                  values='n_purchase',
                                                  aggfunc='count',
                                                  fill_value=0
                                                  )
    return purchase_pivot.groupby('customer_id').transform(pd.Series.cumsum)


def make_split(df: pd.DataFrame,
               train_size: float = 0.7
               ):
    # print(df.target.nunique())
    train_df, test_df = train_test_split(df,
                                         train_size=train_size,
                                         random_state=43,
                                         # stratify=df.target
                                         )
    train_df, validation_df = train_test_split(train_df,
                                               train_size=0.9,
                                               random_state=43
                                               )

    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    validation_df = validation_df.reset_index(drop=True)
    return train_df, validation_df, test_df


if __name__ == '__main__':
    print('Load Dataset (synthetic data)')
    # print(DATA_PATH)
    customers, customer_interactions, purchase_history, product_details = load_dataset(os.path.join(DATA_PATH,
                                                                                                    'interim',
                                                                                                    'synthetic',
                                                                                                    'synthetic_data.pickle'
                                                                                                    )
                                                                                       )
    print('Data loaded')

    # estimate purchase per customer
    purchase_pivot_customer = calculate_purchase_per_customer(

        # merge purchase history and product details
        pd.merge(purchase_history,
                 product_details.loc[:, ['product_id', 'category']],
                 on='product_id'
                 )
    )

    # reformat col name of product_id into string
    purchase_pivot_customer.columns = [str(c) for c in purchase_pivot_customer.columns]

    # calculate time per view of each customer
    customer_interactions['time_per_view'] = customer_interactions.time_spent / customer_interactions.page_views


    df = purchase_history.copy()

    # create target columns by grouping the data based on customer_id and shift the product id 1 step backward
    # This represents the next purchase by the customer
    df['target'] = df.groupby('customer_id')['product_id'].shift(-1).astype(str)

    # remove data with NaN target
    df = df.loc[~df.target.isna(), :].copy()

    # merge df with purchase per customer, product details, and customer interactions
    df = pd.merge(df, purchase_pivot_customer, on=['customer_id', 'purchase_date'])
    df = pd.merge(df, product_details, on=['product_id'])
    df = pd.merge(df, customer_interactions, on='customer_id')

    # drop identity related columns resulting only predictor and target variables
    df = df.drop(columns=['category', 'customer_id', 'product_id', 'purchase_date', 'n_purchase'])


    df.target = df.target.replace({'nan': np.nan})
    df = df.loc[~df.target.isna(), :].reset_index(drop=True)

    #  make OneHotEncoder
    ohe = OneHotEncoder(handle_unknown='infrequent_if_exist',
                        sparse_output=False
                        )

    ohe.fit(df.target.values.reshape(-1, 1))

    # Split data into train set, validation set, and test set
    train_df, validation_df, test_df = make_split(df,
                                                  config['TRAIN_SIZE']
                                                  )

    # compute OHE columns of target variables
    train_df['target_array'] = train_df.target.map(lambda d: ohe.transform(np.array(d).reshape(-1, 1)))
    test_df['target_array'] = test_df.target.map(lambda d: ohe.transform(np.array(d).reshape(-1, 1)))
    validation_df['target_array'] = validation_df.target.map(lambda d: ohe.transform(np.array(d).reshape(-1, 1)))


    print(f'TRAIN Size: {str(train_df.shape[0])}')
    print(f'TEST Size: {str(test_df.shape[0])}')

    train_df = train_df.drop(columns=['target'])
    test_df = test_df.drop(columns=['target'])
    validation_df = validation_df.drop(columns=['target'])

    # save the results
    # print(train_df.columns)
    train_df.to_pickle(os.path.join(DATA_PATH,
                                    'processed',
                                    'train.pickle'
                                    )
                       )

    validation_df.to_pickle(os.path.join(DATA_PATH,
                                         'processed',
                                         'validation.pickle'
                                         )
                            )

    test_df.to_pickle(os.path.join(DATA_PATH,
                                   'processed',
                                   'test.pickle'
                                   )
                      )
    with open(os.path.join(MODEL_PATH, 'ohe.pickle'), 'wb') as infile:
        pickle.dump(ohe, infile)
        infile.close()
    del infile
    print('Completed')
# %%
