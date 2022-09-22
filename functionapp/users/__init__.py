import logging
import typing
import json
from urllib import request

import azure.functions as func
from ..utils.config import Configuration
from ..utils.storage.azuretable import AzureTableStoreUtil
from ..utils.storage.tableentities import UserEntry, TableEntry
from ..utils.identity.credcollector import CredCollector

def create_or_update_user(
    configuration:Configuration, 
    azure_storage_table:AzureTableStoreUtil, 
    request_body:dict ) -> func.HttpResponse:

    return_response = func.HttpResponse("User updated or created", status_code=201)

    if "user_id" in request_body:
        user_id = request_body["user_id"]
        logging.info("Updating user {}".format(user_id))

        users = azure_storage_table.search_with_query(
            configuration.table_name,
            UserEntry.get_id_query(user_id),
            UserEntry
        )

        if len(users) == 0:
            return_response = func.HttpResponse("User with id {} not found".format(user_id), status_code=404)
        elif len(users) > 1:
            return_response = func.HttpResponse(">1 user with id {}".format(user_id), status_code=400)
        else:
            updated_user = users[0]
            mutable_props = updated_user.get_mutable_fields()
            # Update the mutable props
            for prop in request_body:
                if prop in mutable_props:
                    setattr(updated_user, prop, request_body[prop])

            # Update the record
            azure_storage_table.update_record(configuration.table_name, updated_user.get_entity())
    else:
        logging.info("Creating new user")
        new_user = UserEntry(configuration.table_name, configuration.user_partition)
        mutable_props = new_user.get_mutable_fields()
        # Update the mutable props
        for prop in request_body:
            if prop in mutable_props:
                setattr(new_user, prop, request_body[prop])

        # Create the record
        azure_storage_table.add_record(configuration.table_name, new_user.get_entity())

    return return_response

def delete_user(
    configuration:Configuration, 
    azure_storage_table:AzureTableStoreUtil, 
    user_id:str ) -> func.HttpResponse:

    users:typing.List[UserEntry] = []

    users = azure_storage_table.search_with_query(
        configuration.table_name,
        UserEntry.get_id_query(user_id),
        UserEntry
    )

    return_response = func.HttpResponse("Deleted", status_code=200)
    if len(users) == 0:
        return_response = func.HttpResponse("User with id {} not found".format(user_id), status_code=404)
    elif len(users) > 1:
        return_response = func.HttpResponse(">1 user with id {}".format(user_id), status_code=400)
    else:
        delete_user = [(users[0].RowKey, users[0].PartitionKey)]
        azure_storage_table.delete_records(configuration.table_name, delete_user)
        logging.info("User {} deleted".format(users[0].user_id))

    return return_response

def get_users(
    configuration:Configuration, 
    azure_storage_table:AzureTableStoreUtil, 
    user_id:str ) -> func.HttpResponse:

    users:typing.List[UserEntry] = []

    if not user_id:
        logging.info("User query all users")
        users = azure_storage_table.search_with_query(
            configuration.table_name,
            TableEntry.get_partition_query(configuration.user_partition),
            UserEntry
        )
    else:
        logging.info("User query for {} user".format(user_id))
        users = azure_storage_table.search_with_query(
            configuration.table_name,
            UserEntry.get_id_query(user_id),
            UserEntry
        )

    if not len(users):
        return func.HttpResponse("User(s) not found",  status_code=404)
    
    results = []

    for user in users:
        u = {
            "firstname" : user.firstname, 
            "surname" : user.surname, 
            "user_id" : user.user_id
        }

        if len(users) == 1:
            u["choices"] = user.choices
            u["devices"] = user.devices
        
        results.append(u)

    return func.HttpResponse(json.dumps(results, indent=4), status_code=200)    


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get a user or list of users

    Param: user_id
        If present, gets one user by ID
        If not present return a list of users by
        {
            "FirstName" :""
            "LastName" : ""
            "UserId: ""
        }
    """
    logging.info('Python HTTP trigger function processed a request.')

    configuration:Configuration = None
    try:
        configuration = Configuration()
    except Exception as ex:
        return func.HttpResponse(str(ex), status_code=500)

    azure_storage_table = AzureTableStoreUtil(
        configuration.storage_account, 
        configuration.storage_key
    )


    user_id = req.params.get('user_id')
    req_body = None
    
    try:
        req_body = req.get_json()
    except Exception as ex:
        pass


    response:func.HttpResponse = None

    if req.method == "GET":
        response = get_users(configuration, azure_storage_table, user_id)
    elif req.method == "DELETE":
        if not user_id:
            response = func.HttpResponse("User ID is required", status_code=400)
        else:
            response = delete_user(configuration, azure_storage_table, user_id)
    elif req.method == "POST":
        if not req_body:
            response = func.HttpResponse("Request body is required", status_code=400)
        else:
            response = create_or_update_user(configuration, azure_storage_table, req_body)

    return response