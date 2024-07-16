# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os, random, string

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')
    direccion = 'residencialmysql.cn8k44ascgyp.us-east-1.rds.amazonaws.com'
    usuario = 'admin'
    contrasena = 'j&>_RS;9vKect2P'
    nombre_base_datos = 'Residencial'  # Reemplaza con el nombre de tu base de datos

# Cadena de conexión
    SQLALCHEMY_DATABASE_URI =  f"mysql+pymysql://{usuario}:{contrasena}@{direccion}/{nombre_base_datos}?charset=utf8mb4"

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
