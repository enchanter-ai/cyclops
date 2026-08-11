from pathlib import Path

import pytest

from cyclops.downstream import load
from cyclops.enums import Server, Transport

EXAMPLE = Path("downstream.example.toml")

def _write(tmp_path, body):
    path = tmp_path / "downstream.toml"
    path.write_text(body, encoding="utf-8")
    return path

def test_example_template_loads():
    specs = load(EXAMPLE)
    assert {s.server for s in specs} == set(Server)

def test_stdio_spec_parsed(tmp_path):
    path = _write(tmp_path, '[[server]]\nname = "filesystem"\ntransport = "stdio"\ncommand = "python"\nargs = ["-m", "x"]\n')
    spec = load(path)[0]
    assert spec.transport is Transport.STDIO
    assert spec.command == "python"
    assert spec.args == ("-m", "x")
    assert spec.url is None

def test_http_spec_parsed(tmp_path):
    path = _write(tmp_path, '[[server]]\nname = "web"\ntransport = "http"\nurl = "https://x/mcp"\n')
    spec = load(path)[0]
    assert spec.transport is Transport.HTTP
    assert spec.url == "https://x/mcp"
    assert spec.command is None

def test_unknown_role_rejected(tmp_path):
    path = _write(tmp_path, '[[server]]\nname = "database"\ntransport = "stdio"\ncommand = "x"\n')
    with pytest.raises(ValueError):
        load(path)

def test_stdio_without_command_rejected(tmp_path):
    path = _write(tmp_path, '[[server]]\nname = "web"\ntransport = "stdio"\n')
    with pytest.raises(ValueError):
        load(path)

def test_http_without_url_rejected(tmp_path):
    path = _write(tmp_path, '[[server]]\nname = "web"\ntransport = "http"\n')
    with pytest.raises(ValueError):
        load(path)

def test_duplicate_role_rejected(tmp_path):
    body = '[[server]]\nname = "web"\ntransport = "http"\nurl = "https://a/mcp"\n[[server]]\nname = "web"\ntransport = "http"\nurl = "https://b/mcp"\n'
    with pytest.raises(ValueError):
        load(_write(tmp_path, body))

def test_empty_map_rejected(tmp_path):
    with pytest.raises(ValueError):
        load(_write(tmp_path, ""))
