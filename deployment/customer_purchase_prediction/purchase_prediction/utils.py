import pickle

import tensorflow
import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from pathlib import Path
# os.chdir('../')

CURDIR= Path(os.getcwd()).resolve().parent
# Create your views here.
print(CURDIR)
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from dash import html
from dash import dcc
import sqlite3

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

def load_ohe_():
    with open(os.path.join(CURDIR,'customer_purchase_prediction','static','ohe.pickle'),
              'rb'
              ) as infile:
        ohe= pickle.load(infile)
        infile.close()
    del infile
    return ohe

X_COLS=['Beauty', 'Clothing', 'Electronics', 'Home & Kitchen', 'price',
        'ratings', 'page_views', 'time_spent', 'time_per_view']

def format_input_():
    engine= sqlite3.connect(os.path.join(CURDIR,
                                         'customer_purchase_prediction',
                                         'db.sqlite3'
                                         )
                            )
    purchase_history_cols=['Beauty', 'Clothing', 'Electronics', 'Home & Kitchen',]
    customers= pd.read_sql('select * from customers',engine) # where customer_id={customer}
    customer_interactions= pd.read_sql('select * from customer_interactions',engine) #where customer_id={customer}
    purchase_history= pd.read_sql('select * from purchase_history',engine) # where customer_id={customer}
    purchase_history['n_purchase']=1

    product_details= pd.read_sql(f'select * from product_details',engine)

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

    df['target'] = df.groupby('customer_id')['product_id'].shift(-1).astype(str)

    df.target= df.target.replace({'nan':np.nan})
    df= df.loc[df.target.isna(),:].reset_index(drop=True)

    df= df.drop(columns=['target'])


    # df = df.tail(1).copy()

    # merge df with purchase per customer, product details, and customer interactions
    df = pd.merge(df, purchase_pivot_customer, on=['customer_id', 'purchase_date'])
    df = pd.merge(df, product_details, on=['product_id'])
    df = pd.merge(df, customer_interactions, on='customer_id')

    df = df.drop(columns=['category', 'product_id', 'purchase_date', 'n_purchase'])
    for c in purchase_history_cols:
        if c not in df.columns:
            df[c]=0
    df= df.set_index('customer_id',)
    return df

def make_plot_():
    # customer= self.request.GET.get('q')
    df = format_input_()
    X = tensorflow.convert_to_tensor(df.loc[:, X_COLS].values)
    model = tensorflow.keras.models.load_model(os.path.join(CURDIR,
                                                            'customer_purchase_prediction',
                                                            'static',
                                                            'mlp',
                                                            'checkpoint'
                                                            )
                                               )

    ohe = load_ohe_()
    categories = ohe.categories_

    y_predict = pd.DataFrame(data=model.predict(X),
                             columns=[s.strip('.0') for s in categories[0]]
                             )
    y_predict['customer_id'] = df.index
    y_predict.melt(id_vars='customer_id', value_vars=y_predict.columns, var_name='product_id',
                   value_name='purchased_probability'
                   )

    fig = go.Figure(go.Table(header={'values': y_predict.columns},
                             cells={'values': y_predict.T.values}
                             )
                    )

    fig.update_layout(#barmode='stack',
        title_text = 'Purchase Prediction',
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        xaxis_title = 'Date',
        yaxis_title = 'Total_Daily_Cases'
    )
    print('PASSED 2')
    return fig