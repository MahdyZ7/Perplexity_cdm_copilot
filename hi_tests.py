import pytest
import requests
import os
from hi import testApiKey, pick_model, chat_loop, update_api_key

def test_api_key_valid(monkeypatch):
    # Mock API request to return a 200 status code
    def mock_post(*args, **kwargs):
        return type('Response', (), {'status_code': 200})
    monkeypatch.setattr('requests.post', mock_post)
    
    testApiKey("valid_api_key")
    assert True  # If no exception is raised, the test passes

def test_api_key_invalid(monkeypatch):
    # Mock API request to return a non-200 status code
    def mock_post(*args, **kwargs):
        return type('Response', (), {'status_code': 401})
    monkeypatch.setattr('requests.post', mock_post)
    
    with pytest.raises(SystemExit):
        testApiKey("invalid_api_key")

def test_model_selection():
    assert pick_model("0") == "sonar"
    assert pick_model("1") == "sonar-pro"
    assert pick_model("invalid") == "sonar"

def test_chat_loop_single_use():
    # Mock API request to return a response
    def mock_post(*args, **kwargs):
        return type('Response', (), {'status_code': 200, 'json': lambda: {'choices': [{'message': {'content': 'Mockresponse'}}]}})
    requests.post = mock_post
    
    chat_loop("Hello", "sonar")
    assert True  # If no exception is raised, the test passes

def test_chat_loop_multi_use():
    # Mock API request to return a response
    def mock_post(*args, **kwargs):
        return type('Response', (), {'status_code': 200, 'json': lambda: {'choices': [{'message': {'content': 'Mockresponse'}}]}})
    requests.post = mock_post
    
    chat_loop("chat", "sonar", single_use=False)
    assert True  # If no exception is raised, the test passes

def test_system_prompt_handling():
    # Mock API request to return a response
    def mock_post(*args, **kwargs):
        return type('Response', (), {'status_code': 200, 'json': lambda: {'choices': [{'message': {'content': 'Mockresponse'}}]}})
    requests.post = mock_post
    
    chat_loop("Hello", "sonar", "Custom prompt")
    assert True  # If no exception is raised, the test passes

def test_error_handling(monkeypatch):
    # Mock API request to raise an exception
    def mock_post(*args, **kwargs):
        raise requests.exceptions.RequestException
    monkeypatch.setattr('requests.post', mock_post)
    
    with pytest.raises(SystemExit):
        chat_loop("Hello", "sonar")

def test_env_variable_setup(monkeypatch):
    # Mock input to return a new API key
    def mock_input(*args, **kwargs):
        return "new_api_key"
    monkeypatch.setattr('builtins.input', mock_input)
    
    update_api_key()
    assert os.getenv('PERPLEXITY_API_KEY') == "new_api_key"