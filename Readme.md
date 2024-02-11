# Repository structure
```
├── LICENSE
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── deployment         <- Web app deployment with django platform
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── make_dataset.py
│   │
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
│
└── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
```

# Web application deployment 
## See deployed web application here: http://34.162.200.47:8000/
### Set environment variables
```
ALLOWED_HOST='xx.yyy.zzz.mm:8000'
```
### Go to django project directory)
```
cd deployment/customer_purchase_prediction
```
### Install docker
```
sudo snap install docker
```
### Install redis
```
docker pull redis:4
docker run -p 6360:6379 -d redis
```
### collect static files
```
python manage.py collectstatic
```
### Set firewall rule
This section need to match the cloud provider that being used. For example, if you use Google Cloud Platform you can follow this guide:
https://cloud.google.com/firewall/docs/firewalls

### Run server
```
nohup python manage.py runserver '0.0.0.0:8000' 2> /dev/null 
```

### Check deployment
```
ps auxw | grep runserver
```
# References
- References: https://realpython.com/django-nginx-gunicorn/
- https://blog.devgenius.io/implement-interactive-plotly-dash-plot-within-your-django-project-66f3f4fbef94
