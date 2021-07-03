from datetime import datetime

from botocore.exceptions import ClientError
from fastapi import HTTPException

from ..helpers.cognito import Cognito

class Usuarios(Cognito):
    def __init__(self):
        super().__init__()

    def busca_user_grupo(self, username):
        try:
            grupos_cognito = self.client.admin_list_groups_for_user(UserPoolId=self.userpoolid, Username=username)
            grupos = ['geral']
            for grp in grupos_cognito['Groups']:
                if grp['GroupName'] == 'ligantes':
                    grupos.append('ligantes')
                elif grp['GroupName'] == 'diretoria':
                    grupos.append('diretoria')
            return grupos
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})

    def busca_todos(self):
        lista_usuarios = []
        try:
            usuarios = self.client.list_users(UserPoolId=self.userpoolid)
            usuarios = usuarios['Users']
            for user in usuarios:
                usuario = {
                    'username': user['Username'],
                    'grupos': self.busca_user_grupo(username=user['Username']),
                    'email': False,
                    'nome': False,
                    'data_nascimento': False,
                    'curso': False,
                    'telefone': False,
                    'nivel': False,
                    'status': 'Não Confirmado'
                }
                for attr in user['Attributes']:
                    if attr['Name'] == 'name':
                        usuario['nome'] = attr['Value']
                    elif attr['Name'] == 'email':
                        usuario['email'] = attr['Value']
                    elif attr['Name'] == 'custom:nivel':
                        usuario['nivel'] = attr['Value']
                    elif attr['Name'] == 'phone_number':
                        usuario['telefone'] = attr['Value']
                    elif attr['Name'] == 'birthdate':
                        usuario['data_nascimento'] = datetime.strptime(attr['Value'], '%Y-%m-%d')
                    elif attr['Name'] == 'custom:curso':
                        usuario['curso'] = attr['Value']
                if user['UserStatus'] in ['EXTERNAL_PROVIDER', 'CONFIRMED']:
                    usuario['status'] = 'Confirmado'
                lista_usuarios.append(usuario)
            results = sorted(lista_usuarios, key=lambda k: k['nome'])
            return {"status": "sucesso", "resultados":results}
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})
    
    def busca_user(self, username):
        try:
            usuario = {
                'grupos': self.busca_user_grupo(username=username)
            }
            user = self.client.admin_get_user(UserPoolId=self.userpoolid, Username=username)
            usuario['username'] = user['Username']
            for attr in user['UserAttributes']:
                if attr['Name'] == 'name':
                    usuario['nome'] = attr['Value']
                elif attr['Name'] == 'email':
                    usuario['email'] = attr['Value']
            return  {"status": "sucesso", "usuario":usuario}
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})

    def altera(self, username, attr, value):
        try:
            response = self.client.admin_update_user_attributes(
                UserPoolId=self.userpoolid,
                Username=username,
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

    def add_grupo(self, username, grupo):
        try:
            response = self.client.admin_add_user_to_group(
                UserPoolId=self.userpoolid,
                Username=username,
                GroupName=grupo
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"status":"sucesso", 'message':'usuario alterado'}
            else:
                raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro ao criar {self.name_api}"})
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})

    def remove_grupo(self, username, grupo):
        try:
            response = self.client.admin_remove_user_from_group(
                UserPoolId=self.userpoolid,
                Username=username,
                GroupName=grupo
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"status":"sucesso", 'message':'usuario alterado'}
            else:
                raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro ao criar {self.name_api}"})
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})

    def deleta(self,username):
        try:
            response = self.client.admin_delete_user(
                UserPoolId=self.userpoolid,
                Username=username,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"status":"sucesso", 'message':'usuario deletado'}
            else:
                raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"erro ao criar {self.name_api}"})
        except ClientError as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":e.response['Error']['Message']})
        except Exception as e:
            raise HTTPException(status_code=500, detail={"status":"falha", "mensagem":f"{e}"})