import json
from os import environ

import boto3
from dotenv import load_dotenv

from app.helpers.base_aws import exception_handler

load_dotenv()


class S3:
    def __init__(self):
        self.bucket = environ.get("DOCUMENTOS_BUCKET")
        response = self.get_client()
        if response.status is True:
            self.client = response.response
        else:
            raise Exception("erro conectar no s3")
    
    @exception_handler
    def get_client(self):
        boto3.setup_default_session(region_name=environ.get("AWS_REGION"))
        client = boto3.client("s3")
        return client

    @exception_handler
    def get_url(self, arquivo):
        max_time = 3600
        response = self.client.generate_presigned_url("get_object", Params={"Bucket": self.bucket, "Key": arquivo}, ExpiresIn=max_time)
        return response

    @exception_handler
    def make_url(self, arquivo):
        max_time = 300
        response = self.client.generate_presigned_post(Bucket=self.bucket, Key=arquivo, ExpiresIn=max_time)
        return response
