import json
import platform
import azure.functions as func
from ..utils.config import Configuration

def main(req: func.HttpRequest) -> func.HttpResponse:

    config = Configuration()

    status = {
        "Platform" : platform.platform(), 
        "Language" : "Python",
        "Version" : "0.0.1",
        "Endpoints" : {
            "info" : "Information about this service",
            "users" : "List, Add, Update, Remove users "
        },
        "Storage Account" : config.storage_account, 
        "Valid Credentials" : isinstance(config.storage_key, str),
        "Storage Table" : config.table_name,
        "Storage Table Partitions" : [
            "users"
        ]
    }
     
    return func.HttpResponse(json.dumps(status, indent=4))
