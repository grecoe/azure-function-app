import logging
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.mgmt.storage import StorageManagementClient

# https://learn.microsoft.com/en-us/samples/azure-samples/storage-python-manage/storage-python-manage/

class CredCollector:
    RETRIEVED_STORAGE_KEYS:dict = None

    def __init__(self):
        # Use AzureCliCredentials when local, DefaultAzureCredentials when in an App Service
        self.execution_credential = DefaultAzureCredential() #AzureCliCredential()

    def get_storage_key(self, account_name:str, resource_group:str, subscription_id:str) -> dict:

        if (CredCollector.RETRIEVED_STORAGE_KEYS and 
            account_name in CredCollector.RETRIEVED_STORAGE_KEYS and
            len(CredCollector.RETRIEVED_STORAGE_KEYS[account_name]) > 0):
            logging.info("Cached storage credentials being returned.")
            return CredCollector.RETRIEVED_STORAGE_KEYS[account_name]


        logging.info("No cahced storage credentials present, retrieving.")
        storage_client = StorageManagementClient(self.execution_credential, subscription_id)
        keys = storage_client.storage_accounts.list_keys(resource_group, account_name)
        key_dict = {k.key_name : k.value for k in keys.keys}

        CredCollector.RETRIEVED_STORAGE_KEYS = {}
        CredCollector.RETRIEVED_STORAGE_KEYS[account_name] = key_dict

        return CredCollector.RETRIEVED_STORAGE_KEYS[account_name]