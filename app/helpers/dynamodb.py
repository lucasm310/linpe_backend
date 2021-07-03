import json
from os import environ

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from fastapi import HTTPException
from dotenv import load_dotenv

from .logger import get_logger

load_dotenv()

class DynamoDB:
    def __init__(self, table):
        self.table = table
        self.client = self.get_client()
        self.nome_api = None
        self.key = None
    
    def get_client(self):
        try: 
            boto3.setup_default_session(region_name=environ.get("AWS_REGION"))
            dynamodb = boto3.resource('dynamodb')
            client = dynamodb.Table(self.table)
            return client
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "message":"erro ao conectar client", "debug":e})
        
    def cria_item(self, dados):
        dados = json.loads(dados)
        try:
            response = self.client.put_item(
                Item=dados
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"status":"sucesso", self.key: dados[self.key]}
            else:
                message = f"erro ao criar {self.name_api}"
                raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except ClientError as e:
            message = f"erro ao criar {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"erro ao criar {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
    
    def busca_por_id(self, id_item, grupos):
        filterexpression = {
            "KeyConditionExpression": Key(self.key).eq(id_item)
        }
        if grupos:
            filterexpression["FilterExpression"] = Attr('grupo').is_in(grupos)
            
        try:
            response = self.client.query(**filterexpression)
        except ClientError as e:
            message = f"erro buscar por ID {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"erro buscar por ID {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        if len(response['Items']) == 0:
            message = f"{self.nome_api} nao encontrado"
            raise HTTPException(status_code=404, detail={"status":"falha", "mensagem":message})
        else:
            return {"status": "sucesso", "resultados": response['Items']}
        
    def busca_por_argumento(self, argumento, valor, grupos):
        done = False
        results = None
        start_key = None
        scan_kwargs = {
            "ScanFilter":{
                argumento: {
                    "AttributeValueList": [valor],
                    "ComparisonOperator": "CONTAINS"
                }
            }
        }
        if grupos:
            scan_kwargs["ScanFilter"]["grupo"] = {
                "AttributeValueList": grupos,
                "ComparisonOperator": "IN"
            }
        try: 
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                response = self.client.scan(**scan_kwargs)
                results = response.get('Items', [])
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as e:
            message = f"erro ao buscar por argumentos {argumento}-{valor} - {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"erro ao buscar por argumentos {argumento}-{valor} - {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        else:
            if not results:
                message = f"{self.nome_api} nao encontrado"
                raise HTTPException(status_code=404, detail={"status":"falha", "mensagem":message})
            else:
                return {"status": "sucesso", "resultados": results}
    
    def busca_todos(self, grupos):
        done = False
        results = None
        scanfilter = {}
        if grupos:
            scanfilter["ScanFilter"] = {
                "grupo":{
                    "AttributeValueList": grupos,
                    "ComparisonOperator": "IN"
                }
            }
        try:
            while not done:
                response = self.client.scan(**scanfilter)
                results = response.get('Items', [])
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
        except ClientError as e:
            message = f"falha ao buscar registros {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"falha ao buscar registros {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})
        else:
            if not results:
                message = f"{self.nome_api} nao encontrado"
                raise HTTPException(status_code=404, detail={"status":"falha", "mensagem":message})
            else:
                results = sorted(results, key=lambda k: k['data_cadastro'], reverse=True)
                return {"status": "sucesso", "resultados": results}
    
    def deleta_item(self, id_item, grupos):
        raise NotImplementedError
    
    def atualiza_item(self, id_item, dados):
        arguments = {
            "Key": {
                self.key: id_item
            },
            "AttributeUpdates": {},
            "ReturnValues": "NONE"
        }
        for key in dados.keys():
            arguments["AttributeUpdates"][key] = {
                "Value": dados[key],
                "Action": "PUT"
            }
        try:
            response = self.client.update_item(**arguments)
        except ClientError as e:
            message = f"falha ao atualizar registro {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"falha ao atualizar registro {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        else:
            return {"status": "sucesso"}

        
        