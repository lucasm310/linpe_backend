import json
from os import environ

import boto3
from dotenv import load_dotenv

load_dotenv()

class Cognito:
    def __init__(self):
        self.client = self._get_client()
        self.userpoolid = environ.get("USERPOOL_ID")
        self.grupos = ['geral','ligantes','diretoria']
        pass

    def _get_client(self):
        boto3.setup_default_session(region_name=environ.get("AWS_REGION"))
        client = boto3.client('cognito-idp')
        return client