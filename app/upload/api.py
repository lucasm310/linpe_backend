from typing import Optional
from uuid import UUID, uuid4
from os import environ

import boto3
from boto3.dynamodb.conditions import Key, Attr
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from dotenv import load_dotenv

from app.auth.auth_barear import JWTBearer
from ..helpers.helpers import get_groups

router = APIRouter()
load_dotenv()
BUCKET_NAME = environ.get("DOCUMENTOS_BUCKET")

@router.post("/", status_code=201)
async def post(file: UploadFile = File(...), documento_id: Optional[str] = Header(None, convert_underscores=False), user: dict = Depends(JWTBearer())):
    grupos = get_groups(user['cognito:groups'])
    if 'diretoria' in grupos:
        try:
            dynamodb = boto3.resource('dynamodb')
            client = dynamodb.Table(environ.get("DOCUMENTOS_TABLE"))
            response = client.query(
                KeyConditionExpression=Key('documentoID').eq(documento_id),
                FilterExpression=Attr('grupo').is_in(grupos)
            )
            doc = response['Items']
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro buscar documento {e}"})
        else:
            if len(doc) != 1:
                raise HTTPException(status_code=404, detail={"status":"falha", "mensagem":"documento nao encontrado"})

        try:
            s3 = boto3.client('s3')
            file_extension = file.filename.split('.')[-1]
            file_path = f'{uuid4()}.{file_extension}'
            s3_response = s3.put_object(Bucket=BUCKET_NAME, Key=file_path, Body=file.file)
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro ao fazer upload s3 {e}"})
        try:
            dynamodb = boto3.client('dynamodb',environ.get("AWS_REGION"))
            a = dynamodb.update_item(
                TableName=environ.get("DOCUMENTOS_TABLE"),
                Key={
                    'documentoID': {'S':documento_id},
                    'data_cadastro':  {'S':doc[0]['data_cadastro']}
                },
                UpdateExpression="set nome_file = :g",
                ExpressionAttributeValues={
                        ':g': {'S':file_path}
                    },
                ReturnValues="UPDATED_NEW"
            )
            return {"status":"sucesso", "mensagem":"upload ok"}
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"ao atualizar db {e}"})
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
