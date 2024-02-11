## References
- https://blog.devgenius.io/implement-interactive-plotly-dash-plot-within-your-django-project-66f3f4fbef94

# Setup
References: https://realpython.com/django-nginx-gunicorn/
### go to django project directory
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

### Run server
```
nohyp python manage.py runserver 2> /dev/null 
```

tail -100f

