import importlib
import os
import unittest
from unittest.mock import MagicMock, patch

from embedchain.config import BaseLlmConfig
from embedchain.llm.huggingface import HuggingFaceLlm


class TestHuggingFaceLlm(unittest.TestCase):
    def setUp(self):
        os.environ["HUGGINGFACE_ACCESS_TOKEN"] = "test_access_token"
        self.config = BaseLlmConfig(model="google/flan-t5-xxl", max_tokens=50, temperature=0.7, top_p=0.8)

    def test_init_raises_value_error_without_api_key(self):
        os.environ.pop("HUGGINGFACE_ACCESS_TOKEN")
        with self.assertRaises(ValueError):
            HuggingFaceLlm()

    def test_get_llm_model_answer_raises_value_error_for_system_prompt(self):
        llm = HuggingFaceLlm(self.config)
        llm.config.system_prompt = "system_prompt"
        with self.assertRaises(ValueError):
            llm.get_llm_model_answer("prompt")

    def test_top_p_value_within_range(self):
        config = BaseLlmConfig(top_p=1.0)
        with self.assertRaises(ValueError):
            HuggingFaceLlm._get_answer("test_prompt", config)

    def test_dependency_is_imported(self):
        importlib_installed = True
        try:
            importlib.import_module("huggingface_hub")
        except ImportError:
            importlib_installed = False
        self.assertTrue(importlib_installed)

    @patch("embedchain.llm.huggingface.HuggingFaceLlm._get_answer")
    def test_get_llm_model_answer(self, mock_get_answer):
        mock_get_answer.return_value = "Test answer"

        llm = HuggingFaceLlm(self.config)
        answer = llm.get_llm_model_answer("Test query")

        self.assertEqual(answer, "Test answer")
        mock_get_answer.assert_called_once()

    @patch("embedchain.llm.huggingface.HuggingFaceHub")
    def test_hugging_face_mock(self, mock_huggingface):
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Test answer"
        mock_huggingface.return_value = mock_llm_instance

        llm = HuggingFaceLlm(self.config)
        answer = llm.get_llm_model_answer("Test query")

        self.assertEqual(answer, "Test answer")
        mock_huggingface.assert_called_once_with(
            huggingfacehub_api_token="test_access_token",
            repo_id="google/flan-t5-xxl",
            model_kwargs={"temperature": 0.7, "max_new_tokens": 50, "top_p": 0.8},
        )
        mock_llm_instance.assert_called_once_with("Test query")
