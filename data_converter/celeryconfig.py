## Broker settings.
# broker_url = 'amqp://guest:guest@localhost:5672//'

app.conf.broker_url = 'redis://localhost:6379/0' # redis://:password@hostname:port/db_number

app.conf.broker_transport_options = {'visibility_timeout': 3600}  # 1 The default visibility timeout for Redis is 1 hour

# List of modules to import when the Celery worker starts.
IMPORTS = ('myapp.tasks',)

## Using the database to store task state and results.
# result_backend = 'db+sqlite:///results.db'
app.conf.result_backend = 'redis://localhost:6379/0'
# result_backend = 'redis://localhost/0'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
