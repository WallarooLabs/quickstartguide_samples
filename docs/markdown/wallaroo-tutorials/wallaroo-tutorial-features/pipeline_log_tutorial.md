This tutorial and the assets can be downloaded as part of the [Wallaroo Tutorials repository](https://github.com/WallarooLabs/Wallaroo_Tutorials/tree/main/wallaroo-features/pipeline_log_tutorial/).

## Pipeline Log Tutorial

This tutorial demonstrates Wallaroo Pipeline logs and 

This tutorial will demonstrate how to:

1. Select or create a workspace, pipeline and upload the control model, then additional models for A/B Testing and Shadow Deploy.
1. Add a pipeline step with the champion model, then deploy the pipeline and perform sample inferences.
1. Display the various log types for a standard deployed pipeline.
1. Swap out the pipeline step with the champion model with a shadow deploy step that compares the champion model against two competitors.
1. Perform sample inferences with a shadow deployed step, then display the log files for a shadow deployed pipeline.
1. Swap out the shadow deployed pipeline step with an A/B pipeline step.
1. Perform sample inferences with a A/B pipeline step, then display the log files for an A/B pipeline step.
1. Undeploy the pipeline.

This tutorial provides the following:

* Models:
  * `models/rf_model.onnx`: The champion model that has been used in this environment for some time.
  * `models/xgb_model.onnx` and `models/gbr_model.onnx`: Rival models that will be tested against the champion.
* Data:
  * `data/xtest-1.df.json` and `data/xtest-1k.df.json`:  DataFrame JSON inference inputs with 1 input and 1,000 inputs.
  * `data/xtest-1k.arrow`:  Apache Arrow inference inputs with 1 input and 1,000 inputs.

## Prerequisites

* A deployed Wallaroo instance
* The following Python libraries installed:
  * [`wallaroo`](https://pypi.org/project/wallaroo/): The Wallaroo SDK. Included with the Wallaroo JupyterHub service by default.
  * [`pandas`](https://pypi.org/project/pandas/): Pandas, mainly used for Pandas DataFrame
  * [`pyarrow`](https://pypi.org/project/pyarrow/): Pyarrow for Apache Arrow support

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

import os
```

### Connect to the Wallaroo Instance

The first step is to connect to Wallaroo through the Wallaroo client.  The Python library is included in the Wallaroo install and available through the Jupyter Hub interface provided with your Wallaroo environment.

This is accomplished using the `wallaroo.Client()` command, which provides a URL to grant the SDK permission to your specific Wallaroo environment.  When displayed, enter the URL into a browser and confirm permissions.  Store the connection into a variable that can be referenced later.

If logging into the Wallaroo instance through the internal JupyterHub service, use `wl = wallaroo.Client()`.  For more information on Wallaroo Client settings, see the [Client Connection guide](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-client/).

```python
# Login through local Wallaroo instance

wl = wallaroo.Client()

wl = wallaroo.Client()

wallarooPrefix = "doc-test."
wallarooSuffix = "wallarooexample.ai"

wl = wallaroo.Client(api_endpoint=f"https://{wallarooPrefix}api.{wallarooSuffix}", 
                    auth_endpoint=f"https://{wallarooPrefix}keycloak.{wallarooSuffix}", 
                    auth_type="sso")
```

### Create Workspace

We will create a workspace to manage our pipeline and models.  The following variables will set the name of our sample workspace then set it as the current workspace.

```python
workspace_name = 'logworkspace'
main_pipeline_name = 'logpipeline-test'
model_name_control = 'logcontrol'
model_file_name_control = './models/rf_model.onnx'
```

```python
def get_workspace(name):
    workspace = None
    for ws in wl.list_workspaces():
        if ws.name() == name:
            workspace= ws
    if(workspace == None):
        workspace = wl.create_workspace(name)
    return workspace
```

```python
workspace = get_workspace(workspace_name)

wl.set_current_workspace(workspace)
```

    {'name': 'logworkspace', 'id': 7, 'archived': False, 'created_by': '218d4494-6ef6-4781-be30-9cbea0aa1695', 'created_at': '2023-10-26T16:30:41.605212+00:00', 'models': [], 'pipelines': []}

## Standard Pipeline

### Upload The Champion Model

For our example, we will upload the champion model that has been trained to derive house prices from a variety of inputs.  The model file is `rf_model.onnx`, and is uploaded with the name `housingcontrol`.

```python
housing_model_control = (wl.upload_model(model_name_control, 
                                         model_file_name_control, 
                                         framework=wallaroo.framework.Framework.ONNX)
                                         .configure(tensor_fields=["tensor"])
                        )
```

### Build the Pipeline

This pipeline is made to be an example of an existing situation where a model is deployed and being used for inferences in a production environment.  We'll call it `housepricepipeline`, set `housingcontrol` as a pipeline step, then run a few sample inferences.

```python
mainpipeline = wl.build_pipeline(main_pipeline_name)
mainpipeline.undeploy()
# in case this pipeline was run before
mainpipeline.clear()
mainpipeline.add_model_step(housing_model_control).deploy()
```

<table><tr><th>name</th> <td>logpipeline-test</td></tr><tr><th>created</th> <td>2023-10-26 16:50:50.930771+00:00</td></tr><tr><th>last_updated</th> <td>2023-10-26 16:50:51.945682+00:00</td></tr><tr><th>deployed</th> <td>True</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>9aa799f3-bae4-49d5-93ec-82ae91a34ea0, 951f1a15-5aa3-478b-ac64-a1d11a070ab4</td></tr><tr><th>steps</th> <td>logcontrol</td></tr><tr><th>published</th> <td>False</td></tr></table>

### Testing

We'll use two inferences as a quick sample test - one that has a house that should be determined around \$700k, the other with a house determined to be around \$1.5 million.  We'll also save the start and end periods for these events to for later log functionality.

```python
dataframe_start = datetime.datetime.now()

normal_input = pd.DataFrame.from_records({"tensor": [
            [
                4.0, 
                2.5, 
                2900.0, 
                5505.0, 
                2.0, 
                0.0, 
                0.0, 
                3.0, 
                8.0, 
                2900.0, 
                0.0, 
                47.6063, 
                -122.02, 
                2970.0, 
                5251.0, 
                12.0, 
                0.0, 
                0.0
            ]
        ]
    }
)
result = mainpipeline.infer(normal_input)
display(result)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:49:34.750</td>
      <td>[4.0, 2.5, 2900.0, 5505.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2900.0, 0.0, 47.6063, -122.02, 2970.0, 5251.0, 12.0, 0.0, 0.0]</td>
      <td>[718013.7]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

```python
large_house_input = pd.DataFrame.from_records(
    {
        'tensor': [
            [
                4.0, 
                3.0, 
                3710.0, 
                20000.0, 
                2.0, 
                0.0, 
                2.0, 
                5.0, 
                10.0, 
                2760.0, 
                950.0, 
                47.6696, 
                -122.261, 
                3970.0, 
                20000.0, 
                79.0, 
                0.0, 
                0.0
            ]
        ]
    }
)
large_house_result = mainpipeline.infer(large_house_input)
display(large_house_result)

import time
time.sleep(10)
dataframe_end = datetime.datetime.now()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:49:35.392</td>
      <td>[4.0, 3.0, 3710.0, 20000.0, 2.0, 0.0, 2.0, 5.0, 10.0, 2760.0, 950.0, 47.6696, -122.261, 3970.0, 20000.0, 79.0, 0.0, 0.0]</td>
      <td>[1514079.4]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

As one last sample, we'll run through roughly 1,000 inferences at once and show a few of the results.  For this example we'll use an Apache Arrow table, which has a smaller file size compared to uploading a pandas DataFrame JSON file.  The inference result is returned as an arrow table, which we'll convert into a pandas DataFrame to display the first 20 results.

```python
batch_inferences = mainpipeline.infer_from_file('./data/xtest-1k.arrow')

large_inference_result = batch_inferences.to_pandas()
display(large_inference_result.head(20))
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.5, 2900.0, 5505.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2900.0, 0.0, 47.6063, -122.02, 2970.0, 5251.0, 12.0, 0.0, 0.0]</td>
      <td>[718013.75]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[2.0, 2.5, 2170.0, 6361.0, 1.0, 0.0, 2.0, 3.0, 8.0, 2170.0, 0.0, 47.7109, -122.017, 2310.0, 7419.0, 6.0, 0.0, 0.0]</td>
      <td>[615094.56]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.5, 1300.0, 812.0, 2.0, 0.0, 0.0, 3.0, 8.0, 880.0, 420.0, 47.5893, -122.317, 1300.0, 824.0, 6.0, 0.0, 0.0]</td>
      <td>[448627.72]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.5, 2500.0, 8540.0, 2.0, 0.0, 0.0, 3.0, 9.0, 2500.0, 0.0, 47.5759, -121.994, 2560.0, 8475.0, 24.0, 0.0, 0.0]</td>
      <td>[758714.2]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 1.75, 2200.0, 11520.0, 1.0, 0.0, 0.0, 4.0, 7.0, 2200.0, 0.0, 47.7659, -122.341, 1690.0, 8038.0, 62.0, 0.0, 0.0]</td>
      <td>[513264.7]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.0, 2140.0, 4923.0, 1.0, 0.0, 0.0, 4.0, 8.0, 1070.0, 1070.0, 47.6902, -122.339, 1470.0, 4923.0, 86.0, 0.0, 0.0]</td>
      <td>[668288.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 3.5, 3590.0, 5334.0, 2.0, 0.0, 2.0, 3.0, 9.0, 3140.0, 450.0, 47.6763, -122.267, 2100.0, 6250.0, 9.0, 0.0, 0.0]</td>
      <td>[1004846.5]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.0, 1280.0, 960.0, 2.0, 0.0, 0.0, 3.0, 9.0, 1040.0, 240.0, 47.602, -122.311, 1280.0, 1173.0, 0.0, 0.0, 0.0]</td>
      <td>[684577.2]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.5, 2820.0, 15000.0, 2.0, 0.0, 0.0, 4.0, 9.0, 2820.0, 0.0, 47.7255, -122.101, 2440.0, 15000.0, 29.0, 0.0, 0.0]</td>
      <td>[727898.1]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.25, 1790.0, 11393.0, 1.0, 0.0, 0.0, 3.0, 8.0, 1790.0, 0.0, 47.6297, -122.099, 2290.0, 11894.0, 36.0, 0.0, 0.0]</td>
      <td>[559631.1]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 1.5, 1010.0, 7683.0, 1.5, 0.0, 0.0, 5.0, 7.0, 1010.0, 0.0, 47.72, -122.318, 1550.0, 7271.0, 61.0, 0.0, 0.0]</td>
      <td>[340764.53]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.0, 1270.0, 1323.0, 3.0, 0.0, 0.0, 3.0, 8.0, 1270.0, 0.0, 47.6934, -122.342, 1330.0, 1323.0, 8.0, 0.0, 0.0]</td>
      <td>[442168.06]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 1.75, 2070.0, 9120.0, 1.0, 0.0, 0.0, 4.0, 7.0, 1250.0, 820.0, 47.6045, -122.123, 1650.0, 8400.0, 57.0, 0.0, 0.0]</td>
      <td>[630865.6]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 1.0, 1620.0, 4080.0, 1.5, 0.0, 0.0, 3.0, 7.0, 1620.0, 0.0, 47.6696, -122.324, 1760.0, 4080.0, 91.0, 0.0, 0.0]</td>
      <td>[559631.1]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 3.25, 3990.0, 9786.0, 2.0, 0.0, 0.0, 3.0, 9.0, 3990.0, 0.0, 47.6784, -122.026, 3920.0, 8200.0, 10.0, 0.0, 0.0]</td>
      <td>[909441.1]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.0, 1780.0, 19843.0, 1.0, 0.0, 0.0, 3.0, 7.0, 1780.0, 0.0, 47.4414, -122.154, 2210.0, 13500.0, 52.0, 0.0, 0.0]</td>
      <td>[313096.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.5, 2130.0, 6003.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2130.0, 0.0, 47.4518, -122.12, 1940.0, 4529.0, 11.0, 0.0, 0.0]</td>
      <td>[404040.8]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 1.75, 1660.0, 10440.0, 1.0, 0.0, 0.0, 3.0, 7.0, 1040.0, 620.0, 47.4448, -121.77, 1240.0, 10380.0, 36.0, 0.0, 0.0]</td>
      <td>[292859.5]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.5, 2110.0, 4118.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2110.0, 0.0, 47.3878, -122.153, 2110.0, 4044.0, 25.0, 0.0, 0.0]</td>
      <td>[338357.88]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.25, 2200.0, 11250.0, 1.5, 0.0, 0.0, 5.0, 7.0, 1300.0, 900.0, 47.6845, -122.201, 2320.0, 10814.0, 94.0, 0.0, 0.0]</td>
      <td>[682284.6]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

### Standard Pipeline Logs

Pipeline logs with standard pipeline steps are retrieved either with:

* Pipeline `logs` which returns either a pandas DataFrame or Apache Arrow table.
* Pipeline `export_logs` which saves the logs either a pandas DataFrame JSON file or Apache Arrow table.

For full details, see the Wallaroo Documentation Pipeline Log Management guide.

#### Pipeline Log Method

The Pipeline `logs` method includes the following parameters.  For a complete list, see the [Wallaroo SDK Essentials Guide: Pipeline Log Management](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-pipeline-logs/).

| Parameter | Type | Description |
|---|---|---|
| `limit` | **Int** (*Optional*) | Limits how many log records to display.  Defaults to `100`.  If there are more pipeline logs than are being displayed, the **Warning** message `Pipeline log record limit exceeded` will be displayed.  For example, if 100 log files were requested and there are a total of 1,000, the warning message will be displayed. |
| `start_datetime` and `end_datetime` | **DateTime** (*Optional*) | Limits logs to all logs between the `start` and `end` DateTime parameters.  **Both parameters must be provided**. Submitting a `logs()` request with only `start_datetime` or `end_datetime` will generate an exception.<br />If `start_datetime` and `end_datetime` are provided as parameters, then the records are returned in **chronological** order, with the oldest record displayed first. |
| `dataset` | List (*OPTIONAL*) | The datasets to be returned. The datasets available are:<ul><li>`*`: Default. This translates to `["time", "in", "out", "check_failures"]`.</li><li>`time`: The DateTime of the inference request.</li><li>`in`: All inputs listed as `in_{variable_name}`.</li><li>`out`: All outputs listed as `out_variable_name`.</li><li>`check_failures`: Flags whether an [Anomaly or Validation Check]({{<ref "wallaroo-sdk-essentials-pipeline#anomaly-testing">}}) was triggered. `0` indicates no checks were triggered, 1 or greater indicates a check was triggered.</li><li>`meta`: Returns metadata. **IMPORTANT NOTE**: See [Metadata RequestsRestrictions](#metadata-requests-restrictions) for specifications on how this dataset can be used with otherdatasets.<ul><li> Returns in the `metadata.elapsed` field:<ul><li>A list of time in nanoseconds for:<ul><li>The time to serialize the input.</li><li>How long each step took.</li></ul></li></ul></li><li>Returns in the `metadata.last_model` field:</li><ul><li>A dict with each Python step as:<ul><li>`model_name`: The name of the model in the pipeline step.</li><li>`model_sha` : The sha hash of the model in the pipeline step.</li></ul></li></ul></li><li>Returns in the `metadata.pipeline_version` field:<ul><li>The pipeline version as a UUID value.</li></ul></li></ul><li>`metadata.elapsed`: **IMPORTANT NOTE**: See [Metadata Requests Restrictions](#metadata-requests-restrictions)for specifications on how this dataset can be used with other datasets.<ul><li>Returns in the `metadata.elapsed` field:<ul><li>A list of time in nanoseconds for:<ul><li>The time to serialize the input.</li><li>How long each step took.</li></ul></li></ul></li></ul></ul> |
| `arrow` | **Boolean** (*Optional*) | Defaults to **False**.  If `arrow` is set to `True`, then the logs are returned as an [Apache Arrow table](https://arrow.apache.org/).  If `arrow=False`, then the logs are returned as a pandas DataFrame. |

##### Pipeline Log Warnings

If the total number of logs the either the set limit or 10 MB in file size, the following warning is returned:

`Warning: There are more logs available. Please set a larger limit or request a file using export_logs.`

If the total number of logs **requested** either through the limit or through the `start_datetime` and `end_datetime` request is greater than 10 MB in size, the following error is displayed:

`Warning: Pipeline log size limit exceeded. Only displaying 509 log messages. Please request a file using export_logs.`

The following examples demonstrate displaying the logs, then displaying the logs between the `control_model_start` and `control_model_end` periods, then again retrieved as an Arrow table with the logs limited to only 5 entries.

```python
# pipeline log retrieval - reverse chronological order

regular_logs = mainpipeline.logs()

display("Standard Logs")
display(len(regular_logs))
display(regular_logs)

# Display metadata

metadatalogs = mainpipeline.logs(dataset=["time", "out.variable", "metadata"])
display("Metadata Logs")
# Only showing the pipeline version for space reasons
display(metadatalogs.loc[:, ["time", "out.variable", "metadata.pipeline_version"]])

# Display logs restricted by date and limit 

display("Logs restricted by date")
arrow_logs = mainpipeline.logs(start_datetime=dataframe_start, end_datetime=dataframe_end, limit=50)

display(len(arrow_logs))
display(arrow_logs)

# # pipeline log retrieval limited to arrow tables
display(mainpipeline.logs(arrow=True))
```

    Warning: There are more logs available. Please set a larger limit or request a file using export_logs.

    'Standard Logs'

    100

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[3.0, 2.0, 2005.0, 7000.0, 1.0, 0.0, 0.0, 3.0, 7.0, 1605.0, 400.0, 47.6039, -122.298, 1750.0, 4500.0, 34.0, 0.0, 0.0]</td>
      <td>[581003.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[3.0, 1.75, 2910.0, 37461.0, 1.0, 0.0, 0.0, 4.0, 7.0, 1530.0, 1380.0, 47.7015, -122.164, 2520.0, 18295.0, 47.0, 0.0, 0.0]</td>
      <td>[706823.56]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[4.0, 3.25, 2910.0, 1880.0, 2.0, 0.0, 3.0, 5.0, 9.0, 1830.0, 1080.0, 47.616, -122.282, 3100.0, 8200.0, 100.0, 0.0, 0.0]</td>
      <td>[1060847.5]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[4.0, 1.75, 2700.0, 7875.0, 1.5, 0.0, 0.0, 4.0, 8.0, 2700.0, 0.0, 47.454, -122.144, 2220.0, 7875.0, 46.0, 0.0, 0.0]</td>
      <td>[441960.38]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[3.0, 2.5, 2900.0, 23550.0, 1.0, 0.0, 0.0, 3.0, 10.0, 1490.0, 1410.0, 47.5708, -122.153, 2900.0, 19604.0, 27.0, 0.0, 0.0]</td>
      <td>[827411.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>95</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[2.0, 1.5, 1070.0, 1236.0, 2.0, 0.0, 0.0, 3.0, 8.0, 1000.0, 70.0, 47.5619, -122.382, 1170.0, 1888.0, 10.0, 0.0, 0.0]</td>
      <td>[435628.56]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>96</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[3.0, 2.5, 2830.0, 6000.0, 1.0, 0.0, 3.0, 3.0, 9.0, 1730.0, 1100.0, 47.5751, -122.378, 2040.0, 5300.0, 60.0, 0.0, 0.0]</td>
      <td>[981676.6]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>97</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[4.0, 1.75, 1720.0, 8750.0, 1.0, 0.0, 0.0, 3.0, 7.0, 860.0, 860.0, 47.726, -122.21, 1790.0, 8750.0, 43.0, 0.0, 0.0]</td>
      <td>[437177.84]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>98</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[4.0, 2.25, 4470.0, 60373.0, 2.0, 0.0, 0.0, 3.0, 11.0, 4470.0, 0.0, 47.7289, -122.127, 3210.0, 40450.0, 26.0, 0.0, 0.0]</td>
      <td>[1208638.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>99</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[3.0, 1.0, 1150.0, 3000.0, 1.0, 0.0, 0.0, 5.0, 6.0, 1150.0, 0.0, 47.6867, -122.345, 1460.0, 3200.0, 108.0, 0.0, 0.0]</td>
      <td>[448627.72]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>100 rows × 4 columns</p>

    Warning: There are more logs available. Please set a larger limit or request a file using export_logs.

    'Metadata Logs'

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out.variable</th>
      <th>metadata.pipeline_version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[581003.0]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[706823.56]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[1060847.5]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[441960.38]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[827411.0]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>95</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[435628.56]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>96</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[981676.6]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>97</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[437177.84]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>98</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[1208638.0]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
    <tr>
      <th>99</th>
      <td>2023-10-26 16:32:19.282</td>
      <td>[448627.72]</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
  </tbody>
</table>
<p>100 rows × 3 columns</p>

    'Logs restricted by date'

    2

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:30:58.396</td>
      <td>[4.0, 2.5, 2900.0, 5505.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2900.0, 0.0, 47.6063, -122.02, 2970.0, 5251.0, 12.0, 0.0, 0.0]</td>
      <td>[718013.7]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 16:32:08.690</td>
      <td>[4.0, 3.0, 3710.0, 20000.0, 2.0, 0.0, 2.0, 5.0, 10.0, 2760.0, 950.0, 47.6696, -122.261, 3970.0, 20000.0, 79.0, 0.0, 0.0]</td>
      <td>[1514079.4]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

    Warning: There are more logs available. Please set a larger limit or request a file using export_logs.

    pyarrow.Table
    time: timestamp[ms]
    in.tensor: list<item: float> not null
      child 0, item: float
    out.variable: list<inner: float not null> not null
      child 0, inner: float not null
    check_failures: int8
    ----
    time: [[2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,...,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282,2023-10-26 16:32:19.282]]
    in.tensor: [[[3,2,2005,7000,1,...,1750,4500,34,0,0],[3,1.75,2910,37461,1,...,2520,18295,47,0,0],...,[4,2.25,4470,60373,2,...,3210,40450,26,0,0],[3,1,1150,3000,1,...,1460,3200,108,0,0]]]
    out.variable: [[[581003],[706823.56],...,[1208638],[448627.72]]]
    check_failures: [[0,0,0,0,0,...,0,0,0,0,0]]

```python
result = mainpipeline.infer(normal_input, dataset=["*", "metadata.pipeline_version"])
display(result)
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
      <th>metadata.pipeline_version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:47:45.922</td>
      <td>[4.0, 2.5, 2900.0, 5505.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2900.0, 0.0, 47.6063, -122.02, 2970.0, 5251.0, 12.0, 0.0, 0.0]</td>
      <td>[718013.7]</td>
      <td>0</td>
      <td>23b11216-7b04-4e2e-862d-26308055f3cc</td>
    </tr>
  </tbody>
</table>

The following displays the pipeline metadata logs.

#### Standard Pipeline Steps Log Requests

Effected pipeline steps:

* `add_model_step`
* `replace_with_model_step`

For log file requests, the following metadata dataset requests for standard pipeline steps are available:

* `metadata`

These must be paired with specific columns.  `*` is **not** available when paired with `metadata`.

* `in`: All input fields.
* `out`: All output fields.
* `time`: The DateTime the inference request was made. 
* `in.{input_fields}`: Any input fields (`tensor`, etc.)
* `out.{output_fields}`: Any output fields (`out.house_price`, `out.variable`, etc.)
* `check_failures`:  Any validation check failures.

The following requests the metadata, and displays the output variable and last model from the metadata.

```python
# Display metadata

metadatalogs = mainpipeline.logs(dataset=["out","metadata"])
display("Metadata Logs")
display(metadatalogs.loc[:, ['out.variable', 'metadata.last_model']])

```

    Warning: There are more logs available. Please set a larger limit or request a file using export_logs.

    'Metadata Logs'

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out.variable</th>
      <th>metadata.last_model</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[581003.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[706823.56]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[1060847.5]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[441960.38]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[827411.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>95</th>
      <td>[435628.56]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>96</th>
      <td>[981676.6]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>97</th>
      <td>[437177.84]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>98</th>
      <td>[1208638.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>99</th>
      <td>[448627.72]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
  </tbody>
</table>
<p>100 rows × 2 columns</p>

#### Pipeline Limits

In a previous step we performed 10,000 inferences at once.  If we attempt to pull them at once, we'll likely run into the size limit for this pipeline and receive the following warning message indicating that the pipeline size limits were exceeded and we should use `export_logs` instead.

`Warning: Pipeline log size limit exceeded. Only displaying 1000 log messages (of 10000 requested). Please request a file using export_logs.`

```python
logs = mainpipeline.logs(limit=10000)
display(logs)
```

    Warning: Pipeline log size limit exceeded. Please request logs using export_logs

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>in.tensor</th>
      <th>out.variable</th>
      <th>check_failures</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.0, 2005.0, 7000.0, 1.0, 0.0, 0.0, 3.0, 7.0, 1605.0, 400.0, 47.6039, -122.298, 1750.0, 4500.0, 34.0, 0.0, 0.0]</td>
      <td>[581003.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 1.75, 2910.0, 37461.0, 1.0, 0.0, 0.0, 4.0, 7.0, 1530.0, 1380.0, 47.7015, -122.164, 2520.0, 18295.0, 47.0, 0.0, 0.0]</td>
      <td>[706823.56]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 3.25, 2910.0, 1880.0, 2.0, 0.0, 3.0, 5.0, 9.0, 1830.0, 1080.0, 47.616, -122.282, 3100.0, 8200.0, 100.0, 0.0, 0.0]</td>
      <td>[1060847.5]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 1.75, 2700.0, 7875.0, 1.5, 0.0, 0.0, 4.0, 8.0, 2700.0, 0.0, 47.454, -122.144, 2220.0, 7875.0, 46.0, 0.0, 0.0]</td>
      <td>[441960.38]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.5, 2900.0, 23550.0, 1.0, 0.0, 0.0, 3.0, 10.0, 1490.0, 1410.0, 47.5708, -122.153, 2900.0, 19604.0, 27.0, 0.0, 0.0]</td>
      <td>[827411.0]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>661</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[5.0, 3.25, 3160.0, 10587.0, 1.0, 0.0, 0.0, 5.0, 7.0, 2190.0, 970.0, 47.7238, -122.165, 2200.0, 7761.0, 55.0, 0.0, 0.0]</td>
      <td>[573403.1]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>662</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.5, 2210.0, 7620.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2210.0, 0.0, 47.6938, -122.13, 1920.0, 7440.0, 20.0, 0.0, 0.0]</td>
      <td>[677870.9]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>663</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 1.75, 1960.0, 8136.0, 1.0, 0.0, 0.0, 3.0, 7.0, 980.0, 980.0, 47.5208, -122.364, 1070.0, 7480.0, 66.0, 0.0, 0.0]</td>
      <td>[365436.25]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>664</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[3.0, 2.0, 1260.0, 8092.0, 1.0, 0.0, 0.0, 3.0, 7.0, 1260.0, 0.0, 47.3635, -122.054, 1950.0, 8092.0, 28.0, 0.0, 0.0]</td>
      <td>[253958.75]</td>
      <td>0</td>
    </tr>
    <tr>
      <th>665</th>
      <td>2023-10-26 16:51:09.710</td>
      <td>[4.0, 2.5, 2650.0, 18295.0, 2.0, 0.0, 0.0, 3.0, 8.0, 2650.0, 0.0, 47.6075, -122.154, 2230.0, 19856.0, 28.0, 0.0, 0.0]</td>
      <td>[706407.4]</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>666 rows × 4 columns</p>

#### Pipeline export_logs Method

The Pipeline method `export_logs` returns the Pipeline records as either a DataFrame JSON file, or an Apache Arrow table file.  For a complete list, see the [Wallaroo SDK Essentials Guide: Pipeline Log Management](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-pipeline-logs/).

The `export_logs` method takes the following parameters:

| Parameter | Type | Description |
|---|---|---|
| `directory` | **String** (*Optional*) (*Default*: `logs`) | Logs are exported to a file from current working directory to `directory`.|
| `data_size_limit` | **String** (*Optional*) ((*Default*: `100MB`) | The maximum size for the exported data in bytes.  Note that file size is approximate to the request; a request of `10MiB` may return 10.3MB of data.  The fields are in the format "{size as number} {unit value}", and can include a space so "10 MiB" and "10MiB" are the same.  The accepted unit values are:  <ul><li>`KiB` (for KiloBytes)</li><li>`MiB` (for MegaBytes)</li><li>`GiB` (for GigaBytes)</li><li>`TiB` (for TeraBytes)</li></ul>  |
| `file_prefix` | **String** (*Optional*) (*Default*: The name of the pipeline) | The name of the exported files.  By default, this will the name of the pipeline and is segmented by pipeline version between the limits or the start and end period.  For example:  'logpipeline-1.json`, etc. |
| `limit` | **Int** (*Optional*) | Limits how many log records to display.  Defaults to `100`.  If there are more pipeline logs than are being displayed, the **Warning** message `Pipeline log record limit exceeded` will be displayed.  For example, if 100 log files were requested and there are a total of 1,000, the warning message will be displayed. |
| `start` and `end` | **DateTime** (*Optional*) | Limits logs to all logs between the `start` and `end` DateTime parameters.  **Both parameters must be provided**. Submitting a `logs()` request with only `start` or `end` will generate an exception.<br />If `start` and `end` are provided as parameters, then the records are returned in **chronological** order, with the oldest record displayed first. |
| `dataset` | List (*OPTIONAL*) | The datasets to be returned. The datasets available are:<ul><li>`*`: Default. This translates to `["time", "in", "out", "check_failures"]`.</li><li>`time`: The DateTime of the inference request.</li><li>`in`: All inputs listed as `in_{variable_name}`.</li><li>`out`: All outputs listed as `out_variable_name`.</li><li>`check_failures`: Flags whether an [Anomaly or Validation Check]({{<ref "wallaroo-sdk-essentials-pipeline#anomaly-testing">}}) was triggered. `0` indicates no checks were triggered, 1 or greater indicates a check was triggered.</li><li>`meta`: Returns metadata. **IMPORTANT NOTE**: See [Metadata RequestsRestrictions](#metadata-requests-restrictions) for specifications on how this dataset can be used with otherdatasets.<ul><li> Returns in the `metadata.elapsed` field:<ul><li>A list of time in nanoseconds for:<ul><li>The time to serialize the input.</li><li>How long each step took.</li></ul></li></ul></li><li>Returns in the `metadata.last_model` field:</li><ul><li>A dict with each Python step as:<ul><li>`model_name`: The name of the model in the pipeline step.</li><li>`model_sha` : The sha hash of the model in the pipeline step.</li></ul></li></ul></li><li>Returns in the `metadata.pipeline_version` field:<ul><li>The pipeline version as a UUID value.</li></ul></li></ul><li>`metadata.elapsed`: **IMPORTANT NOTE**: See [Metadata Requests Restrictions](#metadata-requests-restrictions)for specifications on how this dataset can be used with other datasets.<ul><li>Returns in the `metadata.elapsed` field:<ul><li>A list of time in nanoseconds for:<ul><li>The time to serialize the input.</li><li>How long each step took.</li></ul></li></ul></li></ul></ul> |
| `arrow` | **Boolean** (*Optional*) | Defaults to **False**.  If `arrow` is set to `True`, then the logs are returned as an [Apache Arrow table](https://arrow.apache.org/).  If `arrow=False`, then the logs are returned as JSON in pandas DataFrame format. |

The following examples demonstrate saving a DataFrame version of the `mainpipeline` logs, then an Arrow version.

```python
# Save the DataFrame version of the log file

mainpipeline.export_logs()
display(os.listdir('./logs'))

mainpipeline.export_logs(arrow=True)
display(os.listdir('./logs'))
```

    Warning: There are more logs available. Please set a larger limit to export more data.
    

    ['logpipeline-1.json']

    Warning: There are more logs available. Please set a larger limit to export more data.
    

    ['logpipeline-1.arrow', 'logpipeline-1.json']

## Shadow Deploy Pipelines

Let's assume that after analyzing the assay information we want to test two challenger models to our control.  We do that with the Shadow Deploy pipeline step.

In Shadow Deploy, the pipeline step is added with the `add_shadow_deploy` method, with the champion model listed first, then an array of challenger models after.  **All** inference data is fed to **all** models, with the champion results displayed in the `out.variable` column, and the shadow results in the format `out_{model name}.variable`.  For example, since we named our challenger models `housingchallenger01` and `housingchallenger02`, the columns `out_housingchallenger01.variable` and `out_housingchallenger02.variable` have the shadow deployed model results.

For this example, we will remove the previous pipeline step, then replace it with a shadow deploy step with `rf_model.onnx` as our champion, and models `xgb_model.onnx` and `gbr_model.onnx` as the challengers.  We'll deploy the pipeline and prepare it for sample inferences.

```python
# Upload the challenger models

model_name_challenger01 = 'logcontrolchallenger01'
model_file_name_challenger01 = './models/xgb_model.onnx'

model_name_challenger02 = 'logcontrolchallenger02'
model_file_name_challenger02 = './models/gbr_model.onnx'

housing_model_challenger01 = (wl.upload_model(model_name_challenger01, 
                                              model_file_name_challenger01, 
                                              framework=wallaroo.framework.Framework.ONNX)
                                              .configure(tensor_fields=["tensor"])
                            )
housing_model_challenger02 = (wl.upload_model(model_name_challenger02, 
                                              model_file_name_challenger02, 
                                              framework=wallaroo.framework.Framework.ONNX)
                                              .configure(tensor_fields=["tensor"])
                            )

```

```python
# Undeploy the pipeline
mainpipeline.undeploy()

mainpipeline.clear()

# Add the new shadow deploy step with our challenger models
mainpipeline.add_shadow_deploy(housing_model_control, [housing_model_challenger01, housing_model_challenger02])

# Deploy the pipeline with the new shadow step
mainpipeline.deploy()
```

<table><tr><th>name</th> <td>logpipeline-test</td></tr><tr><th>created</th> <td>2023-10-26 16:50:50.930771+00:00</td></tr><tr><th>last_updated</th> <td>2023-10-26 17:04:50.279469+00:00</td></tr><tr><th>deployed</th> <td>True</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>b487e3d5-3cff-42de-b4d2-40eab6ad37c3, 9aa799f3-bae4-49d5-93ec-82ae91a34ea0, 951f1a15-5aa3-478b-ac64-a1d11a070ab4</td></tr><tr><th>steps</th> <td>logcontrol</td></tr><tr><th>published</th> <td>False</td></tr></table>

### Shadow Deploy Sample Inference

We'll now use our same sample data for an inference to our shadow deployed pipeline, then display the first 20 results with just the comparative outputs.

```python
shadow_date_start = datetime.datetime.now()

shadow_result = mainpipeline.infer_from_file('./data/xtest-1k.arrow')

shadow_outputs =  shadow_result.to_pandas()
display(shadow_outputs.loc[0:20,['out.variable','out_logcontrolchallenger01.variable','out_logcontrolchallenger02.variable']])

shadow_date_end = datetime.datetime.now()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out.variable</th>
      <th>out_logcontrolchallenger01.variable</th>
      <th>out_logcontrolchallenger02.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[718013.75]</td>
      <td>[659806.0]</td>
      <td>[704901.9]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[615094.56]</td>
      <td>[732883.5]</td>
      <td>[695994.44]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[448627.72]</td>
      <td>[419508.84]</td>
      <td>[416164.8]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[758714.2]</td>
      <td>[634028.8]</td>
      <td>[655277.2]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[513264.7]</td>
      <td>[427209.44]</td>
      <td>[426854.66]</td>
    </tr>
    <tr>
      <th>5</th>
      <td>[668288.0]</td>
      <td>[615501.9]</td>
      <td>[632556.1]</td>
    </tr>
    <tr>
      <th>6</th>
      <td>[1004846.5]</td>
      <td>[1139732.5]</td>
      <td>[1100465.2]</td>
    </tr>
    <tr>
      <th>7</th>
      <td>[684577.2]</td>
      <td>[498328.88]</td>
      <td>[528278.06]</td>
    </tr>
    <tr>
      <th>8</th>
      <td>[727898.1]</td>
      <td>[722664.4]</td>
      <td>[659439.94]</td>
    </tr>
    <tr>
      <th>9</th>
      <td>[559631.1]</td>
      <td>[525746.44]</td>
      <td>[534331.44]</td>
    </tr>
    <tr>
      <th>10</th>
      <td>[340764.53]</td>
      <td>[376337.1]</td>
      <td>[377187.2]</td>
    </tr>
    <tr>
      <th>11</th>
      <td>[442168.06]</td>
      <td>[382053.12]</td>
      <td>[403964.3]</td>
    </tr>
    <tr>
      <th>12</th>
      <td>[630865.6]</td>
      <td>[505608.97]</td>
      <td>[528991.3]</td>
    </tr>
    <tr>
      <th>13</th>
      <td>[559631.1]</td>
      <td>[603260.5]</td>
      <td>[612201.75]</td>
    </tr>
    <tr>
      <th>14</th>
      <td>[909441.1]</td>
      <td>[969585.4]</td>
      <td>[893874.7]</td>
    </tr>
    <tr>
      <th>15</th>
      <td>[313096.0]</td>
      <td>[313633.75]</td>
      <td>[318054.94]</td>
    </tr>
    <tr>
      <th>16</th>
      <td>[404040.8]</td>
      <td>[360413.56]</td>
      <td>[357816.75]</td>
    </tr>
    <tr>
      <th>17</th>
      <td>[292859.5]</td>
      <td>[316674.94]</td>
      <td>[294034.7]</td>
    </tr>
    <tr>
      <th>18</th>
      <td>[338357.88]</td>
      <td>[299907.44]</td>
      <td>[323254.3]</td>
    </tr>
    <tr>
      <th>19</th>
      <td>[682284.6]</td>
      <td>[811896.75]</td>
      <td>[770916.7]</td>
    </tr>
    <tr>
      <th>20</th>
      <td>[583765.94]</td>
      <td>[573618.5]</td>
      <td>[549141.4]</td>
    </tr>
  </tbody>
</table>

### Shadow Deploy Logs

Pipelines with a shadow deployed step include the shadow inference result in the same format as the inference result:  inference results from shadow deployed models are displayed as `out_{model name}.{output variable}`.

```python
# display logs with shadow deployed steps

display(mainpipeline.logs(start_datetime=shadow_date_start, end_datetime=shadow_date_end).loc[:, ["time", "out.variable", "out_logcontrolchallenger01.variable", "out_logcontrolchallenger02.variable"]])
```

    Warning: Pipeline log size limit exceeded. Please request logs using export_logs

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out.variable</th>
      <th>out_logcontrolchallenger01.variable</th>
      <th>out_logcontrolchallenger02.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[718013.75]</td>
      <td>[659806.0]</td>
      <td>[704901.9]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[615094.56]</td>
      <td>[732883.5]</td>
      <td>[695994.44]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[448627.72]</td>
      <td>[419508.84]</td>
      <td>[416164.8]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[758714.2]</td>
      <td>[634028.8]</td>
      <td>[655277.2]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[513264.7]</td>
      <td>[427209.44]</td>
      <td>[426854.66]</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>663</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[642519.75]</td>
      <td>[390891.06]</td>
      <td>[481425.8]</td>
    </tr>
    <tr>
      <th>664</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[301714.75]</td>
      <td>[406503.62]</td>
      <td>[374509.53]</td>
    </tr>
    <tr>
      <th>665</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[448627.72]</td>
      <td>[473771.0]</td>
      <td>[478128.03]</td>
    </tr>
    <tr>
      <th>666</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[544392.1]</td>
      <td>[428174.9]</td>
      <td>[442408.25]</td>
    </tr>
    <tr>
      <th>667</th>
      <td>2023-10-26 17:05:08.349</td>
      <td>[944006.75]</td>
      <td>[902058.6]</td>
      <td>[866622.25]</td>
    </tr>
  </tbody>
</table>
<p>668 rows × 4 columns</p>

For log file requests, the following metadata dataset requests for testing pipeline steps are available:

* `metadata`

These must be paired with specific columns.  `*` is **not** available when paired with `metadata`.

* `in`: All input fields.
* `out`: All output fields.
* `time`: The DateTime the inference request was made.
* `in.{input_fields}`: Any input fields (`tensor`, etc.).
* `out.{output_fields}`: Any output fields matching the specific `output_field` (`out.house_price`, `out.variable`, etc.).
* `out_`: All shadow deployed challenger steps Any output fields matching the specific `output_field` (`out.house_price`, `out.variable`, etc.).
* `check_failures`:  Any validation check failures.

The following example retrieves the logs from a pipeline with shadow deployed models, and displays the specific shadow deployed model outputs and the `metadata.elasped` field.

```python
# display logs with shadow deployed steps

display(mainpipeline.logs(start_datetime=shadow_date_start, end_datetime=shadow_date_end).loc[:, ["time", 
                                                                                                  "out.variable", 
                                                                                                  "out_logcontrolchallenger01.variable", 
                                                                                                  "out_logcontrolchallenger02.variable"
                                                                                                  ]
                                                                                        ])
```

    Warning: Pipeline log size limit exceeded. Please request logs using export_logs

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>out.variable</th>
      <th>out_logcontrolchallenger01.variable</th>
      <th>out_logcontrolchallenger02.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[718013.75]</td>
      <td>[659806.0]</td>
      <td>[704901.9]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[615094.56]</td>
      <td>[732883.5]</td>
      <td>[695994.44]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[448627.72]</td>
      <td>[419508.84]</td>
      <td>[416164.8]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[758714.2]</td>
      <td>[634028.8]</td>
      <td>[655277.2]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[513264.7]</td>
      <td>[427209.44]</td>
      <td>[426854.66]</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>663</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[642519.75]</td>
      <td>[390891.06]</td>
      <td>[481425.8]</td>
    </tr>
    <tr>
      <th>664</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[301714.75]</td>
      <td>[406503.62]</td>
      <td>[374509.53]</td>
    </tr>
    <tr>
      <th>665</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[448627.72]</td>
      <td>[473771.0]</td>
      <td>[478128.03]</td>
    </tr>
    <tr>
      <th>666</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[544392.1]</td>
      <td>[428174.9]</td>
      <td>[442408.25]</td>
    </tr>
    <tr>
      <th>667</th>
      <td>2023-10-26 17:07:56.576</td>
      <td>[944006.75]</td>
      <td>[902058.6]</td>
      <td>[866622.25]</td>
    </tr>
  </tbody>
</table>
<p>668 rows × 4 columns</p>

```python
metadatalogs = mainpipeline.logs(dataset=["time",
                                          "out_logcontrolchallenger01.variable", 
                                          "out_logcontrolchallenger02.variable", 
                                          "metadata"
                                          ],
                                start_datetime=shadow_date_start, 
                                end_datetime=shadow_date_end
                                )

display(metadatalogs.loc[:, ['out_logcontrolchallenger01.variable',	
                             'out_logcontrolchallenger02.variable', 
                             'metadata.elapsed'
                             ]
                        ])
```

    Warning: Pipeline log size limit exceeded. Please request logs using export_logs

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out_logcontrolchallenger01.variable</th>
      <th>out_logcontrolchallenger02.variable</th>
      <th>metadata.elapsed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[659806.0]</td>
      <td>[704901.9]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[732883.5]</td>
      <td>[695994.44]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[419508.84]</td>
      <td>[416164.8]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[634028.8]</td>
      <td>[655277.2]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[427209.44]</td>
      <td>[426854.66]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>663</th>
      <td>[390891.06]</td>
      <td>[481425.8]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>664</th>
      <td>[406503.62]</td>
      <td>[374509.53]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>665</th>
      <td>[473771.0]</td>
      <td>[478128.03]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>666</th>
      <td>[428174.9]</td>
      <td>[442408.25]</td>
      <td>[302804, 26900]</td>
    </tr>
    <tr>
      <th>667</th>
      <td>[902058.6]</td>
      <td>[866622.25]</td>
      <td>[302804, 26900]</td>
    </tr>
  </tbody>
</table>
<p>668 rows × 3 columns</p>

The following demonstrates exporting the shadow deployed logs to the directory `shadow`.

```python
# Save shadow deployed log files as pandas DataFrame

mainpipeline.export_logs(directory="shadow", file_prefix="shadowdeploylogs")
display(os.listdir('./shadow'))
```

    Warning: There are more logs available. Please set a larger limit to export more data.
    

    ['shadowdeploylogs-1.json']

## A/B Testing Pipeline

A/B testing allows inference requests to be split between a control model and one or more challenger models.  For full details, see the [Pipeline Management Guide: A/B Testing](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-pipeline/#ab-testing).

When the inference results and log entries are displayed, they include the column `out._model_split` which displays:

| Field | Type | Description |
|---|---|---|
| `name` | String | The model name used for the inference.  |
| `version` | String| The version of the model. |
| `sha` | String | The sha hash of the model version. |

For this example, the shadow deployed step will be removed and replaced with an A/B Testing step with the ratio 1:1:1, so the control and each of the challenger models will be split randomly between inference requests.  A set of sample inferences will be run, then the pipeline logs displayed.

pipeline = (wl.build_pipeline("randomsplitpipeline-demo")
            .add_random_split([(2, control), (1, challenger)], "session_id"))

```python
mainpipeline.undeploy()

# remove the shadow deploy steps
mainpipeline.clear()

# Add the a/b test step to the pipeline
mainpipeline.add_random_split([(1, housing_model_control), (1, housing_model_challenger01), (1, housing_model_challenger02)], "session_id")

mainpipeline.deploy()

# Perform sample inferences of 20 rows and display the results
ab_date_start = datetime.datetime.now()
abtesting_inputs = pd.read_json('./data/xtest-1k.df.json')

for index, row in abtesting_inputs.sample(20).iterrows():
    display(mainpipeline.infer(row.to_frame('tensor').reset_index()).loc[:,["out._model_split", "out.variable"]])

ab_date_end = datetime.datetime.now()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[921695.4]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[455095.16]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[286100.3]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger02","version":"87a39cd8-1ff5-41a7-b66b-373d49fd2452","sha":"ed6065a79d841f7e96307bb20d5ef22840f15da0b587efb51425c7ad60589d6a"}]</td>
      <td>[360863.16]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger02","version":"87a39cd8-1ff5-41a7-b66b-373d49fd2452","sha":"ed6065a79d841f7e96307bb20d5ef22840f15da0b587efb51425c7ad60589d6a"}]</td>
      <td>[356897.44]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger02","version":"87a39cd8-1ff5-41a7-b66b-373d49fd2452","sha":"ed6065a79d841f7e96307bb20d5ef22840f15da0b587efb51425c7ad60589d6a"}]</td>
      <td>[732620.3]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[729163.06]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger02","version":"87a39cd8-1ff5-41a7-b66b-373d49fd2452","sha":"ed6065a79d841f7e96307bb20d5ef22840f15da0b587efb51425c7ad60589d6a"}]</td>
      <td>[725518.4]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[448627.8]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[628291.1]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[340764.53]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[491306.7]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[673288.6]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[464811.13]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger02","version":"87a39cd8-1ff5-41a7-b66b-373d49fd2452","sha":"ed6065a79d841f7e96307bb20d5ef22840f15da0b587efb51425c7ad60589d6a"}]</td>
      <td>[268304.4]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[1182820.6]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[271387.47]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[637377.0]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrol","version":"096065f1-2d21-4c8b-b499-0c813bc09c04","sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}]</td>
      <td>[403520.16]</td>
    </tr>
  </tbody>
</table>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out._model_split</th>
      <th>out.variable</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[{"name":"logcontrolchallenger01","version":"470363b5-6353-47ae-8c66-1631b783f562","sha":"31e92d6ccb27b041a324a7ac22cf95d9d6cc3aa7e8263a229f7c4aec4938657c"}]</td>
      <td>[1165000.1]</td>
    </tr>
  </tbody>
</table>

```python
## Get the logs with the a/b testing information

metadatalogs = mainpipeline.logs(dataset=["time",
                                          "out", 
                                          "metadata"
                                          ]
                                )

display(metadatalogs.loc[:, ['out.variable', 'metadata.last_model']])
```

    Warning: There are more logs available. Please set a larger limit or request a file using export_logs.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out.variable</th>
      <th>metadata.last_model</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[581003.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[706823.56]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[1060847.5]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[441960.38]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[827411.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>95</th>
      <td>[435628.56]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>96</th>
      <td>[981676.6]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>97</th>
      <td>[437177.84]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>98</th>
      <td>[1208638.0]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
    <tr>
      <th>99</th>
      <td>[448627.72]</td>
      <td>{"model_name":"logcontrol","model_sha":"e22a0831aafd9917f3cc87a15ed267797f80e2afa12ad7d8810ca58f173b8cc6"}</td>
    </tr>
  </tbody>
</table>
<p>100 rows × 2 columns</p>

```python
# Save a/b testing log files as DataFrame

mainpipeline.export_logs(directory="abtesting", 
                         file_prefix="abtests", 
                         start_datetime=ab_date_start, 
                         end_datetime=ab_date_end)
display(os.listdir('./abtesting'))
```

    ['abtests-1.json']

The following exports the metadata with the log files.

```python
# Save a/b testing log files as DataFrame

mainpipeline.export_logs(directory="abtesting-metadata", 
                         file_prefix="abtests", 
                         start_datetime=ab_date_start, 
                         end_datetime=ab_date_end,
                         dataset=["time", "out", "metadata"])
display(os.listdir('./abtesting-metadata'))
```

    ['abtests-1.json']

### Undeploy Main Pipeline

With the examples and tutorial complete, we will undeploy the main pipeline and return the resources back to the Wallaroo instance.

```python
mainpipeline.undeploy()
```

<table><tr><th>name</th> <td>logpipeline-test</td></tr><tr><th>created</th> <td>2023-10-26 16:50:50.930771+00:00</td></tr><tr><th>last_updated</th> <td>2023-10-26 17:46:09.340797+00:00</td></tr><tr><th>deployed</th> <td>False</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>7351b1ab-3038-48e6-81ef-0378a8afc36d, b487e3d5-3cff-42de-b4d2-40eab6ad37c3, 9aa799f3-bae4-49d5-93ec-82ae91a34ea0, 951f1a15-5aa3-478b-ac64-a1d11a070ab4</td></tr><tr><th>steps</th> <td>logcontrol</td></tr><tr><th>published</th> <td>False</td></tr></table>
