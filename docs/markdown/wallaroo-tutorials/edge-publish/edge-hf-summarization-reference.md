The following tutorial is available on the [Wallaroo Github Repository](https://github.com/WallarooLabs/Wallaroo_Tutorials/tree/main/pipeline-edge-publish/edge-llm-summarization).

## Summarization Text Edge Deployment Demonstration

This notebook will walk through building a summarization text pipeline in Wallaroo, deploying it to the local cluster for testing, and then publishing it for edge deployment.

This demonstration will focus on deployment to the edge.  The sample model is available at the following URL.  This model should be downloaded and placed into the `./models` folder before beginning this demonstration.

[model-auto-conversion_hugging-face_complex-pipelines_hf-summarisation-bart-large-samsun.zip (1.4 GB)](https://storage.googleapis.com/wallaroo-public-data/llm-models/model-auto-conversion_hugging-face_complex-pipelines_hf-summarisation-bart-large-samsun.zip)

This demonstration will perform the following:

1. As a Data Scientist:
    1. Upload a computer vision model to Wallaroo, deploy it in a Wallaroo pipeline, then perform a sample inference.
    1. Publish the pipeline to an Open Container Initiative (OCI) Registry service.  This is configured in the Wallaroo instance.  See [Edge Deployment Registry Guide](https://staging.docs.wallaroo.ai/wallaroo-operations-guide/wallaroo-configuration/wallaroo-edge-deployment/) for details on adding an OCI Registry Service to Wallaroo as the Edge Deployment Registry.
    1. View the pipeline publish details.
1. As a DevOps Engineer:
    1. Deploy the published pipeline into an edge instance.  This example will use Docker.
    1. Perform a sample inference into the deployed pipeline with the same data used in the data scientist example.

## Data Scientist Pipeline Publish Steps

### Load Libraries

The first step is to import the libraries used in this notebook.

```python
import wallaroo
from wallaroo.object import EntityNotFoundError

import pyarrow as pa
import pandas as pd

# used to display dataframe information without truncating
from IPython.display import display
pd.set_option('display.max_colwidth', None)
```

### Connect to the Wallaroo Instance through the User Interface

The next step is to connect to Wallaroo through the Wallaroo client.  The Python library is included in the Wallaroo install and available through the Jupyter Hub interface provided with your Wallaroo environment.

This is accomplished using the `wallaroo.Client()` command, which provides a URL to grant the SDK permission to your specific Wallaroo environment.  When displayed, enter the URL into a browser and confirm permissions.  Store the connection into a variable that can be referenced later.

If logging into the Wallaroo instance through the internal JupyterHub service, use `wl = wallaroo.Client()`.  For more information on Wallaroo Client settings, see the [Client Connection guide](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-essentials-client/).

```python
wl = wallaroo.Client()
```

### Create a New Workspace

We'll use the SDK below to create our workspace , assign as our **current workspace**, then display all of the workspaces we have at the moment.  We'll also set up variables for our models and pipelines down the road, so we have one spot to change names to whatever fits your organization's standards best.

To allow this tutorial to be run by multiple users in the same Wallaroo instance, a random 4 character prefix will be added to the workspace, pipeline, and model.  Feel free to set `suffix=''` if this is not required.

```python
import string
import random

# make a random 4 character prefix
suffix= ''.join(random.choice(string.ascii_lowercase) for i in range(4))

suffix=''

workspace_name = f'edge-hf-summarization{suffix}'
pipeline_name = 'edge-hf-summarization'
model_name = 'hf-summarization'
model_file_name = './models/model-auto-conversion_hugging-face_complex-pipelines_hf-summarisation-bart-large-samsun.zip'
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

def get_pipeline(name):
    try:
        pipeline = wl.pipelines_by_name(name)[0]
    except EntityNotFoundError:
        pipeline = wl.build_pipeline(name)
    return pipeline
```

```python
workspace = get_workspace(workspace_name)

wl.set_current_workspace(workspace)
```

    {'name': 'edge-hf-summarization', 'id': 10, 'archived': False, 'created_by': 'aa707604-ec80-495a-a9a1-87774c8086d5', 'created_at': '2023-09-08T18:39:23.616192+00:00', 'models': [], 'pipelines': []}

### Configure PyArrow Schema

This is required for non-native runtimes for models deployed to Wallaroo.

You can find more info on the available inputs under [TextSummarizationInputs](https://github.com/WallarooLabs/platform/blob/main/conductor/model-auto-conversion/flavors/hugging-face/src/io/pipeline_inputs/text_summarization_inputs.py#L14) or under the [official source code](https://github.com/huggingface/transformers/blob/v4.28.1/src/transformers/pipelines/text2text_generation.py#L241) from `🤗 Hugging Face`.

```python
input_schema = pa.schema([
    pa.field('inputs', pa.string()),
    pa.field('return_text', pa.bool_()),
    pa.field('return_tensors', pa.bool_()),
    pa.field('clean_up_tokenization_spaces', pa.bool_()),
    # pa.field('generate_kwargs', pa.map_(pa.string(), pa.null())), # dictionaries are not currently supported by the engine
])

output_schema = pa.schema([
    pa.field('summary_text', pa.string()),
])
```

### Upload the Model

When a model is uploaded to a Wallaroo cluster, it is optimized and packaged to make it ready to run as part of a pipeline. In many times, the Wallaroo Server can natively run a model without any Python overhead. In other cases, such as a Python script, a custom Python environment will be automatically generated. This is comparable to the process of "containerizing" a model by adding a small HTTP server and other wrapping around it.

Our pretrained model is in HuggingFace format, which is specified in the `framework` parameter.  The input and output schemas are included as part of the model upload.  For more information, see [Wallaroo SDK Essentials Guide: Model Uploads and Registrations: Hugging Face](https://docs.wallaroo.ai/wallaroo-developer-guides/wallaroo-sdk-guides/wallaroo-sdk-essentials-guide/wallaroo-sdk-model-uploads/wallaroo-sdk-model-upload-hugging-face/).

```python
model = wl.upload_model(model_name, 
                        model_file_name, 
                        framework=wallaroo.framework.Framework.HUGGING_FACE_SUMMARIZATION, 
                        input_schema=input_schema, 
                        output_schema=output_schema
                        )
model
```

    Waiting for model loading - this will take up to 10.0min.
    Model is pending loading to a container runtime.
    Model is attempting loading to a container runtime...................successful
    
    Ready

<table>
        <tr>
          <td>Name</td>
          <td>hf-summarization</td>
        </tr>
        <tr>
          <td>Version</td>
          <td>4e129a02-79eb-4352-a4d8-157e1026ed08</td>
        </tr>
        <tr>
          <td>File Name</td>
          <td>model-auto-conversion_hugging-face_complex-pipelines_hf-summarisation-bart-large-samsun.zip</td>
        </tr>
        <tr>
          <td>SHA</td>
          <td>ee71d066a83708e7ca4a3c07caf33fdc528bb000039b6ca2ef77fa2428dc6268</td>
        </tr>
        <tr>
          <td>Status</td>
          <td>ready</td>
        </tr>
        <tr>
          <td>Image Path</td>
          <td>proxy.replicated.com/proxy/wallaroo/ghcr.io/wallaroolabs/mlflow-deploy:v2023.3.0-3798</td>
        </tr>
        <tr>
          <td>Updated At</td>
          <td>2023-19-Sep 20:04:40</td>
        </tr>
      </table>

### Reserve Pipeline Resources

Before deploying an inference engine we need to tell wallaroo what resources it will need.
To do this we will use the wallaroo DeploymentConfigBuilder() and fill in the options listed below to determine what the properties of our inference engine will be.

We will be testing this deployment for an edge scenario, so the resource specifications are kept small -- what's the minimum needed to meet the expected load on the planned hardware.

- cpus - 4 => allow the engine to use 4 CPU cores when running the neural net
- memory - 8Gi => each inference engine will have 8 GB of memory, which is plenty for processing a single image at a time.

```python
deployment_config = wallaroo.DeploymentConfigBuilder() \
    .cpus(0.25).memory('1Gi') \
    .sidekick_cpus(model, 4) \
    .sidekick_memory(model, "8Gi") \
    .build()
```

### Simulated Edge Deployment

We will now deploy our pipeline into the current Kubernetes environment using the specified resource constraints. This is a "simulated edge" deploy in that we try to mimic the edge hardware as closely as possible.

```python
pipeline = wl.build_pipeline(pipeline_name)
pipeline.add_model_step(model)

pipeline.deploy(deployment_config=deployment_config)
```

<table><tr><th>name</th> <td>edge-hf-summarization</td></tr><tr><th>created</th> <td>2023-09-19 20:04:42.054449+00:00</td></tr><tr><th>last_updated</th> <td>2023-09-19 20:04:42.795120+00:00</td></tr><tr><th>deployed</th> <td>True</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>e3d28748-cbe2-41ec-a566-dee7fc591a0a, d527c3c2-d5db-42a3-8b16-259558746fe1</td></tr><tr><th>steps</th> <td>hf-summarization</td></tr><tr><th>published</th> <td>False</td></tr></table>

```python
pipeline.status()
```

    {'status': 'Running',
     'details': [],
     'engines': [{'ip': '10.244.3.209',
       'name': 'engine-64b6c9f65d-j48w4',
       'status': 'Running',
       'reason': None,
       'details': [],
       'pipeline_statuses': {'pipelines': [{'id': 'edge-hf-summarization',
          'status': 'Running'}]},
       'model_statuses': {'models': [{'name': 'hf-summarization',
          'version': '4e129a02-79eb-4352-a4d8-157e1026ed08',
          'sha': 'ee71d066a83708e7ca4a3c07caf33fdc528bb000039b6ca2ef77fa2428dc6268',
          'status': 'Running'}]}}],
     'engine_lbs': [{'ip': '10.244.4.242',
       'name': 'engine-lb-584f54c899-xsjz4',
       'status': 'Running',
       'reason': None,
       'details': []}],
     'sidekicks': [{'ip': '10.244.3.210',
       'name': 'engine-sidekick-hf-summarization-60-6d959f7c95-x68qp',
       'status': 'Running',
       'reason': None,
       'details': [],
       'statuses': '\n'}]}

### Run Sample Inference

A single inference using sample input data is prepared below.  We'll run through it to verify the pipeline inference is working.

```python
input_data = {
        "inputs": ["LinkedIn (/lɪŋktˈɪn/) is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. It is now owned by Microsoft. The platform is primarily used for professional networking and career development, and allows jobseekers to post their CVs and employers to post jobs. From 2015 most of the company's revenue came from selling access to information about its members to recruiters and sales professionals. Since December 2016, it has been a wholly owned subsidiary of Microsoft. As of March 2023, LinkedIn has more than 900 million registered members from over 200 countries and territories. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships. Members can invite anyone (whether an existing member or not) to become a connection. LinkedIn can also be used to organize offline events, join groups, write articles, publish job postings, post photos and videos, and more"], # required
        "return_text": [True], # optional: using the defaults, similar to not passing this parameter
        "return_tensors": [False], # optional: using the defaults, similar to not passing this parameter
        "clean_up_tokenization_spaces": [False], # optional: using the defaults, similar to not passing this parameter
}
dataframe = pd.DataFrame(input_data)
dataframe
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>inputs</th>
      <th>return_text</th>
      <th>return_tensors</th>
      <th>clean_up_tokenization_spaces</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>LinkedIn (/lɪŋktˈɪn/) is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. It is now owned by Microsoft. The platform is primarily used for professional networking and career development, and allows jobseekers to post their CVs and employers to post jobs. From 2015 most of the company's revenue came from selling access to information about its members to recruiters and sales professionals. Since December 2016, it has been a wholly owned subsidiary of Microsoft. As of March 2023, LinkedIn has more than 900 million registered members from over 200 countries and territories. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships. Members can invite anyone (whether an existing member or not) to become a connection. LinkedIn can also be used to organize offline events, join groups, write articles, publish job postings, post photos and videos, and more</td>
      <td>True</td>
      <td>False</td>
      <td>False</td>
    </tr>
  </tbody>
</table>

```python
deploy_url = pipeline._deployment._url()

headers = wl.auth.auth_header()

headers['Content-Type']='application/json; format=pandas-records'
# headers['Content-Type']='application/json; format=pandas-records'
headers['Accept']='application/json; format=pandas-records'

dataFile = './data/test_summarization.df.json'
```

```python
!curl -X POST {deploy_url} \
     -H "Authorization:{headers['Authorization']}" \
     -H "Content-Type:{headers['Content-Type']}" \
     -H "Accept:{headers['Accept']}" \
     --data-binary @{dataFile}
```

    [{"time":1695153942490,"in":{"clean_up_tokenization_spaces":false,"inputs":"LinkedIn (/lɪŋktˈɪn/) is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. It is now owned by Microsoft. The platform is primarily used for professional networking and career development, and allows jobseekers to post their CVs and employers to post jobs. From 2015 most of the company's revenue came from selling access to information about its members to recruiters and sales professionals. Since December 2016, it has been a wholly owned subsidiary of Microsoft. As of March 2023, LinkedIn has more than 900 million registered members from over 200 countries and territories. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships. Members can invite anyone (whether an existing member or not) to become a connection. LinkedIn can also be used to organize offline events, join groups, write articles, publish job postings, post photos and videos, and more","return_tensors":false,"return_text":true},"out":{"summary_text":"LinkedIn is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships."},"check_failures":[],"metadata":{"last_model":"{\"model_name\":\"hf-summarization\",\"model_sha\":\"ee71d066a83708e7ca4a3c07caf33fdc528bb000039b6ca2ef77fa2428dc6268\"}","pipeline_version":"e3d28748-cbe2-41ec-a566-dee7fc591a0a","elapsed":[49501,4294967295],"dropped":[]}}]

### Undeploy the Pipeline

Just to clear up resources, we'll undeploy the pipeline.

```python
pipeline.undeploy()
```

<table><tr><th>name</th> <td>edge-hf-summarization</td></tr><tr><th>created</th> <td>2023-09-19 20:04:42.054449+00:00</td></tr><tr><th>last_updated</th> <td>2023-09-19 20:04:42.795120+00:00</td></tr><tr><th>deployed</th> <td>False</td></tr><tr><th>tags</th> <td></td></tr><tr><th>versions</th> <td>e3d28748-cbe2-41ec-a566-dee7fc591a0a, d527c3c2-d5db-42a3-8b16-259558746fe1</td></tr><tr><th>steps</th> <td>hf-summarization</td></tr><tr><th>published</th> <td>False</td></tr></table>

### Publish the Pipeline for Edge Deployment

It worked! For a demo, we'll take working once as "tested". So now that we've tested our pipeline, we are ready to publish it for edge deployment.

Publishing it means assembling all of the configuration files and model assets and pushing them to an Open Container Initiative (OCI) repository set in the Wallaroo instance as the Edge Registry service.  DevOps engineers then retrieve that image and deploy it through Docker, Kubernetes, or similar deployments.

See [Edge Deployment Registry Guide](https://staging.docs.wallaroo.ai/wallaroo-operations-guide/wallaroo-configuration/wallaroo-edge-deployment/) for details on adding an OCI Registry Service to Wallaroo as the Edge Deployment Registry.

This is done through the SDK command `wallaroo.pipeline.publish(deployment_config)` which has the following parameters and returns.

#### Publish a Pipeline Parameters

The `publish` method takes the following parameters.  The containerized pipeline will be pushed to the Edge registry service with the model, pipeline configurations, and other artifacts needed to deploy the pipeline.

| Parameter | Type | Description |
|---|---|---|
| `deployment_config` | `wallaroo.deployment_config.DeploymentConfig` (*Optional*) | Sets the pipeline deployment configuration.  For example:    For more information on pipeline deployment configuration, see the [Wallaroo SDK Essentials Guide: Pipeline Deployment Configuration]({{<ref "wallaroo-sdk-essentials-pipeline-deployment-config">}}).

#### Publish a Pipeline Returns

| Field | Type | Description |
|---|---|---|
| id | integer | Numerical Wallaroo id of the published pipeline. |
| pipeline version id | integer | Numerical Wallaroo id of the pipeline version published. |
| status | string | The status of the pipeline publication.  Values include:  <ul><li>PendingPublish: The pipeline publication is about to be uploaded or is in the process of being uploaded.</li><li>Published:  The pipeline is published and ready for use.</li></ul> |
| Engine URL | string | The URL of the published pipeline engine in the edge registry. |
| Pipeline URL | string | The URL of the published pipeline in the edge registry. |
| Helm Chart URL | string | The URL of the helm chart for the published pipeline in the edge registry. |
| Helm Chart Reference | string | The help chart reference. |
| Helm Chart Version | string | The version of the Helm Chart of the published pipeline.  This is also used as the Docker tag. |
| Engine Config | `wallaroo.deployment_config.DeploymentConfig` | The pipeline configuration included with the published pipeline. |
| Created At | DateTime | When the published pipeline was created. |
| Updated At | DateTime | When the published pipeline was updated. |

### Publish Example

We will now publish the pipeline to our Edge Deployment Registry with the `pipeline.publish(deployment_config)` command.  `deployment_config` is an optional field that specifies the pipeline deployment.  This can be overridden by the DevOps engineer during deployment.

```python
## This may still show an error status despite but if both containers show running it should be good to go
pipeline.publish(deployment_config)
```

    Waiting for pipeline publish... It may take up to 600 sec.
    Pipeline is Publishing..........................Published.

<table>
    <tr><td>ID</td><td>2</td></tr>
    <tr><td>Pipeline Version</td><td>c9b3a503-f408-467a-bdbb-7091fcdcaf79</td></tr>
    <tr><td>Status</td><td>Published</td></tr>
    <tr><td>Engine URL</td><td><a href='https://us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/engines/proxy/wallaroo/ghcr.io/wallaroolabs/standalone-mini:v2023.3.0-3798'>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/engines/proxy/wallaroo/ghcr.io/wallaroolabs/standalone-mini:v2023.3.0-3798</a></td></tr>
    <tr><td>Pipeline URL</td><td><a href='https://us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/pipelines/edge-hf-summarization:c9b3a503-f408-467a-bdbb-7091fcdcaf79'>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/pipelines/edge-hf-summarization:c9b3a503-f408-467a-bdbb-7091fcdcaf79</a></td></tr>
    <tr><td>Helm Chart URL</td><td><a href='https://us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/charts/edge-hf-summarization'>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/charts/edge-hf-summarization</a></td></tr>
    <tr><td>Helm Chart Reference</td><td>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/charts@sha256:0de0a27b158d7eb19e1885ccce5606043dabbf04e1e39d40582dc979fc711539</td></tr>
    <tr><td>Helm Chart Version</td><td>0.0.1-c9b3a503-f408-467a-bdbb-7091fcdcaf79</td></tr>
    <tr><td>Engine Config</td><td>{'engine': {'resources': {'limits': {'cpu': 1.0, 'memory': '512Mi'}, 'requests': {'cpu': 1.0, 'memory': '512Mi'}}}, 'engineAux': {'images': {}}, 'enginelb': {'resources': {'limits': {'cpu': 1.0, 'memory': '512Mi'}, 'requests': {'cpu': 1.0, 'memory': '512Mi'}}}}</td></tr>
    <tr><td>User Images</td><td>[]</td></tr>
    <tr><td>Created By</td><td>john.hummel@wallaroo.ai</td></tr>
    <tr><td>Created At</td><td>2023-09-08 20:04:49.622330+00:00</td></tr>
    <tr><td>Updated At</td><td>2023-09-08 20:04:49.622330+00:00</td></tr>
</table>

### List Published Pipeline

The method `wallaroo.client.list_pipelines()` shows a list of all pipelines in the Wallaroo instance, and includes the `published` field that indicates whether the pipeline was published to the registry (`True`), or has not yet been published (`False`).

```python
wl.list_pipelines()
```

<table><tr><th>name</th><th>created</th><th>last_updated</th><th>deployed</th><th>tags</th><th>versions</th><th>steps</th><th>published</th></tr><tr><td>edge-hf-summarization</td><td>2023-08-Sep 20:03:12</td><td>2023-08-Sep 20:04:49</td><td>False</td><td></td><td>c9b3a503-f408-467a-bdbb-7091fcdcaf79, 8f9823c6-eb8a-45e7-b372-9b424dec2262, b0b85c48-ba1f-4ae6-875a-9e456d7dcc1c</td><td>hf-summarization</td><td>True</td></tr><tr><td>arm-arbitrary-python-example</td><td>2023-08-Sep 15:04:25</td><td>2023-08-Sep 15:04:40</td><td>False</td><td></td><td>2e01c9da-bd71-4481-a9fe-e5b5d0240487, 6ed1a701-b424-41c8-833c-1d203b329391</td><td>vgg16-clustering</td><td>False</td></tr></table>

### List Publishes from a Pipeline

All publishes created from a pipeline are displayed with the `wallaroo.pipeline.publishes` method.  The `pipeline_version_id` is used to know what version of the pipeline was used in that specific publish.  This allows for pipelines to be updated over time, and newer versions to be sent and tracked to the Edge Deployment Registry service.

#### List Publishes Parameters

N/A

#### List Publishes Returns

A List of the following fields:

| Field | Type | Description |
|---|---|---|
| id | integer | Numerical Wallaroo id of the published pipeline. |
| pipeline_version_id | integer | Numerical Wallaroo id of the pipeline version published. |
| engine_url | string | The URL of the published pipeline engine in the edge registry. |
| pipeline_url | string | The URL of the published pipeline in the edge registry. |
| created_by | string | The email address of the user that published the pipeline.
| Created At | DateTime | When the published pipeline was created. |
| Updated At | DateTime | When the published pipeline was updated. |

```python
pipeline.publishes()
```

<table><tr><th>id</th><th>pipeline_version_name</th><th>engine_url</th><th>pipeline_url</th><th>created_by</th><th>created_at</th><th>updated_at</th></tr><tr><td>2</td><td>c9b3a503-f408-467a-bdbb-7091fcdcaf79</td><td><a href='https://us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/engines/proxy/wallaroo/ghcr.io/wallaroolabs/standalone-mini:v2023.3.0-3798'>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/engines/proxy/wallaroo/ghcr.io/wallaroolabs/standalone-mini:v2023.3.0-3798</a></td><td><a href='https://us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/pipelines/edge-hf-summarization:c9b3a503-f408-467a-bdbb-7091fcdcaf79'>us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/pipelines/edge-hf-summarization:c9b3a503-f408-467a-bdbb-7091fcdcaf79</a></td><td>john.hummel@wallaroo.ai</td><td>2023-08-Sep 20:04:49</td><td>2023-08-Sep 20:04:49</td></tr></table>

```python
pub = pipeline.publishes()[0]
```

## DevOps - Pipeline Edge Deployment

Once a pipeline is deployed to the Edge Registry service, it can be deployed in environments such as Docker, Kubernetes, or similar container running services by a DevOps engineer.

### Docker Deployment

First, the DevOps engineer must authenticate to the same OCI Registry service used for the Wallaroo Edge Deployment registry.

For more details, check with the documentation on your artifact service.  The following are provided for the three major cloud services:

* [Set up authentication for Docker](https://cloud.google.com/artifact-registry/docs/docker/authentication)
* [Authenticate with an Azure container registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication?tabs=azure-cli)
* [Authenticating Amazon ECR Repositories for Docker CLI with Credential Helper](https://aws.amazon.com/blogs/compute/authenticating-amazon-ecr-repositories-for-docker-cli-with-credential-helper/)

For the deployment, the engine URL is specified with the following environmental variables:

* `DEBUG` (true|false): Whether to include debug output.
* `OCI_REGISTRY`: The URL of the registry service.
* `CONFIG_CPUS`: The number of CPUs to use.
* `OCI_USERNAME`: The edge registry username.
* `OCI_PASSWORD`:  The edge registry password or token.
* `PIPELINE_URL`: The published pipeline URL.

#### Docker Deployment Example

Using our sample environment, here's sample deployment using Docker with a computer vision ML model, the same used in the [Wallaroo Use Case Tutorials Computer Vision: Retail]({{<ref "use-case-computer-vision-retail">}}) tutorials.

```bash
docker run -p 8080:8080 \
    -e DEBUG=true -e OCI_REGISTRY={your registry server} \
    -e CONFIG_CPUS=4 \
    -e OCI_USERNAME=oauth2accesstoken \
    -e OCI_PASSWORD={registry token here} \
    -e PIPELINE_URL={your registry server}/pipelines/edge-cv-retail:bf70eaf7-8c11-4b46-b751-916a43b1a555 \
    {your registry server}/engine:v2023.3.0-main-3707
```

### Docker Compose Deployment

For users who prefer to use `docker compose`, the following sample `compose.yaml` file is used to launch the Wallaroo Edge pipeline.  This is the same used in the [Wallaroo Use Case Tutorials Computer Vision: Retail]({{<ref "use-case-computer-vision-retail">}}) tutorials.

```yml
services:
  engine:
    image: {Your Engine URL}
    ports:
      - 8080:8080
    environment:
      PIPELINE_URL: {Your Pipeline URL}
      OCI_REGISTRY: {Your Edge Registry URL}
      OCI_USERNAME:  {Your Registry Username}
      OCI_PASSWORD: {Your Token or Password}
      CONFIG_CPUS: 4
```

For example:

```yml
services:
  engine:
    image: sample-registry.com/engine:v2023.3.0-main-3707
    ports:
      - 8080:8080
    environment:
      PIPELINE_URL: sample-registry.com/pipelines/edge-cv-retail:bf70eaf7-8c11-4b46-b751-916a43b1a555
      OCI_REGISTRY: sample-registry.com
      OCI_USERNAME:  _json_key_base64
      OCI_PASSWORD: abc123
      CONFIG_CPUS: 4
```

#### Docker Compose Deployment Example

The deployment and undeployment is then just a simple `docker compose up` and `docker compose down`.  The following shows an example of deploying the Wallaroo edge pipeline using `docker compose`.

```bash
docker compose up
[+] Running 1/1
 ✔ Container cv_data-engine-1  Recreated                                                                                                                                                                 0.5s
Attaching to cv_data-engine-1
cv_data-engine-1  | Wallaroo Engine - Standalone mode
cv_data-engine-1  | Login Succeeded
cv_data-engine-1  | Fetching manifest and config for pipeline: sample-registry.com/pipelines/edge-cv-retail:bf70eaf7-8c11-4b46-b751-916a43b1a555
cv_data-engine-1  | Fetching model layers
cv_data-engine-1  | digest: sha256:c6c8869645962e7711132a7e17aced2ac0f60dcdc2c7faa79b2de73847a87984
cv_data-engine-1  |   filename: c6c8869645962e7711132a7e17aced2ac0f60dcdc2c7faa79b2de73847a87984
cv_data-engine-1  |   name: resnet-50
cv_data-engine-1  |   type: model
cv_data-engine-1  |   runtime: onnx
cv_data-engine-1  |   version: 693e19b5-0dc7-4afb-9922-e3f7feefe66d
cv_data-engine-1  |
cv_data-engine-1  | Fetched
cv_data-engine-1  | Starting engine
cv_data-engine-1  | Looking for preexisting `yaml` files in //modelconfigs
cv_data-engine-1  | Looking for preexisting `yaml` files in //pipelines
```

### Helm Deployment

Published pipelines can be deployed through the use of helm charts.

Helm deployments take up to two steps - the first step is in retrieving the required `values.yaml` and making updates to override.

1. Pull the helm charts from the published pipeline.  The two fields are the Helm Chart URL and the Helm Chart version to specify the OCI .    This typically takes the format of:

  ```bash
  helm pull oci://{published.helm_chart_url} --version {published.helm_chart_version}
  ```

1. Extract the `tgz` file and copy the `values.yaml` and copy the values used to edit engine allocations, etc.  The following are **required** for the deployment to run:

  ```yml
  ociRegistry:
    registry: {your registry service}
    username:  {registry username here}
    password: {registry token here}
  ```

  Store this into another file, suc as `local-values.yaml`.

1. Create the namespace to deploy the pipeline to.  For example, the namespace `wallaroo-edge-pipeline` would be:

  ```bash
  kubectl create -n wallaroo-edge-pipeline
  ```

1. Deploy the `helm` installation with `helm install` through one of the following options:
    1. Specify the `tgz` file that was downloaded and the local values file.  For example:

        ```bash
        helm install --namespace {namespace} --values {local values file} {helm install name} {tgz path}
        ```

    1. Specify the expended directory from the downloaded `tgz` file.

        ```bash
        helm install --namespace {namespace} --values {local values file} {helm install name} {helm directory path}
        ```

    1. Specify the Helm Pipeline Helm Chart and the Pipeline Helm Version.

        ```bash
        helm install --namespace {namespace} --values {local values file} {helm install name} oci://{published.helm_chart_url} --version {published.helm_chart_version}
        ```

1. Once deployed, the DevOps engineer will have to forward the appropriate ports to the `svc/engine-svc` service in the specific pipeline.  For example, using `kubectl port-forward` to the namespace `ccfraud` that would be:

    ```bash
    kubectl port-forward svc/engine-svc -n ccfraud01 8080 --address 0.0.0.0`
    ```

The following code segment generates a `docker compose` template based on the previously published pipeline.

```python
docker_compose = f'''
services:
  engine:
    image: {pub.engine_url}
    ports:
      - 8080:8080
    environment:
      PIPELINE_URL: {pub.pipeline_url}
      OCI_USERNAME: YOUR USERNAME 
      OCI_PASSWORD: YOUR PASSWORD OR TOKEN
      OCI_REGISTRY: us-central1-docker.pkg.dev
      CONFIG_CPUS: 4
'''

print(docker_compose)
```

    
    services:
      engine:
        image: us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/engines/proxy/wallaroo/ghcr.io/wallaroolabs/standalone-mini:v2023.3.0-3798
        ports:
          - 8080:8080
        environment:
          PIPELINE_URL: us-central1-docker.pkg.dev/wallaroo-dev-253816/uat/pipelines/edge-hf-summarization:c9b3a503-f408-467a-bdbb-7091fcdcaf79
          OCI_USERNAME: YOUR USERNAME 
          OCI_PASSWORD: YOUR PASSWORD OR TOKEN
          OCI_REGISTRY: us-central1-docker.pkg.dev
          CONFIG_CPUS: 4
    

## Edge Deployed Pipeline API Endpoints

Once deployed, we can check the pipelines and models available.  We'll use a `curl` command, but any HTTP based request will work the same way.

The endpoint `/pipelines` returns:

* **id** (*String*):  The name of the pipeline.
* **status** (*String*):  The status as either `Running`, or `Error` if there are any issues.

```bash
curl localhost:8080/pipelines
{"pipelines":[{"id":"edge-cv-retail","status":"Running"}]}
```

```python
!curl testboy.local:8080/pipelines
```

    {"pipelines":[{"id":"edge-hf-summarization","status":"Running"}]}

The endpoint `/models` returns a List of models with the following fields:

* **name** (*String*): The model name.
* **sha** (*String*): The sha hash value of the ML model.
* **status** (*String*):  The status of either Running or Error if there are any issues.
* **version** (*String*):  The model version.  This matches the version designation used by Wallaroo to track model versions in UUID format.

```bash
curl localhost:8080/models
{"models":[{"name":"resnet-50","sha":"c6c8869645962e7711132a7e17aced2ac0f60dcdc2c7faa79b2de73847a87984","status":"Running","version":"693e19b5-0dc7-4afb-9922-e3f7feefe66d"}]}
```

```python
!curl testboy.local:8080/models
```

    {"models":[{"name":"hf-summarization","sha":"ee71d066a83708e7ca4a3c07caf33fdc528bb000039b6ca2ef77fa2428dc6268","status":"Running","version":"995b2e0e-1b2d-4d67-91e9-03cb72504f68"}]}

```python
!curl -X POST http://testboy.local:8080/pipelines/edge-hf-summarization -H "Content-Type: application/json; format=pandas-records" -d @./data/test_summarization.df.json
```

    [{"check_failures":[],"elapsed":[223661,2956592525],"model_name":"hf-summarization","model_version":"995b2e0e-1b2d-4d67-91e9-03cb72504f68","original_data":null,"outputs":[{"String":{"data":["LinkedIn is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships."],"dim":[1,1],"v":1}}],"pipeline_name":"edge-hf-summarization","shadow_data":{},"time":1694204017812}]

### Edge Inference Endpoint

The inference endpoint takes the following pattern:

* `/pipelines/{pipeline-name}`:  The `pipeline-name` is the same as returned from the [`/pipelines`](#list-pipelines) endpoint as `id`.

Wallaroo inference endpoint URLs accept the following data inputs through the `Content-Type` header:

* `Content-Type: application/vnd.apache.arrow.file`: For Apache Arrow tables.
* `Content-Type: application/json; format=pandas-records`: For pandas DataFrame in record format.

Once deployed, we can perform an inference through the deployment URL.

The endpoint returns `Content-Type: application/json; format=pandas-records` by default with the following fields:

* **check_failures** (*List[Integer]*): Whether any validation checks were triggered.  For more information, see [Wallaroo SDK Essentials Guide: Pipeline Management: Anomaly Testing]({{<ref "wallaroo-sdk-essentials-pipeline#anomaly-testing">}}).
* **elapsed** (*List[Integer]*): A list of time in nanoseconds for:
  * [0] The time to serialize the input.
  * [1...n] How long each step took.
* **model_name** (*String*): The name of the model used.
* **model_version** (*String*): The version of the model in UUID format.
* **original_data**: The original input data.  Returns `null` if the input may be too long for a proper return.
* **outputs** (*List*): The outputs of the inference result separated by data type, where each data type includes:
  * **data**: The returned values.
  * **dim** (*List[Integer]*): The dimension shape returned.
  * **v** (*Integer*): The vector shape of the data.
* **pipeline_name**  (*String*): The name of the pipeline.
* **shadow_data**: Any shadow deployed data inferences in the same format as **outputs**.
* **time** (*Integer*): The time since UNIX epoch.

```python
import json
import requests
import pandas as pd

# set the content type and accept headers
headers = {
    'Content-Type': 'application/json; format=pandas-records'
}

# Submit arrow file
dataFile="./data/test_summarization.df.json"

data = json.load(open(dataFile))

host = 'http://testboy.local:8080'

deployurl = f'{host}/pipelines/edge-hf-summarization'

response = requests.post(
                    deployurl, 
                    headers=headers, 
                    json=data, 
                    verify=True
                )

# display(response)
display(pd.DataFrame(response.json()).loc[0, ['outputs']][0][0]['String']['data'][0])

```

    'LinkedIn is a business and employment-focused social media platform that works through websites and mobile apps. It launched on May 5, 2003. LinkedIn allows members (both workers and employers) to create profiles and connect with each other in an online social network which may represent real-world professional relationships.'
