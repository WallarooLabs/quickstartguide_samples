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
    # @TODO: UNPUBLISHED
    # {
    #     "inputFile": "wallaroo-features/parallel-inference-aloha-tutorial/parallel-infer-with-aloha.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "parallel-infer-with-aloha-reference.md"
    # },
    # wallaroo 101
    {
        "inputFile": "wallaroo-101/Wallaroo-101.ipynb",
        "outputDir": "/wallaroo-101/",
        "outputFile": "wallaroo-101-reference.md"
    },
        ## deploy and serve
    ## model registry
    {
        "inputFile": "wallaroo-model-deploy-and-serve/mlflow-registries-upload-tutorials/Wallaroo-model-registry-demonstration.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/model-registry",
        "outputFile": "Wallaroo-model-registry-demonstration-reference.md"
    },
    ## keras
    {
        "inputFile": "wallaroo-model-deploy-and-serve/keras-upload-tutorials/wallaroo-upload-keras_sequential_model_single_io.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/keras",
        "outputFile": "wallaroo-upload-keras_sequential_model_single_io-reference.md"
    },
    ## hugging face
    {
        "inputFile": "wallaroo-model-deploy-and-serve/hugging-face-upload-tutorials/wallaroo-api-upload-hf-zero_shot_classification.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/hugging-face",
        "outputFile": "wallaroo-api-upload-hf-zero_shot_classification.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/hugging-face-upload-tutorials/wallaroo-sdk-upload-hf-zero_shot_classification.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/hugging-face",
        "outputFile": "wallaroo-sdk-upload-hf-zero_shot_classification.md"
    },
    ## computer vision
    {
        "inputFile": "wallaroo-model-deploy-and-serve/computer-vision/00_computer_vision_tutorial_intro.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/computer-vision",
        "outputFile": "00-computer-vision-tutorial-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/computer-vision/01_computer_vision_tutorial_mobilenet.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/computer-vision",
        "outputFile": "01_computer_vision_tutorial_mobilenet-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/computer-vision/02_computer_vision_tutorial_resnet50.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/computer-vision",
        "outputFile": "02_computer_vision_tutorial_resnet50-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/computer-vision/03_computer_vision_tutorial_shadow_deploy.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/computer-vision",
        "outputFile": "03_computer_vision_tutorial_shadow_deploy-reference.md"
    },
    ## BYOP
    {
        "inputFile": "wallaroo-model-deploy-and-serve/arbitrary-python-upload-tutorials/00_wallaroo-upload-arbitrary-python-vgg16-model-generation.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/arbitrary-python",
        "outputFile": "00_wallaroo-upload-arbitrary-python-vgg16-model-generation-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/arbitrary-python-upload-tutorials/01_wallaroo-upload-arbitrary-python-vgg16-model-deployment.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/arbitrary-python",
        "outputFile": "01_wallaroo-upload-arbitrary-python-vgg16-model-deployment-reference.md"
    },
    ## Python steps
    {
        "inputFile": "wallaroo-model-deploy-and-serve/python-upload-tutorials/python-step-dataframe-output-logging-example-sdk.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve",
        "outputFile": "python-step-dataframe-output-logging-example-sdk-reference.md"
    },
    ## notebooks in prod
    {
        "inputFile": "wallaroo-model-deploy-and-serve/notebooks_in_prod/00_notebooks_in_prod_introduction.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/notebook_in_prod",
        "outputFile": "_index.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/notebooks_in_prod/01_notebooks_in_prod_explore_and_train.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/notebook_in_prod",
        "outputFile": "01_notebooks_in_prod_explore_and_train-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/notebooks_in_prod/02_notebooks_in_prod_automated_training_process.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/notebook_in_prod",
        "outputFile": "02_notebooks_in_prod_automated_training_process-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/notebooks_in_prod/03_notebooks_in_prod_deploy_model_python.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/notebook_in_prod",
        "outputFile": "03_notebooks_in_prod_deploy_model-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/notebooks_in_prod/04_notebooks_in_prod_regular_batch_inferences.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/notebook_in_prod",
        "outputFile": "04_notebooks_in_prod_regular_batch_inferences-reference.md"
    },
    ## pytorch
    {
        "inputFile": "wallaroo-model-deploy-and-serve/pytorch-upload-tutorials/wallaroo-upload-pytorch-multi-input-output.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/pytorch",
        "outputFile": "wallaroo-upload-pytorch-multi-input-output-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/pytorch-upload-tutorials/wallaroo-upload-pytorch-single-input-output.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/pytorch",
        "outputFile": "wallaroo-upload-pytorch-single-input-output-reference.md"
    },
    ## tensorflow
    {
        "inputFile": "wallaroo-model-deploy-and-serve/tensorflow-upload-tutorials/wallaroo-upload-tensorflow.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/tensorflow",
        "outputFile": "wallaroo-upload-tensorflow-reference.md"
    },

    ## xgboost
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-binary-classification-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-binary-classification-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-multi-classification-softmax-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-multi-classification-softmax-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-multi-classification-softprob-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-multi-classification-softprob-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-regression-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-regression-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-rf-classification-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-rf-classification-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-booster-rf-regression-conversion.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-booster-rf-regression-conversion-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-xbg-classification.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-xbg-classification-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-xbg-regressor.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-xbg-regressor-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-xbg-rf-classification.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-xbg-rf-classification-reference.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/xgboost-upload-tutorials/wallaroo-sdk-upload-xbg-rf-regressor.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/xgboost-upload-tutorials",
        "outputFile": "wallaroo-sdk-upload-xbg-rf-regressor-reference.md"
    },
    ## sklearn
    {
        "inputFile": "wallaroo-model-deploy-and-serve/sklearn-upload-tutorials/wallaroo-upload-sklearn-clustering-kmeans.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/sklearn",
        "outputFile": "wallaroo-upload-sklearn-clustering-kmeans.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/sklearn-upload-tutorials/wallaroo-upload-sklearn-clustering-svm-pca.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/sklearn",
        "outputFile": "wallaroo-upload-sklearn-clustering-svm-pca.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/sklearn-upload-tutorials/wallaroo-upload-sklearn-clustering-svm.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/sklearn",
        "outputFile": "wallaroo-upload-sklearn-clustering-svm.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/sklearn-upload-tutorials/wallaroo-upload-sklearn-linear-regression.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/sklearn",
        "outputFile": "wallaroo-upload-sklearn-linear-regression.md"
    },
    {
        "inputFile": "wallaroo-model-deploy-and-serve/sklearn-upload-tutorials/wallaroo-upload-sklearn-logistic-regression.ipynb",
        "outputDir": "/wallaroo-tutorials/wallaroo-model-deploy-and-serve/sklearn",
        "outputFile": "wallaroo-upload-sklearn-logistic-regression.md"
    },





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
    #     "inputFile": "model_uploads/python-upload-tutorials/python-step-dataframe-output-logging-example-sdk.ipynb",
    #     "outputDir": "/wallaroo-tutorials/model-uploads/python",
    #     "outputFile": "python-step-dataframe-output-logging-example-sdk.md"
    # },





    # # arm architecture section
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-byop-vgg16/wallaroo-arm-arbitrary-python-vgg16-model-deployment.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "wallaroo-arm-arbitrary-python-vgg16-model-deployment-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-classification-cybersecurity/arm-classification-cybersecurity.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "arm-classification-cybersecurity-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-classification-finserv/arm-classification-finserv.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "arm-classification-finserv-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-computer-vision-yolov8/wallaroo-arm-cv-yolov8-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "wallaroo-arm-cv-yolov8-demonstration-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-cv-arrow/arm-computer-vision-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "arm-computer-vision-demonstration-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-arm-llm-summarization/wallaroo-arm-llm-summarization-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "wallaroo-arm-llm-summarization-demonstration-reference.md"
    # },
    # gpu architecture section
    # {
    #     "inputFile": "pipeline-architecture/wallaroo-gpu-llm-summarization/wallaroo-gpu-llm-summarization-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "wallaroo-gpu-llm-summarization-demonstration-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/llamav2/llm-usage-norag.ipynb",
    #     "outputDir": "/wallaroo-tutorials/pipeline-architecture",
    #     "outputFile": "llm-usage-norag-reference.md"
    # },
    # # pipeline edge section
    # {
    #     "inputFile": "pipeline-edge-publish/edge-observability-cv/cv-retail-edge-observability.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "cv-retail-edge-observability-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-unet-brain-segmentation-demonstration/unet_demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "unet_demonstration-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-arbitrary-python/edge-arbitrary-python-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-arbitrary-python-demonstration-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-classification-cybersecurity/edge-classification-cybersecurity-deployment.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-classification-cybersecurity-deployment.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-classification-finserv/edge-classification-finserv-deployment.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-classification-finserv-deployment-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-classification-finserv-api/edge-classification-finserv-deployment-via-api.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-classification-finserv-deployment-via-api-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-cv/edge-cv-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-cv-demonstration.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-cv-healthcare-images/00_computer-vision-mitochondria-imaging-edge-deployment-example.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "00_computer-vision-mitochondria-imaging-edge-deployment-example-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-cv-healthcare-images/01_computer-vision-mitochondria-imaging-edge-deployment-example.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "01_computer-vision-mitochondria-imaging-edge-deployment-example-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-llm-summarization/edge-hf-summarization.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-hf-summarization-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-observability-classification-finserv/edge-observabilty-classification-finserv-deployment.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-observabilty-classification-finserv-deployment-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-observability-classification-finserv-api/edge-observability-classification-finserv-deployment-via-api.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-observability-classification-finserv-deployment-via-api-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-observability-assays/edge-observability-assays.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish",
    #     "outputFile": "edge-observability-assays-reference.md"
    # },
    # {
    #     "inputFile": "pipeline-edge-publish/edge-computer-vision-yolov8/edge-computer-vision-yolov8.ipynb",
    #     "outputDir": "/wallaroo-tutorials/edge-publish/yolov8",
    #     "outputFile": "edge-computer-vision-yolov8-reference.md"
    # },

    # # features section
    # {
    #     "inputFile": "wallaroo-features/assay-model-insights/model-insights.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-model-insights-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/gpu-deployment/wallaroo-llm-with-gpu-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-llm-with-gpu-demonstration.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/model_hot_swap/wallaroo_hot_swap_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-hot-swap-models-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/pipeline_api_log_tutorial/pipeline_api_log_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "pipeline_api_log_tutorial.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/pipeline_log_tutorial/pipeline_log_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "pipeline_log_tutorial.md"
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
    #     "inputFile": "wallaroo-features/wallaroo-tag-management/wallaroo-tags-guide.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features/",
    #     "outputFile": "wallaroo-tags-guide-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/pipeline_api_log_tutorial_cv/pipeline_api_log_tutorial_computer_vision.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features/",
    #     "outputFile": "pipeline_api_log_tutorial_computer_vision-reference.md"
    # },
    # deploy and serve
    ### parallel infer sdk with aloha
    # {
    #     "inputFile": "wallaroo-model-deploy-and-serve/parallel-inferences-sdk-aloha-tutorial/wallaroo-parallel-infer-sdk-with-aloha.ipynb",
    #     "outputDir": "/wallaroo-tutorials/deploy-and-serve",
    #     "outputFile": "wallaroo-parallel-infer-sdk-with-aloha-reference.md"
    # },
    ### multiple replicas forecast updates
    # {
    #     "inputFile": "wallaroo-model-deploy-and-serve/pipeline_multiple_replicas_forecast_tutorial/00_multiple_replicas_forecast.ipynb",
    #     "outputDir": "/wallaroo-tutorials/deploy-and-serve/statsmodel/",
    #     "outputFile": "00_multiple_replicas_forecast.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-deploy-and-serve/pipeline_multiple_replicas_forecast_tutorial/01_multiple_replicas_forecast.ipynb",
    #     "outputDir": "/wallaroo-tutorials/deploy-and-serve/statsmodel/",
    #     "outputFile": "01_multiple_replicas_forecast.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-deploy-and-serve/pipeline_multiple_replicas_forecast_tutorial/02_multiple_replicas_forecast.ipynb",
    #     "outputDir": "/wallaroo-tutorials/deploy-and-serve/statsmodel/",
    #     "outputFile": "02_multiple_replicas_forecast.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-cv-unet/wallaroo-inference-server-cv-unet.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-cv-unet-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-cv-frcnn/wallaroo-inference-server-cv-frcnn.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-cv-frcnn-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-cv-resnet/wallaroo-inference-server-cv-resnet.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-cv-resnet-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-cv-yolov8/wallaroo-inference-server-cv-yolov8.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-cv-yolov8-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-hf-summarizer/wallaroo-inference-server-hf-summarization.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-hf-summarization-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-inference-server-tutorials/wallaroo-inference-server-llama2/wallaroo-inference-server-llama2.ipynb",
    #     "outputDir": "/wallaroo-services/wallaroo-inference-server",
    #     "outputFile": "wallaroo-inference-server-llama2-reference.md"
    # },
    # cookbooks
    # {
    #     "inputFile": "wallaroo-model-cookbooks/aloha/aloha_demo.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-quick-start-aloha-reference.md"
    # },

    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision-mitochondria-imaging/00_computer-vision-mitochondria-imaging-example.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-model-cookbooks/computer-vision-mitochondria",
    #     "outputFile": "00_computer-vision-mitochondria-imaging-example.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision-mitochondria-imaging/01_computer-vision-mitochondria-imaging-example.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-model-cookbooks/computer-vision-mitochondria",
    #     "outputFile": "01_computer-vision-mitochondria-imaging-example.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision-mitochondria-imaging/02_computer-vision-mitochondria-imaging-example.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-model-cookbooks/computer-vision-mitochondria",
    #     "outputFile": "02_computer-vision-mitochondria-imaging-example.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/computer-vision-yolov8/computer-vision-yolov8-demonstration.ipynb",
    #     "outputDir": "/wallaroo-tutorials/computer-vision/yolov8",
    #     "outputFile": "computer-vision-yolov8-demonstration-reference.md"
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
    #     "inputFile": "wallaroo-model-cookbooks/mlflow-tutorial/wallaroo-mlflow-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-mlflow-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/hf-clip-vit-base/clip-vit-hugging-face.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "clip-vit-hugging-face-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-features/onnx-multi-input-demo/test_autoconv_pytorch_multi_io.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "test_autoconv_pytorch_multi_io-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/hf-whisper/wallaroo-whisper_demo.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorial-features",
    #     "outputFile": "wallaroo-whisper_demo-reference.md"
    # },
    # # testing section
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
    #     "inputFile": "wallaroo-testing-tutorials/houseprice-saga/house-price-model-saga-comprehensive.ipynb",
    #     "outputDir": "/wallaroo-tutorials/testing-tutorials",
    #     "outputFile": "house-price-model-saga.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/houseprice-saga/house-price-model-saga-prep.ipynb",
    #     "outputDir": "/wallaroo-tutorials/testing-tutorials",
    #     "outputFile": "house-price-model-saga-prep-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/wallaro-assay-builder-tutorial/wallaroo_assay_builder_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/testing-tutorials",
    #     "outputFile": "wallaroo_assay_builder_tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/wallaro-model_observability_assays/wallaroo_model_observability_assays.ipynb",
    #     "outputDir": "/wallaroo-tutorials/testing-tutorials",
    #     "outputFile": "wallaroo_model_observability_assays.md"
    # },
    # {
    #     "inputFile": "wallaroo-testing-tutorials/shadow_deploy/shadow_deployment_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials",
    #     "outputFile": "wallaroo-shadow-deployment-tutorial-reference.md"
    # },
    # #orchestrations
    # {
    #     "inputFile": "workload-orchestrations/connection_api_bigquery_tutorial/connection_api_bigquery_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "connection_api_bigquery_tutorial.md"
    # },
    # {
    #     "inputFile": "workload-orchestrations/orchestration_api_simple_tutorial/data_orchestrators_api_simple_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "data_orchestrators_api_simple_tutorial.md"
    # },
    # {
    #     "inputFile": "workload-orchestrations/orchestration_sdk_bigquery_houseprice_tutorial/orchestration_sdk_bigquery_houseprice_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "orchestration_sdk_bigquery_houseprice_tutorial.md"
    # },
    # {
    #     "inputFile": "workload-orchestrations/orchestration_sdk_bigquery_statsmodel_tutorial/orchestration_sdk_bigquery_statsmodel_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "orchestration_sdk_bigquery_statsmodel_tutorial.md"
    # },
    # {
    #     "inputFile": "workload-orchestrations/orchestration_sdk_comprehensive_tutorial/data_connectors_and_orchestrators_comprehensive_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "data_connectors_and_orchestrators_comprehensive_tutorial.md"
    # },
    # {
    #     "inputFile": "workload-orchestrations/orchestration_sdk_simple_tutorial/data_connectors_and_orchestrators_simple_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/workload-orchestrations",
    #     "outputFile": "data_connectors_and_orchestrators_simple_tutorial.md"
    # }
    # use case tutorials
    # {
    #     "inputFile": "Workshops/LLM/Summarization/Notebooks-with-code/N1_deploy_a_model-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/llm/summarization",
    #     "outputFile": "N1_deploy_a_model-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/LLM/Summarization/Notebooks-with-code/N2_automate-data-connections-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/llm/summarization",
    #     "outputFile": "N2_automate-data-connections-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/LLM/Summarization/Notebooks-with-code/N3_publsh_pipeline_for_edge-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/llm/summarization",
    #     "outputFile": "N3_publsh_pipeline_for_edge-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/Computer\ Vision/Healthcare/Notebooks-with-code/N0-environment-prep-model-conversion.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/cv/medical",
    #     "outputFile": "N0-environment-prep-model-conversion.md"
    # },
    # {
    #     "inputFile": "Workshops/Computer\ Vision/Healthcare/Notebooks-with-code/N1_deploy_a_model-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/cv/medical",
    #     "outputFile": "N1_deploy_a_model-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/Computer\ Vision/Healthcare/Notebooks-with-code/N2_automate-data-connections-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/cv/medical",
    #     "outputFile": "N2_automate-data-connections-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/Computer\ Vision/Healthcare/Notebooks-with-code/N3_publish_pipeline_for_edge-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/cv/medical",
    #     "outputFile": "N3_publish_pipeline_for_edge-with-code.md"
    # },
    # workshop edge deployment
    # {
    #     "inputFile": "Workshops/Edge-Deployment/Notebooks-with-code/00-edge-computer-vision-yolov8n-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/edge",
    #     "outputFile": "00-edge-computer-vision-yolov8n-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/Edge-Deployment/Notebooks-with-code/02-edge-forecast-retail-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/edge",
    #     "outputFile": "02-edge-forecast-retail-with-code.md"
    # },
    # {
    #     "inputFile": "Workshops/Edge-Deployment/Notebooks-with-code/01-edge-llm-summarization-with-code.ipynb",
    #     "outputDir": "/wallaroo-use-case-tutorials/edge",
    #     "outputFile": "01-edge-llm-summarization-with-code.md"
    # },
    # mlops
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial-User-Management.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides",
    #     "outputFile": "wallaroo-mlops-tutorial-reference-users.md"
    # },
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial-Workspace-Management.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides",
    #     "outputFile": "wallaroo-mlops-tutorial-reference-workspaces.md"
    # },
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial-Model-Management.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides",
    #     "outputFile": "wallaroo-mlops-tutorial-reference-models.md"
    # },
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial-Pipeline-Management.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides",
    #     "outputFile": "wallaroo-mlops-tutorial-reference-pipelines.md"
    # },
    # {
    #     "inputFile": "development/mlops_api/Wallaroo-MLOps-Tutorial-Assay-Management-Plus.ipynb",
    #     "outputDir": "/wallaroo-developer-guides/wallaroo-api-guides",
    #     "outputFile": "Wallaroo-MLOps-Tutorial-Assay-Management-Plus.md"
    # },
    # wallaroo-observe-tutorials
    # {
    #     "inputFile": "wallaroo-observe-tutorials/model-observability-anomaly-detection-ccfraud-sdk-tutorial/model-observability-anomaly-detection-ccfraud-sdk-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-observability",
    #     "outputFile": "model-observability-anomaly-detection-ccfraud-sdk-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-observe-tutorials/model-observability-anomaly-detection-houseprice-sdk-tutorial/model-observability-anomaly-detection-house-price-sdk-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-observability",
    #     "outputFile": "model-observability-anomaly-detection-house-price-sdk-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-observe-tutorials/pipeline-log-tutorial/pipeline_log_tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-observability",
    #     "outputFile": "pipeline_log_tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-observe-tutorials/wallaro-model-observability-assays/wallaroo_model_observability_assays.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-tutorials-observability",
    #     "outputFile": "wallaroo_model_observability_assays-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/edge-observability-assays/00_drift-detection-for-edge-deployments-tutorial-prep.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "00_drift-detection-for-edge-deployments-tutorial-prep-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/edge-observability-assays/01_drift-detection-for-edge-deployments-tutorial-examples.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "01_drift-detection-for-edge-deployments-tutorial-examples-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-model-cookbooks/wallaroo-model-upload-deploy-byop-cv-tutorial/wallaroo-model-upload-deploy-byop-cv-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-upload-serve-models",
    #     "outputFile": "wallaroo-model-upload-deploy-byop-cv-tutorial-reference.md"
    # },
    ## run anywhere
    # {
    #     "inputFile": "wallaroo-run-anywhere/edge-observability-low-no-connection/edge-observability-low-no-connection-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "edge-observability-low-no-connection-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/edge-architecture-publish-linear-regression-houseprice-model/wallaroo-run-anywhere-model-architecture-linear-regression-houseprice-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "wallaroo-run-anywhere-model-architecture-linear-regression-houseprice-tutorial-reference.md"
    # },
    #     {
    #     "inputFile": "wallaroo-run-anywhere/edge-architecture-publish-hf-summarization-model/wallaroo-run-anywhere-model-architecture-publish-hf-summarization.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "wallaroo-run-anywhere-model-architecture-publish-hf-summarization-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/edge-architecture-publish-cv-resnet-model/wallaroo-run-anywhere-model-architecture-publish-cv-resnet-model.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "wallaroo-run-anywhere-model-architecture-publish-cv-resnet-model-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/in-line-edge-model-replacements-tutorial/in-line-edge-model-replacements-tutorial.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "in-line-edge-model-replacements-tutorial-reference.md"
    # },
    # {
    #     "inputFile": "wallaroo-run-anywhere/run-anywhere-acceleration-aloha/run-anywhere-acceleration-aloha.ipynb",
    #     "outputDir": "/wallaroo-tutorials/wallaroo-run-anywhere-tutorials",
    #     "outputFile": "run-anywhere-acceleration-aloha-reference.md"
    # },
    ## tools
    # {
    #     "inputFile": "tools/helper-function-demo/helper-functions-demo.ipynb",
    #     "outputDir": "/wallaroo-tutorials/tools",
    #     "outputFile": "helper-functions-demo-reference.md"
    # },


]

def format(outputdir, document_file):
    # Take the markdown file, remove the extra spaces
    document = open(f'{docs_directory}{outputdir}/{document_file}', "r").read()
    result = re.sub
    
    # fix tables for publication
    # document = re.sub(r'<table.*?>', r'{{<table "table table-striped table-bordered" >}}\n<table>', document)
    # document = re.sub('</table>', r'</table>\n{{</table>}}', document)
    # remove any div table sections
    document = re.sub('<div.*?>', '', document)
    document = re.sub(r'<style.*?>.*?</style>', '', document, flags=re.S)
    document = re.sub('</div>', '', document)

    # remove non-public domains
    document = re.sub('wallaroocommunity.ninja', 'wallarooexample.ai', document)

    # fix image directories
    # ](01_notebooks_in_prod_explore_and_train-reference_files
    # image_replace = f'![png]({outputdir}'
    document = re.sub('!\[png\]\(', f'![png](/images/2024.1{outputdir}/', document)
    document = re.sub('\(./images', '(/images/2024.1', document)
    # move them all to Docsy figures
    document = re.sub(r'!\[(.*?)\]\((.*?)\)', r'{{<figure src="\2" width="800" label="\1">}}', document)

    # move the assay image for UI
    document = re.sub('"images/housepricesaga-sample-assay.png"', '"/images/housepricesaga-sample-assay.png"', document)

    # remove gib
    document = re.sub('gib.bhojraj@wallaroo.ai', 
                      'sample.user@wallaroo.ai', 
                      document)
    # fix github link for final release
    # document = re.sub('https://github.com/WallarooLabs/Wallaroo_Tutorials/blob/wallaroo2024.1_tutorials/', 
    #                   'https://github.com/WallarooLabs/Wallaroo_Tutorials/tree/main/', 
    #                   document)
    
     # obfuscate databricks url
    document = re.sub('https://adb-5939996465837398.18.azuredatabricks.net', 
                      'https://sample.registry.service.azuredatabricks.net', 
                      document)

    # remove edge bundle
    # obfuscate databricks url
    document = re.sub("'EDGE_BUNDLE': '.*?'", 
                      "'EDGE_BUNDLE': 'abcde'", 
                      document)
   # document = re.sub('![png](', 'bob', document)

    # strip the excess newlines - match any pattern of newline plus another one or more empty newlines
    document = re.sub(r'\n[\n]+', r'\n\n', document)

    # remove the whitespace before a table
    document = re.sub(r"^ +<", r"<", document, flags = re.MULTILINE)
    #document.strip() # - test this for whitespace before and after

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