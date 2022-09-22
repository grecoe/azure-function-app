import os
from .identity.credcollector import CredCollector

class Configuration:

    STORAGE_ACCOUNT = "NOTIFICATION_RESOURCE" 
    STORAGE_GROUP = "NOTIFICATION_RESOURCE_GROUP"
    STORAGE_SUB = "NOTIFICATION_RESOURCE_SUB"
    STORAGE_KEY = "NOTIFICATION_RESOURCE_KEY" 
    RECORD_TABLE = "RECORD_TABLE"
    USER_TABLE_PARTITION = "USER_TABLE_PARTITION"
    USER_QUEUE = "USER_QUEUE"

    def __init__(self):
        self.user_queue = os.environ.get(Configuration.USER_QUEUE)
        self.table_name = os.environ.get(Configuration.RECORD_TABLE)
        self.user_partition = os.environ.get(Configuration.USER_TABLE_PARTITION)

        self.storage_account = os.environ.get(Configuration.STORAGE_ACCOUNT)
        self.storage_account_group = os.environ.get(Configuration.STORAGE_GROUP)
        self.storage_account_sub = os.environ.get(Configuration.STORAGE_SUB)

        cred_collector = CredCollector()
        storage_keys = cred_collector.get_storage_key(
            self.storage_account, 
            self.storage_account_group,
            self.storage_account_sub
        )

        if "key1" not in storage_keys:
            raise Exception("Storage keys not available, check access to {}".format(self.storage_account))
        
        self.storage_key = storage_keys["key1"]

