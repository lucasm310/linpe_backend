from botocore.exceptions import ClientError

from app.helpers.logger import get_logger


def exception_handler(func):
    log = get_logger()

    def handler(*args, **kwargs):
        try:
            return AWSResponse(func(*args, **kwargs), True)
        except ClientError as error:
            log.critical(f'erro={error.response["Error"]["Message"]}')
            return AWSResponse(False, False, "Erro Banco de Dados")
        except Exception as e:
            log.critical(f"erro={type(e)}-{e}")
            return AWSResponse(False, False, "Erro interno")

    return handler


class AWSResponse:
    def __init__(self, response, status, error_message=""):
        self.response = response
        self.status = status
        self.error_message = error_message
