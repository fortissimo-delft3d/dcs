import json
import os
from logging.config import dictConfig, logging
from ConfigParser import ConfigParser

with open('logging.json') as jl:
    dictConfig(json.load(jl))

class Settings:

    def __init__(self):
        if not os.path.exists('ilm.conf'):
            logging.error('we need a valid config, none found!')
            raise
        parser = ConfigParser()
        parser.read('ilm.conf')
        self.aws_region = parser.get('aws', 'region')
        self.aws_secret = parser.get('aws', 'secret_key')
        self.aws_access = parser.get('aws', 'access_key')
        self.aws_seqgrp = parser.get('aws', 'security_group')
        self.aws_auto_remove_failed = parser.getboolean('aws', 'auto_remove_failed')
        self.recovery_path = parser.get('parameters', 'recovery_path')
        self.web = parser.get('parameters', 'web')
