import sqlite3
import os
import pandas as pd

CURDIR= os.getcwd()
from .dashapp import plot
from plotly.offline import plot as po
# from .utils import *
from django.shortcuts import render
from plotly import graph_objects as go

def purchase_prediction_view(request):
    def bar_n_purchase_plot():
        engine = sqlite3.connect(os.path.join(CURDIR,
                                              'db.sqlite3'
                                              )
                                 )
        query="""
        select
        product_details.category as product_category,
        count() as n_purchase
        from purchase_history
        left join product_details on purchase_history.product_id = product_details.product_id
        group by 1
        """
        data= pd.read_sql(sql=query,
                          con=engine
                          )
        bar_= go.Bar(name='product_category_historical',
                                    x=data.product_category,
                                    y= data.n_purchase
                                    )
        layout= {
            'title': 'Purchase by Product Category',
            'yaxis':{'range':[data.n_purchase.min(),data.n_purchase.max()]},
            'xaxis':{'categoryarray':data.product_category.unique().tolist()}
            # 'xaxis':
        }
        fig= go.Figure(data= [bar_],
                       layout= layout
                       )

        fig.update_layout(barmode='stack',
                          title_text= 'Numberof Historical Purchase',
                          xaxis_title='Product Category',
                          yaxis_title='Number of Purchase'
                          )
        plot_fig= po(fig,
                     output_type='div',
                     # include_plotlyjs=False,

                     )
        return plot_fig


    context={
        'product_historical_purchase_bar': bar_n_purchase_plot()
    }
    return render(request=request,
                  template_name='purchase_prediction/index.html',
                  context= context
                  # context={'customer_plot':plot}
                  )

