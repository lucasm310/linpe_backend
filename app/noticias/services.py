from fastapi import HTTPException

from ..helpers.dynamodb import DynamoDB

class NoticiasDatabase(DynamoDB):
    def __init__(self, table):
        super().__init__(table)
        self.nome_api = "noticia"
        self.key = "noticiaID"

    def deleta_item(self, id_item, grupos):
        response = self.client.delete_item(
            Key={
                'noticiaID': id_item
            },
            ReturnValues="ALL_OLD"
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and "Attributes" in response.keys():
            return {"status": "sucesso"}
        else:
            raise HTTPException(
                status_code=response['ResponseMetadata']['HTTPStatusCode'], 
                detail={"status":"falha", "message":"erro ao deletar noticia"}
            )

