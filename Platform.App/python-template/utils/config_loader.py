import json
import os.path
import errno

def read_json(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            f'config file {filename} must exist.')

    with open(filename, "r") as _file:
        return json.loads(_file.read())


def load_config_file():
    """ Load confiuration file """
    config = read_json("plataforma.json")
    # Database name is now prefered from environment variable instead from app name.
    appName = config["app"]["name"]
    config["database"] = {
        "name": os.environ.get("DB_NAME", appName) ,
        "host": os.environ.get("POSTGRES_HOST", "postgres-hom.czqebrnlxa8n.us-east-1.rds.amazonaws.com"),
        "user": os.environ.get('POSTGRES_USER', "postgres"),
        "password": os.environ.get('POSTGRES_PASSWORD', "postgres"),
    }

    config["http"] = {
        'port': int(os.environ.get('PORT', 9090)),
    }

    config['core_services'] = {
        "scheme": os.environ.get('COREAPI_SCHEME', "http"),
        "host": os.environ.get('COREAPI_HOST', "apicore"),
        "port": os.environ.get('COREAPI_PORT', "9110"),
    }

    config['process_memory'] = {
        "scheme": os.environ.get('PROCESS_MEMORY_SCHEME', "http"),
        "host": os.environ.get('PROCESS_MEMORY_HOST', "process_memory"),
        "port": os.environ.get('PROCESS_MEMORY_PORT', "9091"),
    }

    config['event_manager'] = {
        "scheme": os.environ.get('EVENT_MANAGER_SCHEME', "http"),
        "host": os.environ.get('EVENT_MANAGER_HOST', "event_manager"),
        "port": os.environ.get('EVENT_MANAGER_PORT', "8081"),
    }

    return config
