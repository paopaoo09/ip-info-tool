# IP Info Tool

A Python CLI that retrieves your public IPv4/IPv6 address and detailed
information about it (city, country, ISP, timezone, etc.).

## Features

- Query IPv4 and/or IPv6 public IP
- Fetch detailed info via [ipwho.is](https://ipwho.is/)
- **NEW:** CLI flags `--ipv4`, `--ipv6`, `--json FILE`
- **NEW:** Export results to JSON
- Automated tests with pytest
- CI pipeline with GitHub Actions
- Testing for the CI pipeline

## Install

```bash
pip install -r requirements.txt
```
