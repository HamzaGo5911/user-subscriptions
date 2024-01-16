import os
from dotenv import load_dotenv
from pathlib import Path

basedir = Path(__file__).parent

env_file = basedir / '.env'
if env_file.is_file():
    load_dotenv(env_file)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
