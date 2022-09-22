# Azure Function App

This repository holds a simple example of using an Azure Function App, written in Python. 

This simple REST API can be run using Visual Studio Code or directly in Azure. 

# Contents

- [Repository Content](#repository-content)
- [Architecture](#architecture)
- [Exposed Endpoints](#endpoints)
- [Notes](#execution-notes)

<hr>


## Repository Content

- Directory __functionapp__ contains the code of the Python based Function App.
- Directory __postman__ contains postman scripts to test the function app locally OR when deployed. 

<hr> 

## Architecture

This demo is made up of a small handful of services in Azure. Specifically

- An Azure Application Service Plan to host your Function App.
- An Azure Function App that hosts the actual API, with a service identity defined.
- [Optional] Application insights and storage if configured when you deploy your function app. 
- Azure Storage Account in which to host the storage table that the API will read/write to. Note that you must also include the service identity of the function app as a contributor to this resource directly. 

![Architecture](./images/architecture.jpg)

<hr> 

## Endpoints
Currently the exposed endpoints of the function application are as follows. 

|Endpoint|Action|Description|
|---|---|---|
|https:..../api/info|GET|Retrieve basic information about the service.|
|https:..../api/users?user_id=XXX|GET|Retrieve information about a single user.|
|https:..../api/users|GET|Retrieve basic information about all users.|
|https:..../api/users?user_id=XXX|DELETE|Delete a single user.|
|https:..../api/users|POST|Add or update a user.|


<hr> 

### Execution Notes
If running locally, ensure that ...\functionapp\utils\identity\credcollector.py:12 is using AzureCliCredential. Switch back to DefaultAzureCredential when deploying to your function app. 

Note that this simple demo does NOT use any API keys or other security on the exposed endpoints. 

Security between the app and the storage account is managed via the system identity of the function app.