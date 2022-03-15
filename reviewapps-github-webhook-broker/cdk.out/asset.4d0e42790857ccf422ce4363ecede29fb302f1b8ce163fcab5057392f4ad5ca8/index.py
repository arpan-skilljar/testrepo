from importlib.abc import FileLoader
import os
import json
from re import template
import boto3
from jinja2 import Environment, FileSystemLoader

def main(event, context):
  if event['path'] == '/':
    message = "Hello World!"

    # Render HTML with Jinja
    fileLoader = FileSystemLoader('resources')
    env = Environment(loader=fileLoader)
    template = env.get_template('index.html')
    html = template.render(
      {
        'message': message
      }
    )

  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'text/html'
    },
    'body': html
  }