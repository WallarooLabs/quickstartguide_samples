This tutorial and the assets can be downloaded as part of the [Wallaroo Tutorials repository](https://github.com/WallarooLabs/Wallaroo_Tutorials/blob/main/wallaroo-features/pipeline_api_log_tutorial_cv).

## Pipeline API Log Tutorial

This tutorial demonstrates Wallaroo Pipeline MLOps API for pipeline log retrieval for Computer Vision based models.

This tutorial will demonstrate how to:

1. Select or create a workspace, pipeline and upload the control model, and additional testing models.
1. Add a pipeline step with the champion model, then deploy the pipeline and perform sample inferences for computer vision detection.
2. Retrieve the logs via the Wallaroo MLOps API.  These steps will be simplified to only show the API log retrieval method.  See the [Wallaroo Documentation site](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-api-guide/) for full details.
3. Use the pipeline logs to display metadata data.
4. Undeploy the pipeline.

This tutorial provides the following:

* Models:
  * `models/yolov8n.onnx`: A pre-trained Yolov8n model.
* Data:
  * `data/dogbike.png`: A PNG image with a dog and bicycle.
  * `data/dogbike.df.json`: A pandas Record format JSON file of the PNG image converted to numpy array values for inference requests.

## Prerequisites

* A deployed Wallaroo instance
* The following Python libraries installed:
  * [`wallaroo`](https://pypi.org/project/wallaroo/): The Wallaroo SDK. Included with the Wallaroo JupyterHub service by default.

## Initial Steps

### Import libraries

The first step is to import the libraries needed for this notebook.

```python
import wallaroo
from wallaroo.object import EntityNotFoundError

import pyarrow as pa

from IPython.display import display

# used to display DataFrame information without truncating
from IPython.display import display
import pandas as pd
pd.set_option('display.max_colwidth', None)

import datetime
import requests
```

### Connect to the Wallaroo Instance

The first step is to connect to Wallaroo through the Wallaroo client.  The Python library is included in the Wallaroo install and available through the Jupyter Hub interface provided with your Wallaroo environment.

This is accomplished using the `wallaroo.Client()` command, which provides a URL to grant the SDK permission to your specific Wallaroo environment.  When displayed, enter the URL into a browser and confirm permissions.  Store the connection into a variable that can be referenced later.

If logging into the Wallaroo instance through the internal JupyterHub service, use `wl = wallaroo.Client()`.  If logging in externally, update the `wallarooPrefix` and `wallarooSuffix` variables with the proper DNS information.  For more information on Wallaroo Client settings, see the [Client Connection guide](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-client/).

```python
# Login through local Wallaroo instance

wl = wallaroo.Client()
```

## Wallaroo MLOps API URL

### API URL

The variable `APIURL` is used to specify the connection to the Wallaroo instance's MLOps API URL, and is composed of the Wallaroo DNS prefix and suffix.  For full details, see the [Wallaroo API Connection Guide
](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-api-guide/wallaroo-mlops-connection-guide/).

For this demonstration, the following Wallaroo SDK methods are used to generate the API authentication Bearer token, and the MLOps API URL.

For full details on connecting to a Wallaroo instance via MLOps API calls, see the [Wallaroo API Connection Guide](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-api-guide/wallaroo-mlops-connection-guide/).

These methods are:

* `wallaroo.client.auth_header()`: Returns the authorization Bearer token for a user authenticated through the Wallaroo SDK.
* `wallaroo.client.api_endpoint`: Returns the Wallaroo instance's api endpoint.

```python
display(wl.auth.auth_header())
display(wl.api_endpoint)
```

    {'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJzWThabWtGcm9VWDdDSzFiQjEyS1dwWGtaaUk2R01Gd1ZQUHduWmxxbkVRIn0.eyJleHAiOjE3MDMyNjYxOTIsImlhdCI6MTcwMzI2NjEzMiwiYXV0aF90aW1lIjoxNzAzMjY0OTgxLCJqdGkiOiI0NDdmNmU4YS02NTY0LTRhMDQtODBiYy03MDY1YjViMzM4NTQiLCJpc3MiOiJodHRwczovL2RvYy10ZXN0LmtleWNsb2FrLndhbGxhcm9vY29tbXVuaXR5Lm5pbmphL2F1dGgvcmVhbG1zL21hc3RlciIsImF1ZCI6WyJtYXN0ZXItcmVhbG0iLCJhY2NvdW50Il0sInN1YiI6ImNkOGZkMDYzLTYyZmItNDhkYy05NTg5LTFkZTFiMjlkOTZhNyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNkay1jbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiMTIxNTg0M2UtMThhNy00NzgyLWE0YjgtODQ4YjIyYWQxYzdmIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLW1hc3RlciIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJtYXN0ZXItcmVhbG0iOnsicm9sZXMiOlsibWFuYWdlLXVzZXJzIiwidmlldy11c2VycyIsInF1ZXJ5LWdyb3VwcyIsInF1ZXJ5LXVzZXJzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6InByb2ZpbGUgb3BlbmlkIGVtYWlsIiwic2lkIjoiMTIxNTg0M2UtMThhNy00NzgyLWE0YjgtODQ4YjIyYWQxYzdmIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLXVzZXItaWQiOiJjZDhmZDA2My02MmZiLTQ4ZGMtOTU4OS0xZGUxYjI5ZDk2YTciLCJ4LWhhc3VyYS1kZWZhdWx0LXJvbGUiOiJ1c2VyIiwieC1oYXN1cmEtYWxsb3dlZC1yb2xlcyI6WyJ1c2VyIl0sIngtaGFzdXJhLXVzZXItZ3JvdXBzIjoie30ifSwibmFtZSI6IkpvaG4gSGFuc2FyaWNrIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiam9obi5odW1tZWxAd2FsbGFyb28uYWkiLCJnaXZlbl9uYW1lIjoiSm9obiIsImZhbWlseV9uYW1lIjoiSGFuc2FyaWNrIiwiZW1haWwiOiJqb2huLmh1bW1lbEB3YWxsYXJvby5haSJ9.W4rshsGTfdHrQnfP03zDcKUJSTEXVHb6HGmci5wDjCSUmqVibauaifoPl1b9mC9XR384-mt9CTEoA4k9JR9YntGzVgifQ2FgSvFtLHaTMMdl1BYulmJmnG_1jxheU7bc0XcgaBpTTQprkVn_UNvipIQuTxIwSsRyJzCmTXofQ8MQB5M1UVz2EQij-w9PzNWUbgDQ0K4IueYFK3idF3VWZCrO3ETEQV-xqySc-GoOmS8IQHWgNBb_WD11SjBYj1wrISYj3PgBAalyCc-hxZKDbdtuWGjjjeexqkGr_aTc4DfxQS3VUki4k9pCJEi5riLeOf0eJvRRYT69GrLrIe7IIA'}

    'https://doc-test.api.wallarooexample.ai'

### Create Workspace

We will create a workspace to manage our pipeline and models.  The following variables will set the name of our sample workspace then set it as the current workspace.

* **IMPORTANT NOTE**:  Workspace names must be unique across the Wallaroo instance.  To verify unique names, the randomization code below is provided to allow the workspace name to be unique.  If this is not required, set `suffix` to `''`.

* References
  * [Wallaroo SDK Essentials Guide: Workspace Management](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-workspace/)

```python
import string
import random

# make a random 4 character suffix to prevent overwriting other user's workspaces
suffix= ''.join(random.choice(string.ascii_lowercase) for i in range(4))

suffix=''

workspace_name = f'log-api-cv-workspace{suffix}'
main_pipeline_name = 'log-api-cv'
model_name = 'yolov8n'
model_file_name = './models/yolov8n.onnx'
```

```python
def get_workspace(name, client):
    workspace = None
    for ws in client.list_workspaces():
        if ws.name() == name:
            workspace= ws
    if(workspace == None):
        workspace = client.create_workspace(name)
    return workspace
```

```python
workspace = get_workspace(workspace_name, wl)

wl.set_current_workspace(workspace)

workspace_id = workspace.id()
```

### Upload The Computer Vision Model

For our example, we will upload the Yolov8n model, and set the input field to `images`.

```python
# Upload Retrained Yolo8 Model 

yolov8_model = (wl.upload_model(model_name, 
                               model_file_name, 
                               framework=wallaroo.framework.Framework.ONNX)
                               .configure(tensor_fields=['images'],
                                          batch_config="single"
                                          )
                )
```

### Build the Pipeline

This pipeline is made to be an example of an existing situation where a model is deployed and being used for inferences in a production environment.  We'll call it `housepricepipeline`, set `housingcontrol` as a pipeline step, then run a few sample inferences.

```python
mainpipeline = wl.build_pipeline(main_pipeline_name)

# in case this pipeline was run before
mainpipeline.undeploy()
mainpipeline.clear()
mainpipeline.add_model_step(yolov8_model).deploy()
```

<table><tr><th>name</th> <td>log-api-cv</td></tr><tr><th>created</th> <td>2023-12-22 17:10:06.563220+00:00</td></tr><tr><th>last_updated</th> <td>2023-12-22 17:55:34.460452+00:00</td></tr><tr><th>deployed</th> <td>True</td></tr><tr><th>arch</th> <td>None</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>b1c6d8ea-0259-4a45-aca5-c065a2d59d2d, a8f0adef-5ab9-4695-95eb-e09c256b221c, d174e395-66b5-40bb-bec0-a689e597749f, 4db1d862-0c8d-4394-9009-8aee1324503c, ce598566-83f7-4983-a8e5-4fc779e2c008, b016fb58-d52e-46e1-afc4-31268f471077, 0bd75ecf-1923-42cf-b7e5-6593699465c0</td></tr><tr><th>steps</th> <td>api-sample-model</td></tr><tr><th>published</th> <td>False</td></tr></table>

### Testing

We'll pass in our DataFrame reference file as an inference request, noting the start and end times for our log retrieval.

```python
dataframe_start = datetime.datetime.now(datetime.timezone.utc)

# run as inference api

# Retrieve the token
headers = wl.auth.auth_header()

# set Content-Type type
headers['Content-Type']='application/json; format=pandas-records'

## Inference through external URL using dataframe

df = pd.read_json('./data/dogbike.df.json')
data = df.to_dict(orient="records")

# submit the request via POST, import as pandas DataFrame
response = pd.DataFrame.from_records(
    requests.post(
        mainpipeline._deployment._url(), 
        json=data, 
        headers=headers)
        .json()
    )
# just to account for any local versus server time discrepancy
import time
time.sleep(20)
dataframe_end = datetime.datetime.now(datetime.timezone.utc)

# run additional inferences outside the time frame

for i in range(10):
    # submit the request via POST, import as pandas DataFrame
    response = pd.DataFrame.from_records(
        requests.post(
            mainpipeline._deployment._url(), 
            json=data, 
            headers=headers)
            .json()
        )
```

### Get Pipeline Logs

Pipeline logs are retrieved through the Wallaroo MLOps API with the following request.

* **REQUEST URL**
  * `v1/api/pipelines/get_logs`
* **Headers**
  * **Accept**:
    * `application/json; format=pandas-records`: For the logs returned as pandas DataFrame
    * `application/vnd.apache.arrow.file`: for the logs returned as Apache Arrow
* **PARAMETERS**
  * **pipeline_name** (*String* *Required*): The name of the pipeline.
  * **workspace_id** (*Integer* *Required*): The numerical identifier of the workspace.
  * **cursor** (*String* *Optional*): Cursor returned with a previous page of results from a pipeline log request, used to retrieve the next page of information.
  * **order**  (*String* *Optional* Default: `Desc`): The order for log inserts returned.  Valid values are:
    * `Asc`: In chronological order of inserts.
    * `Desc`: In reverse chronological order of inserts.
  * **page_size** (*Integer* *Optional* Default: `1000`.): Max records per page.
  * **start_time** (*String* *Optional*): The start time of the period to retrieve logs for in RFC 3339 format for DateTime.  **Must** be combined with `end_time`.
  * **end_time** (*String* *Optional*): The end time of the period to retrieve logs for in RFC 3339 format for DateTime.  **Must** be combined with `start_time`. 
* **RETURNS**
  * The logs are returned by default as  `'application/json; format=pandas-records'` format.  To request the logs as Apache Arrow tables, set the submission header `Accept` to `application/vnd.apache.arrow.file`.
  * Headers:
    * x-iteration-cursor: Used to retrieve the next page of results.  This is not included if `x-iteration-status` is `All`.
    * x-iteration-status: Informs whether there are more records available outside of this log request parameters.
      * All: This page includes all logs available from this request.  If `x-iteration-status` is `All`, then `x-iteration-cursor` is not provided.
      * SchemaChange: A change in the log schema caused by actions such as pipeline version, etc.
      * RecordLimited: The number of records exceeded from the page size, more records can be requested as the next page.  There **may** be more records available to retrieve OR the record limit was reached for this request even if no more records are available in next cursor request.
      * ByteLimited: The number of records exceeded the pipeline log limit which is around 100K. 

### Get Pipeline Logs Example

For our example, we will retrieve the pipeline logs.  FIrst by specifying the date and time, then we will request the logs and continue to show them as long as the cursor has another log to display.  Because of the size of the input and outputs, most logs may be constrained by the `x-iteration-status` as `ByteLimited`.

```python
# retrieve the authorization token
headers = wl.auth.auth_header()

url = f"{wl.api_endpoint}/v1/api/pipelines/get_logs"

# Standard log retrieval

data = {
    'pipeline_name': main_pipeline_name,
    'workspace_id': workspace_id,
    'start_time': dataframe_start.isoformat(),
    'end_time': dataframe_end.isoformat()
}

response = requests.post(url, headers=headers, json=data)
standard_logs = pd.DataFrame.from_records(response.json())

display(len(standard_logs))
display(standard_logs.loc[:, ["time", "out"]])
```

    1

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1703267760538</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
  </tbody>
</table>

```python
# retrieve the authorization token
headers = wl.auth.auth_header()

url = f"{wl.api_endpoint}/v1/api/pipelines/get_logs"

# datetime set back one day to get more values

data = {
    'pipeline_name': main_pipeline_name,
    'workspace_id': workspace_id
}

response = requests.post(url, headers=headers, json=data)
standard_logs = pd.DataFrame.from_records(response.json())

display(standard_logs.loc[:, ["time", "out"]])
cursor = response.headers['x-iteration-cursor']

# if there's another record, get the next one

while 'x-iteration-cursor' in response.headers:
    # retrieve the authorization token
    headers = wl.auth.auth_header()

    url = f"{wl.api_endpoint}/v1/api/pipelines/get_logs"

    # datetime set back one day to get more values

    data = {
        'pipeline_name': main_pipeline_name,
        'workspace_id': workspace_id,
        'cursor': response.headers['x-iteration-cursor']
    }

    response = requests.post(url, headers=headers, json=data)
    # if there's no response, the logs are done
    if response.json() != []:
        standard_logs = pd.DataFrame.from_records(response.json())
        display(standard_logs.head(5).loc[:, ["time", "out"]])
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1703267304746</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1703267414439</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1703267420527</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1703267426032</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1703267432037</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1703267437567</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1703267442644</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1703267449561</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1703267455734</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>9</th>
      <td>1703267462641</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>10</th>
      <td>1703267468362</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1703267760538</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1703267788432</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1703267794241</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1703267802339</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1703267810346</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1703266176951</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1703266192757</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1703266198591</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1703266205430</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1703266212538</td>
      <td>{'output0': [17.09787, 16.459343, 17.259743, 19.960602, 43.600235, 59.986958, 62.826073, 68.24793, 77.43261, 80.82158, 89.44183, 96.168915, 99.22421, 112.584045, 126.75803, 131.9707, 137.1645, 141.93822, 146.29594, 152.00876, 155.94037, 165.20976, 175.27249, 184.05307, 193.66891, 201.51189, 215.04979, 223.80424, 227.24472, 234.19638, 244.9743, 248.5781, 252.42526, 264.95795, 278.48563, 285.758, 293.1897, 300.48227, 305.47742, 314.46085, 319.89404, 324.83658, 335.99536, 345.1116, 350.31964, 352.41107, 365.44934, 381.30008, 391.52316, 399.29163, 405.78503, 411.33804, 415.93207, 421.6868, 431.67108, 439.9069, 447.71542, 459.38522, 474.13187, 479.32642, 484.49884, 493.5153, 501.29932, 507.7967, 514.26044, 523.1473, 531.3479, 542.5094, 555.619, 557.7229, 564.6408, 571.5525, 572.8373, 587.95703, 604.2997, 609.452, 616.31714, 623.5797, 624.13153, 634.47266, 16.970057, 16.788723, 17.441803, 17.900642, 36.188023, 57.277973, 61.664352, 62.556896, 63.43486, 79.50621, 83.844, 95.983765, 106.166, 115.368454, 123.09253, 124.5821, 128.65866, 139.16113, 142.02315, 143.69855, ...]}</td>
    </tr>
  </tbody>
</table>

### Undeploy Main Pipeline

With the examples and tutorial complete, we will undeploy the main pipeline and return the resources back to the Wallaroo instance.

```python
mainpipeline.undeploy()
```

<table><tr><th>name</th> <td>log-api-cv</td></tr><tr><th>created</th> <td>2023-12-22 17:10:06.563220+00:00</td></tr><tr><th>last_updated</th> <td>2023-12-22 17:55:34.460452+00:00</td></tr><tr><th>deployed</th> <td>False</td></tr><tr><th>arch</th> <td>None</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>b1c6d8ea-0259-4a45-aca5-c065a2d59d2d, a8f0adef-5ab9-4695-95eb-e09c256b221c, d174e395-66b5-40bb-bec0-a689e597749f, 4db1d862-0c8d-4394-9009-8aee1324503c, ce598566-83f7-4983-a8e5-4fc779e2c008, b016fb58-d52e-46e1-afc4-31268f471077, 0bd75ecf-1923-42cf-b7e5-6593699465c0</td></tr><tr><th>steps</th> <td>api-sample-model</td></tr><tr><th>published</th> <td>False</td></tr></table>
