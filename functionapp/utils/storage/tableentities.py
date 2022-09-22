import datetime
import uuid
import json
import typing

class TableEntry:
    def __init__(self, table_name:str, partition_key:str):
        self.table_name = table_name
        self.RowKey = datetime.datetime.utcnow().isoformat()
        self.PartitionKey = partition_key

    def get_entity(self):
        """
        Entity is everyting in self.__dict__ EXCEPT the 
        table name.
        """
        entity = {}
        for prop in self.__dict__:
            if prop != 'table_name':
                if isinstance(self.__dict__[prop], dict) or isinstance(self.__dict__[prop], list):
                    entity[prop] = json.dumps(self.__dict__[prop])
                else:    
                    entity[prop] = self.__dict__[prop]

        return entity

    def get_mutable_fields(self, restrict:typing.List[str]):
        mutable = []
        for prop in self.__dict__:
            if prop != "table_name" and prop != "RowKey" and prop != "PartitionKey" and prop not in restrict:
                mutable.append(prop)
        return mutable

    @staticmethod
    def get_partition_query(partition:str):
        return "PartitionKey eq '{}'".format(partition)

    @staticmethod
    def from_entity(table_name:str, entity:dict, klass) -> object:
        partition = entity["PartitionKey"]

        return_object = klass(table_name, partition)

        for prop in entity:
            if hasattr(return_object, prop):
                orig = getattr(return_object, prop)
                if isinstance(orig, dict) or isinstance(orig, list):
                    setattr(return_object, prop, json.loads(entity[prop]))
                else:
                    setattr(return_object, prop, entity[prop])
            else:
                setattr(return_object, prop, entity[prop])
        
        return return_object

class UserEntry(TableEntry):
    def __init__(self, table_name:str, partition_key:str):
        super().__init__(table_name, partition_key)
        self.user_id = str(uuid.uuid4())
        self.surname = None
        self.firstname = None
        self.devices = []
        self.choices = {}

    def get_mutable_fields(self):
        return super().get_mutable_fields(["user_id"])
        
    @staticmethod
    def get_id_query(user_id:str):
        return "user_id eq '{}'".format(user_id)