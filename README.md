# system-status-flask

Python 3 Flask application for reading system statuses via Springshare and
returning a simple JSON response at a single endpoint.

## Requires

* Python 3

## Installation

```bash
# clone this repository
git clone git@github.com:peichman-umd/system-status-flask.git

# install requirements
cd system-status-flask
pip install -r requirements.txt
```

## Running the Webapp

```bash
# create a .env file
cat >.env <<END
STATUS_URL=[Springshare status URL]
FLASK_ENV=development
FLASK_APP=src/app.py
END

# run the app with Flask
flask run
```

This will start the webapp listening on the default port 5000 on localhost 
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests): 
<http://localhost:5000/>

Status endpoint: <http://localhost:5000/status>

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.0.x/quickstart/#debug-mode
