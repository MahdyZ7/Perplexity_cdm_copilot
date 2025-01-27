import pytest
import requests
import os, sys
import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

script_dir = Path( __file__ ).parent
mymodule_path = str( script_dir.joinpath( '..', 'hi') )

# Import mymodule
loader = importlib.machinery.SourceFileLoader( 'hi', mymodule_path )
spec = importlib.util.spec_from_loader('hi', loader)
if spec is not None:
	hi = importlib.util.module_from_spec(spec)
	loader.exec_module(hi)
else:
	raise ImportError("Cannot load module 'hi'")

# Configuration Tests
def test_environment_variables():
	with patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'}):
		assert os.getenv('PERPLEXITY_API_KEY') == 'test_key'

# API Key Tests
@pytest.mark.parametrize("api_key,expected_status", [
	("valid_key", 200),
	("invalid_key", 401),
])
def test_api_key_validation(api_key, expected_status):
	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = expected_status
		mock_post.return_value = mock_response
		
		if expected_status == 200:
			hi.testApiKey(api_key)  # Should not raise exception
		else:
			with pytest.raises(SystemExit):
				hi.testApiKey(api_key)

# Model Selection Tests
@pytest.mark.parametrize("input_model,expected_model", [
	("s", "sonar"),
	("pro", "sonar-pro"),
	("invalid", "sonar"),
	("", "sonar"),
])
def test_pick_model(input_model, expected_model):
	assert hi.pick_model(input_model) == expected_model

# Chat Loop Tests
def test_chat_loop_single_use():
	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {
			"choices": [{"message": {"content": "Test response"}}],
			"citations": None
		}
		mock_post.return_value = mock_response
		
		with patch('sys.stdout', new=StringIO()) as fake_output:
			hi.chat_loop("test question", "sonar", "give a breif answer", True)
			assert "Test response" in fake_output.getvalue()

# Input Processing Tests
def test_read_prompt_with_stdin():
	test_input = "test input from stdin"
	with patch('sys.stdin') as mock_stdin:
		mock_stdin.isatty.return_value = False
		mock_stdin.read.return_value = test_input
		with patch('sys.argv', ['script.py', 'prefix']):
			result = hi.read_promt()
			assert test_input in result

# Update Function Tests
def test_update_function():
	with patch('subprocess.run') as mock_run:
		mock_run.return_value = MagicMock(stdout="test_path")
		hi.update()
		mock_run.assert_called()

# Citation Handling Tests
def test_print_citations():
	mock_response = MagicMock()
	mock_response.json.return_value = {
		'citations': ['source1', 'source2']
	}
	with patch('sys.stdout', new=StringIO()) as fake_output:
		hi.printCitations(mock_response, "sonar")
		assert 'source1' in fake_output.getvalue()
		assert 'source2' in fake_output.getvalue()

# Error Handling Tests
def test_chat_loop_api_error():
	with patch('requests.post') as mock_post:
		mock_post.side_effect = requests.exceptions.RequestException("API Error")
		with pytest.raises(SystemExit):
			hi.chat_loop("test", "sonar", "be brief", True)

# Integration Tests
def test_main_function_help():
	with patch('sys.argv', ['script.py', 'help']):
		with patch('sys.stdout', new=StringIO()) as fake_output:
			with pytest.raises(SystemExit):
				hi.main()
			assert "welcome to the perplexity command line ai" in fake_output.getvalue()

@pytest.fixture
def mock_environment():
	with patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'test_key'}):
		yield

def test_full_workflow(mock_environment):
	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {
			"choices": [{"message": {"content": "Test response"}}],
			"citations": None
		}
		mock_post.return_value = mock_response
		
		with patch('sys.argv', ['script.py', 'test question']):
			with patch('sys.stdout', new=StringIO()) as fake_output:
				with patch('sys.stdin') as mock_stdin:
					hi.main()
					assert "Test response" in fake_output.getvalue()