import pickle

from django.shortcuts import render
from django.db.models import Q,QuerySet,F


import tensorflow
import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import numpy as np

CURDIR= os.getcwd()
# Create your views here.
import plotly.graph_objects as go
from .dashapp import plot
from .utils import *
from django.shortcuts import render


def purchase_prediction_view(request):
    return render(request=request,
                  template_name='purchase_prediction/index.html',
                  # context={'customer_plot':plot}
                  )
