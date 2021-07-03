from os import environ

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from dotenv import load_dotenv

from ..helpers.dynamodb import DynamoDB

load_dotenv()
BUCKET_NAME = environ.get("DOCUMENTOS_BUCKET")


class DocumentosDatabase(DynamoDB):
    def __init__(self, table):
        super().__init__(table)
        self.nome_api = "documento"
        self.key = "documentoID"

    def _create_presigned_url(self, arquivo):
        bucket_name = BUCKET_NAME
        expiration = 3600
        s3_client = boto3.client('s3')
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': arquivo
                },
                ExpiresIn=expiration
            )
            return {"status": "sucesso", "url": response}
        except ClientError as e:
            message = f"erro ao gerar url doc {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status": "falha", "mensagem": message})

    def busca_documento_id(self, id_documento, grupos, tipo, for_delete=False):
        resultado = self.busca_por_id(id_item=id_documento, grupos=grupos)
        if for_delete:
            return resultado["resultados"]
        else:
            for doc in resultado["resultados"]:
                if tipo and (doc["tipo"] == tipo or tipo == "all"):
                    if "nome_file" in doc.keys() and doc["nome_file"] != "":
                        url = self._create_presigned_url(arquivo=doc["nome_file"])
                        doc["url"] = url
            return {"status": "sucesso", "resultados": resultado["resultados"]}

    def deleta_item(self, id_item, grupos):
        try:
            documento = self.busca_documento_id(
                id_documento=id_item, grupos=grupos, tipo="all", for_delete=True)
            if len(documento) == 1:
                response = self.client.delete_item(
                    Key={
                        'documentoID': id_item,
                        'data_cadastro': documento[0]['data_cadastro'],
                    },
                    ReturnValues="ALL_OLD"
                )
                if response['ResponseMetadata']['HTTPStatusCode'] == 200 and "Attributes" in response.keys():
                    return {"status": "sucesso", "message": "documento deletada"}
                else:
                    raise HTTPException(
                        status_code=response['ResponseMetadata']['HTTPStatusCode'],
                        detail={"status": "falha", "message": "erro ao deletar documento"}
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail={"status": "falha", "message": "nao foi encontrado documento"}
                )
        except ClientError as e:
            message = f"erro ao deletar documento {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status": "falha", "message": message})

    def atualiza_item(self, id_item, dados, grupos):
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
            documento = self.busca_documento_id(
                id_documento=id_item, grupos=grupos, tipo="all", for_delete=True)
            if len(documento) == 1:
                arguments["Key"]["data_cadastro"] = documento[0]['data_cadastro']
                response = self.client.update_item(**arguments)
            else:
                raise HTTPException(
                    status_code=404,
                    detail={"status": "falha",
                            "message": "nao foi encontrado documento"}
                )
        except ClientError as e:
            message = f"erro ao atualizar documento {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status": "falha", "mensagem": message})
        except Exception as e:
            message = f"erro ao atualizar documento {e}"
            raise HTTPException(status_code=500, detail={"status": "falha", "mensagem": message})
        else:
            return {"status": "sucesso"}
