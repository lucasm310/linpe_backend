import json
from os import environ
from datetime import datetime

import boto3
from dotenv import load_dotenv

from app.helpers.base_aws import exception_handler

load_dotenv()


class Cognito:
    def __init__(self):
        self.client = None
        self.userpoolid = environ.get("USERPOOL_ID")
        self.grupos = ["geral", "ligantes", "diretoria"]
        response = self.get_client()
        if response.status is True:
            self.client = response.response
        else:
            raise Exception("erro conectar ao cognito")

    @exception_handler
    def get_client(self):
        boto3.setup_default_session(region_name=environ.get("AWS_REGION"))
        client = boto3.client("cognito-idp")
        return client

    @exception_handler
    def get_perfil(self, token):
        data = {}
        user = self.client.get_user(AccessToken=token)
        data["username"] = user["Username"]
        for attr in user["UserAttributes"]:
            if attr["Name"] == "name":
                data["nome"] = attr["Value"]
            elif attr["Name"] == "email":
                data["email"] = attr["Value"]
        return data

    @exception_handler
    def altera_perfil(self, token, attr, value):
        response = self.client.update_user_attributes(AccessToken=token, UserAttributes=[{"Name": attr, "Value": value}])
        return True

    @exception_handler
    def busca_user_grupo(self, username):
        grupos_cognito = self.client.admin_list_groups_for_user(UserPoolId=self.userpoolid, Username=username)
        grupos = ["geral"]
        for grp in grupos_cognito["Groups"]:
            if grp["GroupName"] == "ligantes":
                grupos.append("ligantes")
            elif grp["GroupName"] == "diretoria":
                grupos.append("diretoria")
        return grupos

    @exception_handler
    def busca_todos_usuarios(self):
        lista_usuarios = []
        usuarios = self.client.list_users(UserPoolId=self.userpoolid)
        usuarios = usuarios["Users"]
        for user in usuarios:
            grupos = self.busca_user_grupo(username=user["Username"])
            if grupos.status is False:
                raise Exception(grupos.error_message)
            usuario = {
                "username": user["Username"],
                "grupos": grupos.response,
                "email": False,
                "nome": False,
                "data_nascimento": False,
                "curso": False,
                "telefone": False,
                "nivel": False,
                "status": "Não Confirmado",
            }
            for attr in user["Attributes"]:
                if attr["Name"] == "name":
                    usuario["nome"] = attr["Value"]
                elif attr["Name"] == "email":
                    usuario["email"] = attr["Value"]
                elif attr["Name"] == "custom:nivel":
                    usuario["nivel"] = attr["Value"]
                elif attr["Name"] == "phone_number":
                    usuario["telefone"] = attr["Value"]
                elif attr["Name"] == "birthdate":
                    usuario["data_nascimento"] = datetime.strptime(attr["Value"], "%Y-%m-%d")
                elif attr["Name"] == "custom:curso":
                    usuario["curso"] = attr["Value"]
            if user["UserStatus"] in ["EXTERNAL_PROVIDER", "CONFIRMED"]:
                usuario["status"] = "Confirmado"
            lista_usuarios.append(usuario)
        results = sorted(lista_usuarios, key=lambda k: k["nome"])
        return results

    @exception_handler
    def busca_usuario(self, username):
        grupos = self.busca_user_grupo(username=username)
        if grupos.status is False:
            raise Exception(grupos.error_message)
        user = self.client.admin_get_user(UserPoolId=self.userpoolid, Username=username)
        usuario = {"grupos": grupos.response}
        usuario["username"] = user["Username"]
        for attr in user["UserAttributes"]:
            if attr["Name"] == "name":
                usuario["nome"] = attr["Value"]
            elif attr["Name"] == "email":
                usuario["email"] = attr["Value"]
            elif attr["Name"] == "custom:nivel":
                usuario["nivel"] = attr["Value"]
            elif attr["Name"] == "phone_number":
                usuario["telefone"] = attr["Value"]
            elif attr["Name"] == "birthdate":
                usuario["data_nascimento"] = datetime.strptime(attr["Value"], "%Y-%m-%d")
            elif attr["Name"] == "custom:curso":
                usuario["curso"] = attr["Value"]
        return usuario

    @exception_handler
    def altera_usuario(self, username, attr, value):
        response = self.client.admin_update_user_attributes(
            UserPoolId=self.userpoolid, Username=username, UserAttributes=[{"Name": attr, "Value": value}]
        )
        return response

    @exception_handler
    def add_grupo(self, username, grupo):
        response = self.client.admin_add_user_to_group(UserPoolId=self.userpoolid, Username=username, GroupName=grupo)
        return response

    @exception_handler
    def remove_grupo(self, username, grupo):
        response = self.client.admin_remove_user_from_group(UserPoolId=self.userpoolid, Username=username, GroupName=grupo)
        return response

    @exception_handler
    def deleta_usuario(self, username):
        response = self.client.admin_delete_user(
            UserPoolId=self.userpoolid,
            Username=username,
        )
        return response
