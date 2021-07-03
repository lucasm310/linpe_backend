from botocore.exceptions import ClientError
from fastapi import HTTPException

from ..helpers.dynamodb import DynamoDB

class EventosDatabase(DynamoDB):
    def __init__(self, table):
        super().__init__(table)
        self.nome_api = "evento"
        self.key = "eventosID"

    def busca_por_data(self, inicio, fim, grupos):
        done = False
        results = None
        start_key = None
        scan_kwargs = {
            "ScanFilter":{
                "data_inicio": {
                    "AttributeValueList": [inicio],
                    "ComparisonOperator": "GE"
                },
                "data_fim": {
                    "AttributeValueList": [fim],
                    "ComparisonOperator": "LE"
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
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})
        else:
            if not results:
                raise HTTPException(status_code=404, detail={"status":"falha", "mensagem":f"{self.nome_api} nao encontrado"})
            else:
                return {"status": "sucesso", "resultados": results}

    def deleta_item(self, id_item, grupos):
        response = self.client.delete_item(
            Key={
                self.key: id_item
            },
            ReturnValues="ALL_OLD"
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and "Attributes" in response.keys():
            return {"status": "sucesso"}
        else:
            raise HTTPException(
                status_code=response['ResponseMetadata']['HTTPStatusCode'], 
                detail={"status":"falha", "message":"erro ao deletar evento"}
            )
