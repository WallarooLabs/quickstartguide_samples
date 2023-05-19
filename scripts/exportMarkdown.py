#!/usr/bin/env python

"""
Converts the following Python notebooks into the same format used for the Wallaroo Documentation site.

This uses the jupyter nbconvert command.  For now this will always assume we're exporting to markdown:

    jupyter nbconvert {file} --to markdown --output {output}

"""

import os
import nbformat
from traitlets.config import Config
import re
import shutil
import glob
#import argparse

c = Config()

c.NbConvertApp.export_format = "markdown"

docs_directory = "docs/markdown"

fileList = [
    # {
    #     "inputFile": "wallaroo-model-cookbooks/aloha/aloha_demo.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-quick-start-aloha-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/demand_curve/demandcurve_demo.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-quick-start-demandcurve-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/imdb/imdb_sample.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-quick-start-imdb-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/model_insights/model-insights.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-model-insights-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/shadow_deploy/shadow_deployment_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-shadow-deployment-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-101/Wallaroo-101.ipynb",
    #     "outputDir": "/wallaroo-101/",
    #     "outputFile": "wallaroo-101-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/autoconversion-tutorial/auto-convert-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "sklearn-auto-conversion-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/keras-to-onnx/autoconvert-keras-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "keras-auto-conversion-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/pytorch-to-onnx/pytorch-to-onnx.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "pytorch-to-onnx-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/sklearn-classification-to-onnx/convert-sklearn-classification-to-onnx.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "sklearn-logistic-to-onnx-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/sklearn-regression-to-onnx/convert-sklearn-regression-to-onnx.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "sklearn-regression-to-onnx-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/statsmodels/convert-statsmodel-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "statsmodel-conversion-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/xgboost-autoconversion/xgboost-autoconversion-classification-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "xgboost-autoconversion-classification-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/xgboost-autoconversion/xgboost-autoconversion-regression-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "xgboost-autoconversion-regression-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/simulated_edge/simulated_edge.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-simulated_edge-reference.md"
    # },
    # {
    #     "inputFile": "notebooks_in_prod/00_notebooks_in_prod_Introduction.ipynb",
    #     "outputDir": "/wallaroo-tutorials/notebook_in_prod",
    #     "outputFile": "_index.md"
    # },
    # {
    #     "inputFile": "notebooks_in_prod/01_notebooks_in_prod_explore_and_train.ipynb",
    #     "outputDir": "/wallaroo-tutorials/notebook_in_prod",
    #     "outputFile": "01_notebooks_in_prod_explore_and_train-reference.md"
    # },
    # {
    #     "inputFile": "notebooks_in_prod/02_notebooks_in_prod_automated_training_process.ipynb",
    #     "outputDir": "/wallaroo-tutorials/notebook_in_prod",
    #     "outputFile": "02_notebooks_in_prod_automated_training_process-reference.md"
    # },
    # {
    #     "inputFile": "notebooks_in_prod/03_notebooks_in_prod_deploy_model.ipynb",
    #     "outputDir": "/wallaroo-tutorials/notebook_in_prod",
    #     "outputFile": "03_notebooks_in_prod_deploy_model-reference.md"
    # },
    # {
    #     "inputFile": "notebooks_in_prod/04_notebooks_in_prod_regular_batch_inferences.ipynb",
    #     "outputDir": "/wallaroo-tutorials/notebook_in_prod",
    #     "outputFile": "04_notebooks_in_prod_regular_batch_inferences-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/abtesting/wallaroo-abtesting-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-abtesting-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/anomaly_detection/wallaroo-anomaly-detection.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-anomaly-detection-reference.md"
    # },
    # {
    #     "inputFile": "model_conversion/xgboost-to-onnx/xgboost-to-onnx.ipynb",
    #     "outputDir": "/wallaroo-tutorials/conversion-tutorials",
    #     "outputFile": "xgboost-to-onnx-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/wallaroo-model-endpoints/wallaroo-model-endpoints-api.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-model-endpoints",
    #     "outputFile": "wallaroo-model-endpoints-api-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/wallaroo-model-endpoints/wallaroo-model-endpoints-sdk.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-model-endpoints",
    #     "outputFile": "wallaroo-model-endpoints-setup-reference.md"
    # },
    # {
    #     "inputFile": "development/sdk-install-guides/google-vertex-sdk-install/install-wallaroo-sdk-google-vertex-guide.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-sdk-guides/",
    #     "outputFile": "install-wallaroo-sdk-google-vertex-guide-reference.md"
    # },
    # {
    #     "inputFile": "development/sdk-install-guides/standard-install/install-wallaroo-sdk-standard-guide.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-sdk-guides/",
    #     "outputFile": "install-wallaroo-sdk-standard-guide-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/wallaroo-tag-management/wallaroo-tags-guide.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features/",
    #     "outputFile": "wallaroo-tags-guide-reference.md"
    # },
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides/",
    #     "outputFile": "wallaroo-mlops-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "development/sdk-install-guides/azure-ml-sdk-install/install-wallaroo-sdk-azureml-guide.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-sdk-guides/",
    #     "outputFile": "install-wallaroo-sdk-azureml-guide-reference.md"
    # },
    # {
    #     "inputFile": "development/sdk-install-guides/aws-sagemaker-install/install-wallaroo-aws-sagemaker-guide.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-sdk-guides/",
    #     "outputFile": "install-wallaroo-sdk-aws-sagemaker-guide-reference.md"
    # },
    # {
    #     "inputFile": "development/sdk-install-guides/databricks-azure-sdk-install/install-wallaroo-sdk-databricks-azure-guide.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-sdk-guides/",
    #     "outputFile": "install-wallaroo-sdk-databricks-azure-guide-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/mlflow-tutorial/wallaroo-mlflow-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-mlflow-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/model_hot_swap/wallaroo_hot_swap_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-hot-swap-models-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision/00_computer_vision_tutorial_intro.ipynb",
    #     "outputDir": "/wallaroo-tutorials/computer-vision",
    #     "outputFile": "00-computer-vision-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision/01_computer_vision_tutorial_mobilenet.ipynb",
    #     "outputDir": "/wallaroo-tutorials/computer-vision",
    #     "outputFile": "01_computer_vision_tutorial_mobilenet-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision/02_computer_vision_tutorial_resnet50.ipynb",
    #     "outputDir": "/wallaroo-tutorials/computer-vision",
    #     "outputFile": "02_computer_vision_tutorial_resnet50-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision/03_computer_vision_tutorial_shadow_deploy.ipynb",
    #     "outputDir": "/wallaroo-tutorials/computer-vision",
    #     "outputFile": "03_computer_vision_tutorial_shadow_deploy-reference.md"
    # },
    # {
    #     "inputFile": "tools/convert_wallaroo_data_to_pandas_arrow/convert_wallaroo_inference_data.ipynb",
    #     "outputDir": "/wallaroo-tutorials/tools/",
    #     "outputFile": "convert_wallaroo_data_inference-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/houseprice-saga/house-price-model-saga.ipynb",
    #     "outputDir": "/wallaroo-tutorials/testing-tutorials/",
    #     "outputFile": "house-price-model-saga.md"
    # },
    {
        "inputFile": "pipeline-orchestrators/connection_api_bigquery_tutorial/connection_api_bigquery_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "connection_api_bigquery_tutorial.md"
    },
    {
        "inputFile": "pipeline-orchestrators/orchestration_api_simple_tutorial/data_orchestrators_api_simple_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "data_orchestrators_api_simple_tutorial.md"
    },
    {
        "inputFile": "pipeline-orchestrators/orchestration_sdk_bigquery_houseprice_tutorial/orchestration_sdk_bigquery_houseprice_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "orchestration_sdk_bigquery_houseprice_tutorial.md"
    },
    {
        "inputFile": "pipeline-orchestrators/orchestration_sdk_bigquery_statsmodel_tutorial/orchestration_sdk_bigquery_statsmodel_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "orchestration_sdk_bigquery_statsmodel_tutorial.md"
    },
    {
        "inputFile": "pipeline-orchestrators/orchestration_sdk_comprehensive_tutorial/data_connectors_and_orchestrators_comprehensive_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "data_connectors_and_orchestrators_comprehensive_tutorial.md"
    },
    {
        "inputFile": "pipeline-orchestrators/orchestration_sdk_simple_tutorial/data_connectors_and_orchestrators_simple_tutorial.ipynb",
        "outputDir": "/wallaroo-tutorials/pipeline-orchestrations",
        "outputFile": "data_connectors_and_orchestrators_simple_tutorial.md"
    },
    # {
    #     "inputFile": "wallaroo-features/pipeline_log_tutorial/pipeline_log_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "pipeline_log_tutorial.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/pipeline_api_log_tutorial/pipeline_api_log_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "pipeline_api_log_tutorial.md"
    # },

]

def format(outputdir, document_file):
    # Take the markdown file, remove the extra spaces
    document = open(f'{docs_directory}{outputdir}/{document_file}', "r").read()
    result = re.sub
    
    # fix tables for publication
    document = re.sub(r'<table.*?>', r'{{<table "table table-striped table-bordered" >}}\n<table>', document)
    document = re.sub('</table>', r'</table>\n{{</table>}}', document)
    # remove any div table sections
    document = re.sub('<div.*?>', '', document)
    document = re.sub(r'<style.*?>.*?</style>', '', document, flags=re.S)
    document = re.sub('</div>', '', document)

    # remove non-public domains
    document = re.sub('wallaroocommunity.ninja', 'wallarooexample.ai', document)

    # fix image directories
    # ](01_notebooks_in_prod_explore_and_train-reference_files
    # image_replace = f'![png]({outputdir}'
    document = re.sub('!\[png\]\(', f'![png](/images/current{outputdir}/', document)
    document = re.sub('\(./images', '(/images/current', document)
    # move them all to Docsy figures
    document = re.sub(r'!\[(.*?)\]\((.*?)\)', r'{{<figure src="\2" width="800" label="\1">}}', document)

    # fix github link for final release
    document = re.sub('https://github.com/WallarooLabs/Wallaroo_Tutorials/blob/20230314_2023.2_updates/', 
                      'https://github.com/WallarooLabs/Wallaroo_Tutorials/tree/main/', 
                      document)
   # document = re.sub('![png](', 'bob', document)

    # strip the excess newlines - match any pattern of newline plus another one or more empty newlines
    document = re.sub(r'\n[\n]+', r'\n\n', document)

    # save the file for publishing
    newdocument = open(f'{docs_directory}{outputdir}/{document_file}', "w")
    newdocument.write(document)
    newdocument.close()

def move_images(image_directory):
    source_directory = f"{docs_directory}{image_directory}"
    target_directory = f"./images{image_directory}"
    # check the current directory for reference files
    # reference_directories = os.listdir(image_directory)
    print(source_directory)
    reference_directories = [ name for name in os.listdir(source_directory) if os.path.isdir(os.path.join(source_directory, name)) ]
    # copy only the directories to their image location
    for reference in reference_directories:
        print(f"cp -rf ./{source_directory}/{reference} {target_directory}")
        # print(f"To: {target_directory}/{reference}")
        os.system(f"cp -rf ./{source_directory}/{reference} {target_directory}")

def main():
    for currentFile in fileList:
        convert_cmd = f'jupyter nbconvert --to markdown --output-dir {docs_directory}{currentFile["outputDir"]} --output {currentFile["outputFile"]} {currentFile["inputFile"]}'
        print(convert_cmd)
        os.system(convert_cmd)
        # format(f'{docs_directory}{currentFile["outputDir"]}/{currentFile["outputFile"]}')
        format(currentFile["outputDir"],currentFile["outputFile"])
        move_images(currentFile["outputDir"])
    # get rid of any extra markdown files
    os.system("find ./images -name '*.md' -type f -delete")

if __name__ == '__main__':
    main()