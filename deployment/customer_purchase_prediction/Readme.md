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
