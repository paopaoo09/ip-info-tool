"""Automated tests for ip_tool.py."""

import json
import pytest
from unittest.mock import patch, Mock

import ip_tool


# ---------- get_ip() ----------

@patch("ip_tool.requests.get")
def test_get_ip_success(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"ip": "8.8.8.8"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    assert ip_tool.get_ip("http://fake", "IPv4") == "8.8.8.8"


@patch("ip_tool.requests.get")
def test_get_ip_timeout_returns_none(mock_get):
    import requests
    mock_get.side_effect = requests.exceptions.Timeout()
    assert ip_tool.get_ip("http://fake", "IPv4") is None


@patch("ip_tool.requests.get")
def test_get_ip_connection_error_returns_none(mock_get):
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    assert ip_tool.get_ip("http://fake", "IPv6") is None


@patch("ip_tool.requests.get")
def test_get_ip_invalid_json_returns_none(mock_get):
    mock_resp = Mock()
    mock_resp.json.side_effect = ValueError("bad json")
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    assert ip_tool.get_ip("http://fake", "IPv4") is None


@patch("ip_tool.requests.get")
def test_get_ip_missing_key_returns_none(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"no_ip_here": True}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    assert ip_tool.get_ip("http://fake", "IPv4") is None


# ---------- get_ip_information() ----------

@patch("ip_tool.requests.get")
def test_get_ip_information_success(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {
        "success": True,
        "ip": "8.8.8.8",
        "type": "IPv4",
        "city": "Mountain View",
        "region": "California",
        "country": "United States",
        "country_code": "US",
        "connection": {"org": "Google", "asn": 15169},
        "timezone": {"id": "America/Los_Angeles"},
        "postal": "94043",
    }
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    info = ip_tool.get_ip_information("8.8.8.8")
    assert info["ip"] == "8.8.8.8"
    assert info["country"] == "United States"
    assert info["org"] == "Google"


@patch("ip_tool.requests.get")
def test_get_ip_information_unsuccessful(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"success": False, "message": "invalid ip"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    assert ip_tool.get_ip_information("bad") is None


@patch("ip_tool.requests.get")
def test_get_ip_information_request_error(mock_get):
    import requests
    mock_get.side_effect = requests.exceptions.RequestException("boom")
    assert ip_tool.get_ip_information("8.8.8.8") is None


# ---------- CLI parsing ----------

def test_parser_defaults():
    args = ip_tool.build_parser().parse_args([])
    assert args.ipv4 is False
    assert args.ipv6 is False
    assert args.json is None


def test_parser_ipv4_flag():
    args = ip_tool.build_parser().parse_args(["--ipv4"])
    assert args.ipv4 is True


def test_parser_ipv6_flag():
    args = ip_tool.build_parser().parse_args(["--ipv6"])
    assert args.ipv6 is True


def test_parser_json_flag():
    args = ip_tool.build_parser().parse_args(["--json", "out.json"])
    assert args.json == "out.json"


# ---------- main() behaviour ----------

@patch("ip_tool.requests.get")
def test_main_only_queries_ipv4(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"ip": "1.2.3.4"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    with patch("ip_tool.get_ip_information", return_value={"ip": "1.2.3.4"}):
        results = ip_tool.main(["--ipv4"])

    assert "IPv4" in results
    assert "IPv6" not in results


# ---------- JSON export ----------

def test_save_json_writes_file(tmp_path):
    path = tmp_path / "out.json"
    data = {"IPv4": {"ip": "1.2.3.4"}}
    ip_tool.save_json(data, str(path))
    assert json.loads(path.read_text(encoding="utf-8")) == data