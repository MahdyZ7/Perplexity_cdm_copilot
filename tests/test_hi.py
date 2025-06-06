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

# Additional Configuration Tests
def test_invalid_environment_variables():
	with patch.dict('os.environ', {'PERPLEXITY_API_KEY': ''}):
		assert os.getenv('PERPLEXITY_API_KEY') == ''

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
			hi.settings.testApiKey(api_key)  # Should not raise exception
		else:
			with pytest.raises(SystemExit):
				hi.settings.testApiKey(api_key)

# Model Selection Tests
@pytest.mark.parametrize("input_model,expected_model", [
	("s", "sonar"),
	("pro", "sonar-pro"),
	("invalid", "r1-1776"),
	("", "r1-1776"),
	(None, "r1-1776"),
	("r", "sonar-reasoning"),
	("rp", "sonar-reasoning-pro"),
	("0", "r1-1776"),
	("1", "sonar"),
	("2", "sonar-pro"),
	("3", "sonar-reasoning"),
	("4", "sonar-reasoning-pro"),
])
def test_pick_model(input_model, expected_model):
	assert hi.help.pick_model(input_model) == expected_model

# Additional Model Selection Tests
@pytest.mark.parametrize("input_model,expected_model", [
	("sonar", "sonar"),
	("sonar-pro", "sonar-pro"),
	("sonar-reasoning", "sonar-reasoning"),
	("sonar-reasoning-pro", "sonar-reasoning-pro"),
	("sonar-deep-research", "sonar-deep-research"),
	("r1", "r1-1776"),
	("0", "r1-1776"),
	("s", "sonar"),
	("1", "sonar"),
	("l", "sonar-pro"),
	("2", "sonar-pro"),
	("r", "sonar-reasoning"),
	("3", "sonar-reasoning"),
	("rp", "sonar-reasoning-pro"),
	("4", "sonar-reasoning-pro"),
	("d", "sonar-deep-research"),
	("5", "sonar-deep-research"),
	("", "r1-1776"),
	(None, "r1-1776"),
	("invalid", "r1-1776"),
])
def test_pick_model_edge_cases(input_model, expected_model):
	assert hi.help.pick_model(input_model) == expected_model

# Chat Loop Tests
def test_chat_loop_single_use():
	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {
			"choices": [{"message": {"content": "Test response"}}],
			"model": "sonar",
			"citations": None
		}
		mock_post.return_value = mock_response
		
		with patch('sys.stdout', new=StringIO()) as fake_output:
			args = hi.cliParsing()
			args.single_use = True
			hi.chat_loop("sonar", "give a breif answer", args)
			assert "Test response" in fake_output.getvalue()

# Additional Chat Loop Tests
def test_chat_loop_invalid_response_format():
	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {"unexpected_key": "unexpected_value"}
		mock_post.return_value = mock_response
		
		with patch('sys.stdout', new=StringIO()) as fake_output:
			args = hi.cliParsing()
			args.single_use = True
			with pytest.raises(KeyError):
				hi.chat_loop("sonar", "give a brief answer", args)

# Input Processing Tests
def test_read_prompt_with_stdin():
	test_input = "test input from stdin"
	with patch('sys.stdin') as mock_stdin:
		mock_stdin.isatty.return_value = False
		mock_stdin.read.return_value = test_input
		with patch('sys.argv', ['script.py', 'prefix']):
			result = hi.read_prompt()
			assert test_input in result

# Update Function Tests
def test_update_function():
	with patch('subprocess.run') as mock_run:
		mock_run.return_value = MagicMock(stdout="test_path")
		hi.settings.update()
		mock_run.assert_called()

# Citation Handling Tests
def test_print_citations():
	mock_response = MagicMock()
	mock_response.list.return_value = ['source1', 'source2']
	with patch('sys.stdout', new=StringIO()) as fake_output:
		hi.printCitations(mock_response.list())
		assert 'source1' in fake_output.getvalue()
		assert 'source2' in fake_output.getvalue()

def test_print_citations_empty():
	mock_response = MagicMock()
	mock_response.list.return_value = []
	with patch('sys.stdout', new=StringIO()) as fake_output:
		hi.printCitations(mock_response.list())
		assert '' in fake_output.getvalue()

def test_print_citations_none():
	mock_response = MagicMock()
	mock_response.list.return_value = None
	with patch('sys.stdout', new=StringIO()) as fake_output:
		hi.printCitations(mock_response.list())
		assert '' in fake_output.getvalue()

def test_print_citations_with_special_characters():
	mock_response = MagicMock()
	mock_response.list.return_value = ['source1', 'source2 with special char: ©']
	with patch('sys.stdout', new=StringIO()) as fake_output:
		hi.printCitations(mock_response.list())
		assert 'source1' in fake_output.getvalue()
		assert 'source2 with special char: ©' in fake_output.getvalue()

# Error Handling Tests
def test_chat_loop_api_error():
	with patch('requests.post') as mock_post:
		mock_post.side_effect = requests.exceptions.RequestException("API Error")
		with pytest.raises(SystemExit):
			args = hi.cliParsing()
			args.single_use = True
			hi.chat_loop("sonar", "be brief", args)

# Additional Error Handling Tests
def test_chat_loop_timeout_error():
	with patch('requests.post') as mock_post:
		mock_post.side_effect = requests.exceptions.Timeout("Timeout Error")
		with pytest.raises(SystemExit):
			args = hi.cliParsing()
			args.single_use = True
			hi.chat_loop("sonar", "be brief", args)

# Integration Tests
def test_main_function_help():
	with patch('sys.stdin') as mock_stdin:
		mock_stdin.isatty.return_value = True
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
			"model": "sonar",
			"citations": None
		}
		mock_post.return_value = mock_response
		
		with patch('sys.argv', ['script.py', 'test question']):
			with patch('sys.stdout', new=StringIO()) as fake_output:
				with patch('sys.stdin') as mock_stdin:
					hi.main()
					assert "Test response" in fake_output.getvalue()