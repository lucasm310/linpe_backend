from botocore.exceptions import ClientError
from fastapi import HTTPException

from ..helpers.cognito import Cognito

class Perfil(Cognito):
    def __init__(self):
        super().__init__()
    
    def get_perfil(self, token):
        try:
            data = {}
            user = self.client.get_user(AccessToken=token)
            data['username'] = user['Username']
            for attr in user['UserAttributes']:
                if attr['Name'] == 'name':
                    data['nome'] = attr['Value']
                elif attr['Name'] == 'email':
                    data['email'] = attr['Value']
            return  {"status": "sucesso", "usuario":data}
        except ClientError as e:
            message = f"erro ao buscar dados perfil {e.response['Error']['Message']}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})
        except Exception as e:
            message = f"erro ao buscar dados perfil {e}"
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":message})

    def altera_perfil(self, token, attr, value):
        try:
            response = self.client.update_user_attributes(
                AccessToken=token,
                UserAttributes=[
                    {
                        'Name': attr,
                        'Value': value
                    }
                ]
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"status":"sucesso", 'message':'usuario alterado'}
            else:
                raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro ao criar {self.name_api}"})
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})
