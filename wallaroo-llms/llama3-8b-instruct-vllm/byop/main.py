from typing import Any, Set

import subprocess
import sys
import numpy as np

from mac.config.inference import CustomInferenceConfig
from mac.inference import Inference
from mac.inference.creation import InferenceBuilder
from mac.types import InferenceData

pip_command = (
    f'{sys.executable} -m pip install https://github.com/vllm-project/vllm/releases/download/v0.5.2/vllm-0.5.2+cu118-cp310-cp310-manylinux1_x86_64.whl --extra-index-url https://download.pytorch.org/whl/cu118'
)

subprocess.check_call(pip_command, shell=True)

from vllm import LLM, SamplingParams

class VLLMInference(Inference):
    @property
    def expected_model_types(self) -> Set[Any]:
        return {LLM}

    @Inference.model.setter
    def model(self, model) -> None:
        self._raise_error_if_model_is_wrong_type(model)
        self._model = model

    def _predict(self, input_data: InferenceData):
        prompts = input_data["text"].tolist()

        sampling_params = SamplingParams(temperature=0.1, top_p=0.95)
        responses = self.model.generate(prompts, sampling_params)

        return {"generated_text": np.array([response.outputs[0].text for response in responses])}


class VLLMInferenceBuilder(InferenceBuilder):
    @property
    def inference(self) -> VLLMInference:
        return VLLMInference()

    def create(self, config: CustomInferenceConfig) -> VLLMInference:
        inference = self.inference
        model = self._load_model(config.model_path)
        inference.model = model

        return inference

    def _load_model(self, model_path):
        llm = LLM(
            model=f"{model_path}/artifacts/Meta-Llama-3-8B-Instruct/"
        )

        return llm

