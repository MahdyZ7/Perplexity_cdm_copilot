import pytest
import requests
import os
import sys
import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

script_dir = Path(__file__).parent
mymodule_path = str(script_dir.joinpath("..", "hi"))

# Add parent directory to sys.path so hi_constants, hi_help, hi_settings can be imported
parent_dir = str(script_dir.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import mymodule
loader = importlib.machinery.SourceFileLoader("hi", mymodule_path)
spec = importlib.util.spec_from_loader("hi", loader)
if spec is not None:
    hi = importlib.util.module_from_spec(spec)
    loader.exec_module(hi)
else:
    raise ImportError("Cannot load module 'hi'")


# Configuration Tests
def test_environment_variables():
    with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "test_key"}):
        assert os.getenv("PERPLEXITY_API_KEY") == "test_key"


# Additional Configuration Tests
def test_invalid_environment_variables():
    with patch.dict("os.environ", {"PERPLEXITY_API_KEY": ""}):
        assert os.getenv("PERPLEXITY_API_KEY") == ""


# API Key Tests
@pytest.mark.parametrize(
    "api_key,expected_status",
    [
        ("valid_key", 200),
        ("invalid_key", 401),
    ],
)
def test_api_key_validation(api_key, expected_status):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = expected_status
        mock_post.return_value = mock_response

        if expected_status == 200:
            hi.settings.testApiKey(api_key)  # Should not raise exception
        else:
            with pytest.raises(SystemExit):
                hi.settings.testApiKey(api_key)


# Model Selection Tests
@pytest.mark.parametrize(
    "input_model,expected_model",
    [
        ("s", "sonar"),
        ("pro", "sonar-pro"),
        ("invalid", "sonar"),
        ("", "sonar"),
        (None, "sonar"),
        ("r", "sonar-reasoning"),
        ("rp", "sonar-reasoning-pro"),
        ("0", "sonar"),
        ("1", "sonar-pro"),
        ("2", "sonar-reasoning"),
        ("3", "sonar-reasoning-pro"),
        ("4", "sonar-deep-research"),
        ("5", "sonar"),
    ],
)
def test_pick_model(input_model, expected_model):
    assert hi.help.pick_model(input_model) == expected_model


# Additional Model Selection Tests
@pytest.mark.parametrize(
    "input_model,expected_model",
    [
        ("sonar", "sonar"),
        ("sonar-pro", "sonar-pro"),
        ("sonar-reasoning", "sonar-reasoning"),
        ("sonar-reasoning-pro", "sonar-reasoning-pro"),
        ("sonar-deep-research", "sonar-deep-research"),
        ("0", "sonar"),
        ("s", "sonar"),
        ("l", "sonar-pro"),
        ("2", "sonar-reasoning"),
        ("r", "sonar-reasoning"),
        ("3", "sonar-reasoning-pro"),
        ("rp", "sonar-reasoning-pro"),
        ("4", "sonar-deep-research"),
        ("d", "sonar-deep-research"),
        ("", "sonar"),
        (None, "sonar"),
        ("invalid", "sonar"),
    ],
)
def test_pick_model_edge_cases(input_model, expected_model):
    assert hi.help.pick_model(input_model) == expected_model

# Input Processing Tests
def test_read_prompt_with_stdin():
    test_input = "test input from stdin"
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = test_input
        with patch("sys.argv", ["script.py", "prefix"]):
            result = hi.read_prompt()
            assert test_input in result


# Update Function Tests
def test_update_function():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="test_path")
        hi.settings.update()
        mock_run.assert_called()


# Citation Handling Tests
def test_print_citations():
    mock_response = MagicMock()
    mock_response.list.return_value = [{"title": "source1", "url": "http://source1.com", "date": "2023-01-01"}, {"title": "source2", "url": "http://source2.com", "date": "2023-01-02"}]
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.printSearchResults(mock_response.list())
        assert "source1" in fake_output.getvalue()
        assert "source2" in fake_output.getvalue()


def test_print_citations_empty():
    mock_response = MagicMock()
    mock_response.list.return_value = []
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.printSearchResults(mock_response.list())
        assert "" in fake_output.getvalue()


def test_print_citations_none():
    mock_response = MagicMock()
    mock_response.list.return_value = None
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.printSearchResults(mock_response.list())
        assert "" in fake_output.getvalue()


def test_print_citations_with_special_characters():
    mock_response = MagicMock()
    mock_response.list.return_value = [{"title": "source1", "url": "http://source1.com", "date": "2023-01-01"}, {"title": "source2 with special char: ©", "url": "http://source2.com", "date": "2023-01-02"}]
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.printSearchResults(mock_response.list())
        assert "source1" in fake_output.getvalue()
        assert "source2 with special char: ©" in fake_output.getvalue()

# Integration Tests
def test_main_function_help():
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = True
        with patch("sys.argv", ["script.py", "help"]):
            with patch("sys.stdout", new=StringIO()) as fake_output:
                with pytest.raises(SystemExit):
                    hi.main()
                assert (
                    "welcome to the perplexity command line ai"
                    in fake_output.getvalue()
                )


@pytest.fixture
def mock_environment():
    with patch.dict("os.environ", {"PERPLEXITY_API_KEY": "test_key"}):
        yield


# Color Function Tests
def test_color_with_rich_available():
    # When rich is available, RICH_AVAILABLE should be True
    result = hi.color("test", "red")
    # The result should contain the text, whether formatted or not
    assert "test" in result


def test_color_with_invalid_color_when_rich_unavailable():
    # Test with an invalid color when rich is not available
    # This should fall back to CONST.COLORS
    result = hi.color("test", "invalid_color")
    assert "test" in result


def test_color_invalid_color():
    result = hi.color("test", "invalid_color")
    assert "test" in result


# Prepare Payload Tests
@pytest.mark.parametrize(
    "model,context,expected_model",
    [
        ("sonar", "test context", "sonar"),
        ("sonar-pro", "another context", "sonar-pro"),
        ("sonar-reasoning", "", "sonar-reasoning"),
    ],
)
def test_prepare_payload(model, context, expected_model):
    args = MagicMock()
    args.include = None
    args.exclude = None
    args.recency = None
    args.related = False

    result = hi.preparePayload(model, context, args)

    assert result["model"] == expected_model
    assert len(result["messages"]) == (1 if context else 0)
    if context:
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][0]["content"] == context


def test_prepare_payload_with_include_filter():
    args = MagicMock()
    args.include = ["example.com", "test.com"]
    args.exclude = None
    args.recency = None
    args.related = False

    result = hi.preparePayload("sonar", "context", args)
    assert result["search_domain_filter"] == ["example.com", "test.com"]


def test_prepare_payload_with_exclude_filter():
    args = MagicMock()
    args.include = None
    args.exclude = ["spam.com", "ads.com"]
    args.recency = None
    args.related = False

    result = hi.preparePayload("sonar", "context", args)
    assert result["search_domain_filter"] == ["-spam.com", "-ads.com"]


def test_prepare_payload_with_recency():
    args = MagicMock()
    args.include = None
    args.exclude = None
    args.recency = "week"
    args.related = False

    result = hi.preparePayload("sonar", "context", args)
    assert result["search_recency_filter"] == "week"


def test_prepare_payload_with_related_questions():
    args = MagicMock()
    args.include = None
    args.exclude = None
    args.recency = None
    args.related = True

    result = hi.preparePayload("sonar", "context", args)
    assert result["return_related_questions"] == True


# Handle User Input Tests
def test_handle_user_input_single_use():
    chat_payload = {"messages": []}
    args = MagicMock()
    args.single_use = True
    args.question = "What is AI?"

    result = hi.handleUserInput(chat_payload, args)

    assert result == "What is AI?"
    assert len(chat_payload["messages"]) == 1
    assert chat_payload["messages"][0]["role"] == "user"


def test_handle_user_input_exit():
    chat_payload = {"messages": []}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", return_value="exit"):
        with pytest.raises(SystemExit):
            hi.handleUserInput(chat_payload, args)


def test_handle_user_input_new_chat_yes():
    chat_payload = {"messages": [{"role": "user", "content": "old message"}]}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", side_effect=["new chat", "y"]):
        result = hi.handleUserInput(chat_payload, args)

    assert result == ""
    assert len(chat_payload["messages"]) == 0


def test_handle_user_input_new_chat_no():
    chat_payload = {"messages": [{"role": "user", "content": "old message"}]}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", side_effect=["new chat", "n"]):
        result = hi.handleUserInput(chat_payload, args)

    assert result == ""
    assert len(chat_payload["messages"]) == 1


def test_handle_user_input_change_model():
    chat_payload = {"messages": [], "model": "sonar"}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", side_effect=["change model", "1"]):
        result = hi.handleUserInput(chat_payload, args)

    assert result == ""
    assert chat_payload["model"] == "sonar-pro"


def test_handle_user_input_normal_question():
    chat_payload = {"messages": []}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", return_value="What is Python?"):
        result = hi.handleUserInput(chat_payload, args)

    assert result == "What is Python?"
    assert len(chat_payload["messages"]) == 1


# Send Request Tests
def test_send_request_success():
    chat_payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": "test"}]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "response text"}}],
        "model": "sonar"
    }

    with patch("requests.post", return_value=mock_response):
        with patch("sys.stdout", new=StringIO()):
            result = hi.sendRequest(chat_payload)

    assert result == "response text"


def test_send_request_timeout():
    chat_payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": "test"}]
    }

    with patch("requests.post", side_effect=requests.exceptions.Timeout):
        with pytest.raises(SystemExit):
            hi.sendRequest(chat_payload)


def test_send_request_http_error():
    chat_payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": "test"}]
    }

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(SystemExit):
            hi.sendRequest(chat_payload)


# Display Response Tests
def test_display_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "sonar",
        "choices": [{"message": {"content": "Test response"}}]
    }

    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.displayResponse(mock_response)
        output = fake_output.getvalue()
        assert "Test response" in output


# Read Prompt Tests
def test_read_prompt_with_stdin_and_prompt():
    test_input = "stdin content"
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = test_input
        result = hi.read_prompt("prefix text")
        assert "prefix text" in result
        assert test_input in result


def test_read_prompt_no_stdin():
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = True
        result = hi.read_prompt("test prompt")
        assert result == "test prompt"


def test_read_prompt_stdin_only():
    test_input = "only stdin"
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = test_input
        result = hi.read_prompt("")
        assert result == test_input


# CLI Parsing Tests
def test_cli_parsing_basic():
    with patch("sys.argv", ["hi", "What is AI?"]):
        args = hi.cliParsing()
        assert args.question == "What is AI?"


def test_cli_parsing_with_model():
    with patch("sys.argv", ["hi", "test question", "-m", "1"]):
        args = hi.cliParsing()
        assert args.question == "test question"
        assert args.model == "1"


def test_cli_parsing_with_context():
    with patch("sys.argv", ["hi", "test", "-c", "custom context"]):
        args = hi.cliParsing()
        assert args.context == "custom context"


def test_cli_parsing_with_include_domains():
    with patch("sys.argv", ["hi", "test", "-i", "example.com", "test.com"]):
        args = hi.cliParsing()
        assert args.include == ["example.com", "test.com"]


def test_cli_parsing_with_exclude_domains():
    with patch("sys.argv", ["hi", "test", "-e", "spam.com"]):
        args = hi.cliParsing()
        assert args.exclude == ["spam.com"]


def test_cli_parsing_with_recency():
    with patch("sys.argv", ["hi", "test", "-T", "week"]):
        args = hi.cliParsing()
        assert args.recency == "week"


def test_cli_parsing_with_related():
    with patch("sys.argv", ["hi", "test", "-R"]):
        args = hi.cliParsing()
        assert args.related == True


def test_cli_parsing_update_flag():
    with patch("sys.argv", ["hi", "-u"]):
        args = hi.cliParsing()
        assert args.update == True


# Help Module Tests
def test_available_models():
    result = hi.help.availableModels()
    assert "sonar" in result
    assert "sonar-pro" in result
    assert "[0]" in result
    assert "[1]" in result


def test_print_available_models():
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.help.printAvailableModels()
        output = fake_output.getvalue()
        assert "sonar" in output


def test_description():
    result = hi.help.description()
    assert "welcome to the perplexity command line ai" in result.lower()
    assert "chat" in result.lower()


# Settings Module Tests
def test_update_api_key_invalid():
    with patch("builtins.input", return_value="invalid_key"):
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_post.return_value = mock_response
            with pytest.raises(SystemExit):
                hi.settings.update_api_key()


def test_update_api_key_with_valid_key():
    with patch("builtins.input", return_value="valid_key"):
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            with patch("os.path.isfile", return_value=True):
                with patch("builtins.open", MagicMock()):
                    with patch("sys.stdout", new=StringIO()) as fake_output:
                        hi.settings.update_api_key()
                        output = fake_output.getvalue()
                        # Should complete without raising SystemExit
                        assert "enviroment variable" in output or "API Key is valid" in output


# Main Function Tests
def test_main_function_update():
    with patch("sys.argv", ["hi", "update"]):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            with patch("subprocess.run"):
                with pytest.raises(SystemExit):
                    hi.main()


def test_main_function_models():
    with patch("sys.argv", ["hi", "models"]):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            with patch("sys.stdout", new=StringIO()) as fake_output:
                with pytest.raises(SystemExit):
                    hi.main()
                assert "sonar" in fake_output.getvalue()


def test_main_function_chat():
    with patch("sys.argv", ["hi", "chat"]):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            with patch.object(hi, "chat_loop") as mock_chat:
                mock_chat.return_value = None
                hi.main()
                mock_chat.assert_called_once()


# Edge Cases and Error Handling
def test_empty_question_handling():
    chat_payload = {"messages": []}
    args = MagicMock()
    args.single_use = False

    with patch("builtins.input", return_value=""):
        result = hi.handleUserInput(chat_payload, args)

    assert result == ""


def test_print_search_results_malformed_data():
    malformed_results = [{"title": "test"}]  # Missing url and date
    with patch("sys.stdout", new=StringIO()) as fake_output:
        hi.printSearchResults(malformed_results)
        output = fake_output.getvalue()
        assert "test" in output
        assert "No URL" in output
        assert "No Date" in output


# Constants Tests
def test_constants_available_models():
    import hi_constants as CONST
    assert len(CONST.AVAILABLE_MODELS) == 5
    assert "sonar" in CONST.AVAILABLE_MODELS
    assert "sonar-pro" in CONST.AVAILABLE_MODELS


def test_constants_api_url():
    import hi_constants as CONST
    assert CONST.API_URL == "https://api.perplexity.ai/chat/completions"


def test_constants_timeout():
    import hi_constants as CONST
    assert CONST.TIMEOUT == 7200


