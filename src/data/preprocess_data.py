import pandas as pd
import dotenv
import os
from sdv.datasets.local import load_csvs
import re

dotenv.load_dotenv()

PROJECT_PATH = os.getcwd()
DATA_PATH = os.path.join(PROJECT_PATH,
                         'data'
                         )


def load_dataset(DATA_PATH: str):
    # assume that my_folder contains many CSV files
    customer_interactions = pd.read_csv(os.path.join(DATA_PATH,
                                                     'raw',
                                                     'customer_interactions.csv'
                                                     ),
                                        sep=','
                                        )

    product_details = pd.read_csv(os.path.join(DATA_PATH,
                                               'raw',
                                               'product_details.csv'
                                               ),
                                  sep=';'
                                  )

    purchase_history = pd.read_csv(os.path.join(DATA_PATH,
                                                'raw',
                                                'purchase_history.csv',
                                                ),
                                   sep=';'
                                   )
    return customer_interactions, product_details, purchase_history


def remove_unnamed_cols(df):
    cols = df.columns
    dropped_cols = []
    for c in cols:
        if re.match(r'Unnamed.*', c):
            dropped_cols.append(c)

    results = df.drop(columns=dropped_cols)
    return results


if __name__ == '__main__':
    print('Load Dataset')
    customer_interactions, product_details, purchase_history = load_dataset(os.path.join(DATA_PATH))

    print('Remove Unnmaed cols')
    f_customer_interactions = remove_unnamed_cols(customer_interactions)
    f_product_details = remove_unnamed_cols(product_details)
    f_purchase_history = remove_unnamed_cols(purchase_history)

    print('Save results')
    f_customer_interactions.to_csv(os.path.join(DATA_PATH,
                                                'interim',
                                                'original',
                                                'customer_interactions.csv'
                                                ),
                                   index=False
                                   )

    f_product_details.to_csv(os.path.join(DATA_PATH,
                                          'interim',
                                          'original',
                                          'product_details.csv'
                                          ),
                             index=False
                             )

    f_purchase_history.to_csv(os.path.join(DATA_PATH,
                                           'interim',
                                           'original',
                                           'purchase_history.csv'
                                           ),
                              index=False
                              )

    f_customers = customer_interactions.loc[:, ['customer_id']].drop_duplicates()
    f_customers.to_csv(os.path.join(DATA_PATH,
                                    'interim',
                                    'original',
                                    'customers.csv'
                                    )
                       ,
                       index=False
                       )
