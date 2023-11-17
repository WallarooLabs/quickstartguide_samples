This tutorial and the assets can be downloaded as part of the [Wallaroo Tutorials repository](https://github.com/WallarooLabs/Wallaroo_Tutorials/tree/main/wallaroo-model-cookbooks/hf-clip-vit-base).

## CLIP ViT-B/32 Transformer Demonstration with Wallaroo

The following tutorial demonstrates deploying and performing sample inferences with the Hugging Face CLIP ViT-B/32 Transformer model.

### Prerequisites

This tutorial is geared towards the Wallaroo version 2023.2.1 and above.  The model `clip-vit-base-patch-32.zip` must be downloaded and placed into the `./models` directory.  This is available from the following URL:

[https://storage.googleapis.com/wallaroo-public-data/hf-clip-vit-b32/clip-vit-base-patch-32.zip](https://storage.googleapis.com/wallaroo-public-data/hf-clip-vit-b32/clip-vit-base-patch-32.zip)

If performing this tutorial from outside the Wallaroo JupyterHub environment, install the [Wallaroo SDK](https://pypi.org/project/wallaroo/).

## Steps

### Imports

The first step is to import the libraries used for the example.

```python
import json
import os
import requests

import wallaroo
from wallaroo.pipeline   import Pipeline
from wallaroo.deployment_config import DeploymentConfigBuilder
from wallaroo.framework import Framework
from wallaroo.object import EntityNotFoundError

import pyarrow as pa
import numpy as np
import pandas as pd

from PIL import Image
```

### Connect to the Wallaroo Instance

The first step is to connect to Wallaroo through the Wallaroo client.  The Python library is included in the Wallaroo install and available through the Jupyter Hub interface provided with your Wallaroo environment.

This is accomplished using the `wallaroo.Client()` command, which provides a URL to grant the SDK permission to your specific Wallaroo environment.  When displayed, enter the URL into a browser and confirm permissions.  Store the connection into a variable that can be referenced later.

If logging into the Wallaroo instance through the internal JupyterHub service, use `wl = wallaroo.Client()`.  For more information on Wallaroo Client settings, see the [Client Connection guide](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-client/).

```python
## blank space to log in 

wl = wallaroo.Client()
```

### Set Workspace and Pipeline

The next step is to create the Wallaroo workspace and pipeline used for the inference requests.

* References
  * [Wallaroo SDK Essentials Guide: Workspace Management](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-workspace/)
  * Wallaroo SDK Essentials Guide: Pipeline Management](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-pipelines/wallaroo-sdk-essentials-pipeline/)

```python
## convenience functions from the previous notebooks

# return the workspace called <name> through the Wallaroo client.
def get_workspace(name, client):
    workspace = None
    for ws in client.list_workspaces():
        if ws.name() == name:
            workspace= ws
            return workspace
    # if no workspaces were found
    if workspace==None:
        workspace = wl.create_workspace(name)
    return workspace

# get a pipeline by name in the workspace
def get_pipeline(pipeline_name, workspace, client):
    plist = workspace.pipelines()
    pipeline = [p for p in plist if p.name() == pipeline_name]
    if len(pipeline) <= 0:
        pipeline = client.build_pipeline(pipeline_name)
        return pipeline
    return pipeline[0]

```

```python
# create the workspace and pipeline

workspace_name = 'clip-demo'
pipeline_name = 'clip-demo'

workspace = get_workspace(workspace_name, wl)

wl.set_current_workspace(workspace)
display(wl.get_current_workspace())

pipeline = get_pipeline(pipeline_name, workspace, wl)
pipeline
```

    {'name': 'clip-demo', 'id': 28, 'archived': False, 'created_by': 'b0a387d7-cb82-49e1-81f9-1eb47952a01c', 'created_at': '2023-11-17T18:12:59.090213+00:00', 'models': [], 'pipelines': []}

<table><tr><th>name</th> <td>clip-demo</td></tr><tr><th>created</th> <td>2023-11-17 18:12:59.318806+00:00</td></tr><tr><th>last_updated</th> <td>2023-11-17 18:12:59.318806+00:00</td></tr><tr><th>deployed</th> <td>(none)</td></tr><tr><th>arch</th> <td>None</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>9fb2e370-9adc-40f8-96be-cff824b5f143</td></tr><tr><th>steps</th> <td></td></tr><tr><th>published</th> <td>False</td></tr></table>

### Configure and Upload Model

The 🤗 Hugging Face model is uploaded to Wallaroo by defining the input and output schema, and specifying the model's framework as `wallaroo.framework.Framework.HUGGING_FACE_ZERO_SHOT_IMAGE_CLASSIFICATION`.

The data schemas are defined in Apache PyArrow Schema format.

The model is converted to the Wallaroo Containerized runtime after the upload is complete.

* References
  * [Wallaroo SDK Essentials Guide: Model Uploads and Registrations: Hugging Face](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-model-uploads/wallaroo-sdk-model-upload-hugging-face/)

```python
input_schema = pa.schema([
    pa.field('inputs', # required, fixed image dimensions
        pa.list_(
            pa.list_(
                pa.list_(
                    pa.int64(),
                    list_size=3
                ),
                list_size=640 
            ),
        list_size=480
    )),
    pa.field('candidate_labels', pa.list_(pa.string(), list_size=4)), # required, equivalent to `options` in the provided demo
]) 

output_schema = pa.schema([
    pa.field('score', pa.list_(pa.float64(), list_size=4)), # has to be same as number of candidate labels
    pa.field('label', pa.list_(pa.string(), list_size=4)), # has to be same as number of candidate labels
])
```

### Upload Model

```python
model = wl.upload_model('er-clip-vit', './models/clip-vit-base-patch-32.zip', 
                        framework=Framework.HUGGING_FACE_ZERO_SHOT_IMAGE_CLASSIFICATION, 
                        input_schema=input_schema, 
                        output_schema=output_schema)
model
```

    Waiting for model loading - this will take up to 10.0min.
    Model is pending loading to a container runtime....
    Model is attempting loading to a container runtime...................................................successful
    
    Ready

<table>
        <tr>
          <td>Name</td>
          <td>er-clip-vit</td>
        </tr>
        <tr>
          <td>Version</td>
          <td>4b48c745-4f29-45e5-9843-770b1eadec51</td>
        </tr>
        <tr>
          <td>File Name</td>
          <td>clip-vit-base-patch-32.zip</td>
        </tr>
        <tr>
          <td>SHA</td>
          <td>4efc24685a14e1682301cc0085b9db931aeb5f3f8247854bedc6863275ed0646</td>
        </tr>
        <tr>
          <td>Status</td>
          <td>ready</td>
        </tr>
        <tr>
          <td>Image Path</td>
          <td>proxy.replicated.com/proxy/wallaroo/ghcr.io/wallaroolabs/mac-deploy:v2024.1.0-main-4159</td>
        </tr>
        <tr>
          <td>Architecture</td>
          <td>None</td>
        </tr>
        <tr>
          <td>Updated At</td>
          <td>2023-17-Nov 18:19:57</td>
        </tr>
      </table>

### Deploy Pipeline

With the model uploaded and prepared, we add the model as a pipeline step and deploy it.  For this example, we will allocate 4 Gi of RAM and 1 CPU to the model's use through the pipeline deployment configuration.

* References
  * [Wallaroo SDK Essentials Guide: Pipeline Deployment Configuration](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-pipelines/wallaroo-sdk-essentials-pipeline-deployment-config/)

```python
deployment_config = wallaroo.DeploymentConfigBuilder() \
    .cpus(.25).memory('1Gi') \
    .sidekick_memory(model, '4Gi') \
    .sidekick_cpus(model, 1.0) \
    .build()
```

```python
pipeline.clear()
pipeline.add_model_step(model)
pipeline.deploy(deployment_config=deployment_config)
```

### Run Inference

We verify the pipeline is deployed by checking the `status()`.

The sample images in the `./data` directory are converted into numpy arrays, and the candidate labels added as inputs.  Both are set as DataFrame arrays where the field `inputs` are the image values, and `candidate_labels` the labels.

```python
pipeline.status()
```

    {'status': 'Running',
     'details': [],
     'engines': [{'ip': '10.244.0.103',
       'name': 'engine-6fbd98994c-qrg6z',
       'status': 'Running',
       'reason': None,
       'details': [],
       'pipeline_statuses': {'pipelines': [{'id': 'clip-demo',
          'status': 'Running'}]},
       'model_statuses': {'models': [{'name': 'er-clip-vit',
          'version': '4b48c745-4f29-45e5-9843-770b1eadec51',
          'sha': '4efc24685a14e1682301cc0085b9db931aeb5f3f8247854bedc6863275ed0646',
          'status': 'Running'}]}}],
     'engine_lbs': [{'ip': '10.244.1.26',
       'name': 'engine-lb-584f54c899-8mzkn',
       'status': 'Running',
       'reason': None,
       'details': []}],
     'sidekicks': [{'ip': '10.244.0.102',
       'name': 'engine-sidekick-er-clip-vit-55-554c87c874-bcl7b',
       'status': 'Running',
       'reason': None,
       'details': [],
       'statuses': '\n'}]}

```python
image_paths = [
    "./data/bear-in-tree.jpg",
    "./data/elephant-and-zebras.jpg",
    "./data/horse-and-dogs.jpg",
    "./data/kittens.jpg",
    "./data/remote-monitor.jpg"
]
images = []

for iu in image_paths:
    image = Image.open(iu)
    image = image.resize((640, 480)) # fixed image dimensions
    images.append(np.array(image))

dataframe = pd.DataFrame({"images": images})
```

```python
input_data = {
        "inputs": images,
        "candidate_labels": [["cat", "dog", "horse", "elephant"]] * 5,
}
dataframe = pd.DataFrame(input_data)
dataframe
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>inputs</th>
      <th>candidate_labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[[[60, 62, 61], [62, 64, 63], [67, 69, 68], [7...</td>
      <td>[cat, dog, horse, elephant]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[[[228, 235, 241], [229, 236, 242], [230, 237,...</td>
      <td>[cat, dog, horse, elephant]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[[[177, 177, 177], [177, 177, 177], [177, 177,...</td>
      <td>[cat, dog, horse, elephant]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[[[140, 25, 56], [144, 25, 67], [146, 24, 73],...</td>
      <td>[cat, dog, horse, elephant]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[[[24, 20, 11], [22, 18, 9], [18, 14, 5], [21,...</td>
      <td>[cat, dog, horse, elephant]</td>
    </tr>
  </tbody>
</table>

### Inference Outputs

The inference is run, and the labels with their corresponding confidence values for each label are mapped to `out.label` and `out.score` for each image.

```python
results = pipeline.infer(dataframe,timeout=600,dataset=["in", "out", "metadata.elapsed", "time", "check_failures"])
pd.set_option('display.max_colwidth', None)
display(results.loc[:, ['out.label', 'out.score']])
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>out.label</th>
      <th>out.score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[elephant, dog, horse, cat]</td>
      <td>[0.4146825075149536, 0.3483847379684448, 0.1285749077796936, 0.10835790634155273]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[elephant, horse, dog, cat]</td>
      <td>[0.9981434345245361, 0.001765866531059146, 6.823801231803373e-05, 2.2441448891186155e-05]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[horse, dog, elephant, cat]</td>
      <td>[0.7596800923347473, 0.217111736536026, 0.020392831414937973, 0.0028152535669505596]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[cat, dog, elephant, horse]</td>
      <td>[0.9870228171348572, 0.0066468678414821625, 0.0032716328278183937, 0.003058753442019224]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[dog, horse, cat, elephant]</td>
      <td>[0.5713965892791748, 0.17229433357715607, 0.15523898601531982, 0.1010700911283493]</td>
    </tr>
  </tbody>
</table>

### Undeploy Pipelines

With the tutorial complete, the pipeline is undeployed and the resources returned back to the cluster.

```python
pipeline.undeploy()
```

    Waiting for undeployment - this will take up to 45s ..................................... ok

<table><tr><th>name</th> <td>clip-demo</td></tr><tr><th>created</th> <td>2023-11-17 18:12:59.318806+00:00</td></tr><tr><th>last_updated</th> <td>2023-11-17 18:48:29.241654+00:00</td></tr><tr><th>deployed</th> <td>False</td></tr><tr><th>arch</th> <td>None</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>a73048a7-f8ad-41ad-8b2f-3f17f18e5ef0, 06d24fd4-d350-4711-a79c-21b08c20cb88, 89d3744a-bd6e-454e-a868-34a02bad3920, 4f4d6419-533d-4f1d-91fd-f2e2e5021593, 9fb2e370-9adc-40f8-96be-cff824b5f143</td></tr><tr><th>steps</th> <td>er-clip-vit</td></tr><tr><th>published</th> <td>False</td></tr></table>
