import pickle

import tensorflow
import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import numpy as np

from pathlib import Path

# os.chdir('../')

CURDIR = Path(__file__).resolve().parent.parent.parent

import plotly.graph_objects as go
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash
from dash import html
from dash import dcc, callback
import sqlite3

from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd


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


def load_ohe():
    with open(os.path.join(CURDIR,
                           'models', 'ohe.pickle'),
              'rb'
              ) as infile:
        ohe = pickle.load(infile)
        infile.close()
    del infile
    return ohe


X_COLS = ['Beauty', 'Clothing', 'Electronics', 'Home & Kitchen', 'price',
          'ratings', 'page_views', 'time_spent', 'time_per_view']


def format_input():
    engine = sqlite3.connect(os.path.join(CURDIR,
                                          'db.sqlite3'
                                          )
                             )
    purchase_history_cols = ['Beauty', 'Clothing', 'Electronics', 'Home & Kitchen', ]
    customers = pd.read_sql('select * from customers', engine)  # where customer_id={customer}
    customer_interactions = pd.read_sql('select * from customer_interactions', engine)  # where customer_id={customer}
    purchase_history = pd.read_sql('select * from purchase_history', engine)  # where customer_id={customer}
    purchase_history['n_purchase'] = 1

    product_details = pd.read_sql(f'select * from product_details', engine)

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

    df.target = df.target.replace({'nan': np.nan})
    df = df.loc[df.target.isna(), :].reset_index(drop=True)

    df = df.drop(columns=['target'])

    # df = df.tail(1).copy()

    # merge df with purchase per customer, product details, and customer interactions
    df = pd.merge(df, purchase_pivot_customer, on=['customer_id', 'purchase_date'])
    df = pd.merge(df, product_details, on=['product_id'])
    df = pd.merge(df, customer_interactions, on='customer_id')

    df = df.drop(columns=['category', 'product_id', 'purchase_date', 'n_purchase'])
    for c in purchase_history_cols:
        if c not in df.columns:
            df[c] = 0
    df = df.set_index('customer_id', )
    return df,product_details


def make_plot(value):
    # print(value)
    # customer= self.request.GET.get('q')
    df,product_details = format_input()
    X = tensorflow.convert_to_tensor(df.loc[:, X_COLS].values)
    model = tensorflow.keras.models.load_model(os.path.join(CURDIR,
                                                            'models',
                                                            'mlp',
                                                            'checkpoint'
                                                            )
                                               )

    ohe = load_ohe()
    categories = ohe.categories_

    y_predict = pd.DataFrame(data=model.predict(X),
                             columns=[s.strip('.0') for s in categories[0]]
                             )
    y_predict['customer_id'] = df.index
    if value != 'all':
        y_predict = y_predict.loc[y_predict.customer_id == value, :].copy()
    predict_df = y_predict.melt(id_vars='customer_id', value_vars=y_predict.columns, var_name='product_id',
                                value_name='purchased_probability')
    predict_df.purchased_probability = predict_df.purchased_probability
    product_details.product_id= product_details.product_id.astype(str)

    predict_df= pd.merge(predict_df,
                         product_details.loc[:, ['product_id','category']],
                         on='product_id'
                         )

    return predict_df.loc[:,['customer_id','product_id','category','purchased_probability']].sort_values('purchased_probability',ascending=False)


engine = sqlite3.connect(os.path.join(CURDIR,
                                      'db.sqlite3'
                                      )
                         )
app = DjangoDash(name='PurchasePrediction')
customers = make_plot('all')  # where customer_id={customer}

# Configure app layout
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div([
                    # Add dropdown for option selection
                    dcc.Dropdown(
                        id='customer',
                        options=[{'label': i, 'value': i} for i in customers.customer_id.unique().tolist() + ['all']],
                        value='all')
                ],
                    style={'width': '25%', 'margin': '0px auto','display': 'inline-block'}
                ),
            ])
        ]
        ),
        dbc.Col(
            [
                dbc.Row([
                    html.Div([
                        # dcc.Graph(id = 'customer_plot',
                        #           # animate = True,
                        #           # style={"backgroundColor": "#FFF0F5"}
                        #         )
                        dbc.Container([
                            dash_table.DataTable(customers.to_dict(orient='records'),
                                                 [{'name': i, 'id': i} for i in customers.columns],
                                                 id='tbl',
                                                 # filter_action="native",
                                                 ),
                            dbc.Alert(id='table_out')
                        ], id='table-container')
                    ],
                        # style={'display': 'inline-block'}
                    )
                ]
                )
            ]
        )
    ],justify= 'center'
    ),

]
)


# @app.callback(
#     Output('customer_plot', 'figure'),
#     [Input('customer', 'value')]
# )
@app.callback(Output('tbl', 'data'),
              [Input('customer', 'value')]
              )
def display_value(value):
    """
    This function returns figure object according to value input
    Input: Value specified
    Output: Figure object
    """
    # Get daily cases plot with input value

    df = make_plot(value)
    return df.to_dict(orient='records')
