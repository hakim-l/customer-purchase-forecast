import pandas as pd
import dotenv
import os
from sdv.datasets.local import load_csvs
from sdv.multi_table import HMASynthesizer
# from sdv.single_table import GaussianCopulaSynthesizer
from sdv import metadata
import pickle

dotenv.load_dotenv()

PROJECT_PATH = os.getcwd()
DATA_PATH = os.path.join(PROJECT_PATH,
                         'data'
                         )
MODEL_PATH = os.path.join(PROJECT_PATH,
                          'models'
                          )

# load datasets
def load_dataset(DATA_PATH: str):
    # assume that my_folder contains many CSV files
    datasets = load_csvs(
        folder_name=DATA_PATH,
        read_csv_parameters={
            'skipinitialspace': True,
            'parse_dates': True
        })

    return datasets


# customer_interactions, product_details, purchase_history
if __name__ == '__main__':
#%% load dataset
    print('Load Dataset')
    # print(DATA_PATH)
    datasets = load_dataset(os.path.join(DATA_PATH,
                                         'interim',
                                         'original'
                                         )
                            )
    print(datasets.keys())
    print('Data loaded')

#%% set table schemas
    print('Create metadata')
    dataset_metadata = metadata.MultiTableMetadata()
    dataset_metadata.detect_from_dataframes(data=datasets)
    dataset_metadata.update_column(table_name='customers', column_name='customer_id', sdtype='id')
    dataset_metadata.update_column(table_name='customer_interactions', column_name='customer_id', sdtype='id')
    dataset_metadata.update_column(table_name='product_details', column_name='product_id', sdtype='id')
    dataset_metadata.update_column(table_name='purchase_history', column_name='customer_id', sdtype='id')
    dataset_metadata.update_column(table_name='purchase_history', column_name='product_id', sdtype='id')

    dataset_metadata.set_primary_key(
        table_name='customers',
        column_name='customer_id'
    )

    dataset_metadata.set_primary_key(
        table_name='product_details',
        column_name='product_id'
    )

    dataset_metadata.add_relationship(
        parent_table_name='customers',
        child_table_name='customer_interactions',
        child_foreign_key='customer_id',
        parent_primary_key='customer_id'
    )

    dataset_metadata.add_relationship(
        parent_table_name='customers',
        child_table_name='purchase_history',
        parent_primary_key='customer_id',
        child_foreign_key='customer_id'
    )

    dataset_metadata.add_relationship(
        parent_table_name='product_details',
        child_table_name='purchase_history',
        parent_primary_key='product_id',
        child_foreign_key='product_id'
    )

    print('Validate metadata')
    dataset_metadata.validate()
    print('Dataset validated')

#%% train generator

    print('Metadata created')
    # Create the synthesizer
    synthesizer = HMASynthesizer(dataset_metadata)

    # Train the synthesizer
    synthesizer.fit(datasets)
    synthesizer.save(
        filepath=os.path.join(MODEL_PATH,
                              'my_synthesizer.pkl'
                              )
    )

    # Generate synthetic data
    synthetic_data = synthesizer.sample(scale=100)

    with open(os.path.join(DATA_PATH,
                           'interim',
                           'synthetic',
                           'synthetic_data.pickle',
                           ),
              'wb'
              ) as infile:
        pickle.dump(synthetic_data,
                    infile
                    )
        infile.close()
    del infile
