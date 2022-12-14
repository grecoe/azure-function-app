import typing
import datetime
from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.data.tables._entity import EntityProperty
from azure.data.tables._deserialize import TablesEntityDatetime
from .tableentities import TableEntry


class AzureTableStoreUtil:
    CONN_STR = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix=core.windows.net"

    def __init__(self, account_name:str, account_key:str):
        self.connection_string = AzureTableStoreUtil.CONN_STR.format(
            account_name,
            account_key
        )

    def search_with_query(self, table_name:str, query:str, klass) -> typing.List[TableEntry]:
        return_records = []
        with self._get_table_client(table_name) as table_client:
    
            results = table_client.query_entities(query)
            for result in results:
                entity_record = {}
                
                for key in result:
                    value = result[key]

                    if isinstance(result[key], EntityProperty): 
                        value = result[key].value
                    if isinstance(result[key], TablesEntityDatetime):
                        value = datetime.datetime.fromisoformat(str(result[key]))

                    entity_record[key] = value
                
                record = TableEntry.from_entity(table_name, entity_record, klass)
                return_records.append(record)
        
        return return_records

    def search_table(self, table_name:str, start: datetime, end: datetime = None) -> typing.List[typing.Dict[str, typing.Any]]:
        """
        Search the storage table for records in a time window.

        If end is not provided, get all records before start, otherwise
        all records between start and end.

        Params:
        table_name - required: Yes  Storage Table to search
        start -      required: Yes  When end is none = all records before this time
                                    When end is not none = start of window
        end -        required: No   Identifies end of window scan

        Returns:
        List of dictionaries, each represents a record found
        """
        return_records = []
        with self._get_table_client(table_name) as table_client:
            query_filter = AzureTableStoreUtil._get_query_filter(start, end)
    
            results = table_client.query_entities(query_filter)
            for result in results:
                entity_record = {}
                
                for key in result:
                    value = result[key]

                    if isinstance(result[key], EntityProperty): 
                        value = result[key].value
                    if isinstance(result[key], TablesEntityDatetime):
                        value = datetime.datetime.fromisoformat(str(result[key]))

                    entity_record[key] = value
                
                return_records.append(entity_record)
        
        return return_records

    def delete_records(self, table_name:str, records:typing.List[typing.Tuple[str,str]]) -> None:
        """
        Delete records from a table
        
        Parameters:
        table_name - name of table to remove. 
        records - List of tuples that are (RowKey,PartitionKey)
        """
        with self._get_table_client(table_name) as table_client:
            for pair in records:
                table_client.delete_entity(
                    row_key=pair[0], 
                    partition_key=pair[1]
                    )

    def add_record(self, table_name:str, entity:dict):
        """
        Add a record to a table

        Parameters:
        table_name - Name of table to add to
        entity - Dictionary of non list/dict data
        """
        with self._create_table(table_name) as log_table:
            try:
                resp = log_table.create_entity(entity=entity)
            except Exception as ex:
                print("Entity already exists?")
                print(str(ex))

    def update_record(self,  table_name:str, entity:dict):
        """
        Add a record to a table

        Parameters:
        table_name - Name of table to add to
        entity - Dictionary of non list/dict data
        """
        with self._create_table(table_name) as log_table:
            try:
                resp = log_table.update_entity(entity=entity, mode=UpdateMode.REPLACE)
            except Exception as ex:
                print("Entity already exists?")
                print(str(ex))

    @staticmethod
    def _get_query_filter(start: datetime, end: datetime) -> str:
        """If no end date we are looking for anything BEFORE start, 
        otherwise get records between times
        
        NOTE: This was done with an IOT Hub in mind so the time field
        EventProcessedUtcTime comes from the IOT Hub, this will need
        to change to whatever time field you add to your table. 
        """
        query_filter = None
        if end is not None:
            query_filter = "EventProcessedUtcTime ge datetime'{}' and EventProcessedUtcTime lt datetime'{}'".format(
                start.isoformat(),
                end.isoformat()
            )
        else:
            query_filter = "EventProcessedUtcTime lt datetime'{}'".format(
                start.isoformat()
            )

        return query_filter

    def _create_table(self, table_name:str) -> TableClient:
        """
        Ensure a table exists in the table storage 
        """
        with TableClient.from_connection_string(conn_str=self.connection_string, table_name=table_name) as table_client:
            try:
                table_client.create_table()
            except Exception as ex:
                pass
                
        return self._get_table_client(table_name)

    def _get_table_client(self, table_name: str) ->TableClient:
        """Searches for and returns a table client for the specified
        table in this account. If not found throws an exception."""
        return_client = None

        with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service:
            name_filter = "TableName eq '{}'".format(table_name)
            queried_tables = table_service.query_tables(name_filter)

            found_tables = []
            for table in queried_tables:
                # Have to do this as its an Item_Paged object
                if table.name == table_name:
                    found_tables.append(table)
                    break 
        
            if found_tables and len(found_tables) == 1:
                return_client = TableClient.from_connection_string(conn_str=self.connection_string, table_name=table_name)
            else:
                raise Exception("Table {} not found".format(table_name))

        return return_client                