import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import ollama
from benchmark import run_benchmark, OllamaResponse, Message

class TestBenchmark(unittest.TestCase):
    def setUp(self):
        self.model_name = "test-model"
        self.prompt = "Test prompt"
        self.verbose = False

    @patch('ollama.chat')
    def test_run_benchmark_success(self, mock_chat):
        # Mock successful response from Ollama API
        mock_response = {
            "model": self.model_name,
            "created_at": datetime.now().isoformat(),
            "message": {
                "role": "assistant",
                "content": "Test response"
            },
            "done": True,
            "total_duration": 1000000000,
            "load_duration": 500000000,
            "prompt_eval_count": 10,
            "prompt_eval_duration": 200000000,
            "eval_count": 20,
            "eval_duration": 300000000
        }
        mock_chat.return_value = mock_response

        # Call the function under test
        result = run_benchmark(self.model_name, self.prompt, self.verbose)

        # Assertions
        self.assertIsInstance(result, OllamaResponse)
        self.assertEqual(result.model, self.model_name)
        self.assertEqual(result.message.content, "Test response")
        mock_chat.assert_called_once_with(
            model=self.model_name,
            messages=[{"role": "user", "content": self.prompt}],
            stream=False
        )

    @patch('ollama.chat')
    def test_run_benchmark_error(self, mock_chat):
        # Mock an exception from Ollama API
        mock_chat.side_effect = Exception("API connection failed")

        # Call the function under test
        result = run_benchmark(self.model_name, self.prompt, self.verbose)

        # Assertions
        self.assertIsNone(result)
        mock_chat.assert_called_once_with(
            model=self.model_name,
            messages=[{"role": "user", "content": self.prompt}],
            stream=False
        )

    @patch('ollama.chat')
    def test_run_benchmark_verbose_streaming(self, mock_chat):
        # Mock successful streaming response from Ollama API
        mock_stream = [
            {"message": {"content": "Test "}, "done": False},
            {"message": {"content": "response"}, "done": True,
             "model": self.model_name,
             "created_at": datetime.now().isoformat(),
             "total_duration": 1000000000,
             "load_duration": 500000000,
             "prompt_eval_count": 10,
             "prompt_eval_duration": 200000000,
             "eval_count": 20,
             "eval_duration": 300000000}
        ]
        mock_chat.return_value = mock_stream

        # Call the function under test with verbose=True
        result = run_benchmark(self.model_name, self.prompt, verbose=True)

        # Assertions
        self.assertIsInstance(result, OllamaResponse)
        self.assertEqual(result.model, self.model_name)
        mock_chat.assert_called_once_with(
            model=self.model_name,
            messages=[{"role": "user", "content": self.prompt}],
            stream=True
        )

if __name__ == '__main__':
    unittest.main()
