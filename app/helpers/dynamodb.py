import json
from os import environ

import boto3
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv

from app.helpers.base_aws import exception_handler

load_dotenv()


class DynamoDB:
    def __init__(self, table, nome_api, key):
        self.table = table
        self.nome_api = nome_api
        self.key = key
        response = self.get_client()
        if response.status is True:
            self.client = response.response
        else:
            raise Exception("erro conectar no banco")

    @exception_handler
    def get_client(self):
        boto3.setup_default_session(region_name=environ.get("AWS_REGION"))
        dynamodb = boto3.resource("dynamodb")
        client = dynamodb.Table(self.table)
        return client

    @exception_handler
    def cria_item(self, dados):
        dados = json.loads(dados)
        response = self.client.put_item(Item=dados)
        return dados[self.key]

    @exception_handler
    def busca_por_id(self, id_item, grupos):
        filterexpression = {"KeyConditionExpression": Key(self.key).eq(id_item)}
        if grupos:
            filterexpression["FilterExpression"] = Attr("grupo").is_in(grupos)
        response = self.client.query(**filterexpression)
        return response["Items"]

    @exception_handler
    def buscar(self, scan_kwargs, grupos):
        done = False
        results = None
        start_key = None
        if grupos:
            scan_kwargs["ScanFilter"]["grupo"] = {"AttributeValueList": grupos, "ComparisonOperator": "IN"}
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.client.scan(**scan_kwargs)
            results = response.get("Items", [])
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None
        if results:
            results = sorted(results, key=lambda k: k["data_cadastro"], reverse=True)
        return results

    def busca_por_argumento(self, argumento, valor, grupos):
        scan_kwargs = {"ScanFilter": {argumento: {"AttributeValueList": [valor], "ComparisonOperator": "CONTAINS"}}}
        return self.buscar(scan_kwargs=scan_kwargs, grupos=grupos)

    def busca_todos(self, grupos):
        return self.buscar(scan_kwargs={"ScanFilter": {}}, grupos=grupos)

    def busca_por_data(self, inicio, fim, grupos):
        scan_kwargs = {
            "ScanFilter": {
                "data_inicio": {"AttributeValueList": [inicio], "ComparisonOperator": "GE"},
                "data_fim": {"AttributeValueList": [fim], "ComparisonOperator": "LE"},
            }
        }
        return self.buscar(scan_kwargs=scan_kwargs, grupos=grupos)

    @exception_handler
    def deleta_item(self, id_item, grupos):
        response = self.client.delete_item(Key={self.key: id_item}, ReturnValues="ALL_OLD")
        return True

    @exception_handler
    def atualiza_item(self, id_item, dados):
        dados = json.loads(dados)
        arguments = {"Key": {self.key: id_item}, "AttributeUpdates": {}, "ReturnValues": "NONE"}
        for key in dados.keys():
            arguments["AttributeUpdates"][key] = {"Value": dados[key], "Action": "PUT"}
        response = self.client.update_item(**arguments)
        return True
