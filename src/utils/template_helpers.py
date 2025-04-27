#src/utils/template_helpers.py
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')

template_environment = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def get_template(name: str):
    try: 
        return template_environment.get_template(name)
    except Exception as e:
        print("Error during template retrival:", str(e))
