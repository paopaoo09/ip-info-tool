"""IP Address Information Tool.

Features:
  - Query IPv4 and/or IPv6 public IP
  - Fetch detailed info for each IP via ipwho.is
  - NEW: CLI flags --ipv4 / --ipv6 / --json FILE
  - NEW: Export results to JSON
"""

import argparse
import json
import requests

IPV4_URL = "https://api.ipify.org?format=json"
IPV6_URL = "https://api6.ipify.org?format=json"
INFO_URL = "https://ipwho.is/"


def get_ip(url, version):
    """Return the public IP as a string, or None on any failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["ip"]
    except requests.exceptions.Timeout:
        print(f"{version}: Request timed out.")
    except requests.exceptions.ConnectionError:
        print(f"{version}: Could not connect. This IP version may be unavailable.")
    except requests.exceptions.RequestException as error:
        print(f"{version}: Request failed: {error}")
    except (ValueError, KeyError):
        print(f"{version}: Invalid API response.")
    return None


def get_ip_information(ip):
    """Return a dict of IP details, or None on failure."""
    try:
        response = requests.get(f"{INFO_URL}{ip}", timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print("Could not retrieve detailed IP information.")
            print(data.get("message", "Unknown API error."))
            return None

        connection = data.get("connection", {})
        return {
            "ip": data.get("ip"),
            "type": data.get("type"),
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "country_code": data.get("country_code"),
            "org": connection.get("org"),
            "asn": connection.get("asn"),
            "timezone": data.get("timezone", {}).get("id"),
            "postal": data.get("postal"),
        }
    except requests.exceptions.RequestException as error:
        print(f"Could not retrieve detailed information: {error}")
    except (ValueError, AttributeError):
        print("The API returned an invalid response.")
    return None


def print_info(info):
    """Pretty-print the info dict."""
    for key, value in info.items():
        print(f"{key.title()}: {value if value else 'N/A'}")


def save_json(results, path):
    """Write the results dict to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {path}")


def build_parser():
    """Build the argparse parser (exposed for tests)."""
    parser = argparse.ArgumentParser(description="IP Address Information Tool")
    parser.add_argument("--ipv4", action="store_true", help="Query IPv4 only")
    parser.add_argument("--ipv6", action="store_true", help="Query IPv6 only")
    parser.add_argument("--json", metavar="FILE", help="Save results to JSON file")
    return parser


def main(argv=None):
    """Run the tool. Returns the results dict (useful for tests)."""
    args = build_parser().parse_args(argv)

    if args.ipv4 and not args.ipv6:
        targets = [("IPv4", IPV4_URL)]
    elif args.ipv6 and not args.ipv4:
        targets = [("IPv6", IPV6_URL)]
    else:
        targets = [("IPv4", IPV4_URL), ("IPv6", IPV6_URL)]

    print("=" * 45)
    print("         IP ADDRESS INFORMATION TOOL")
    print("=" * 45)

    results = {}
    for version, url in targets:
        print(f"\nRetrieving {version} information...")
        ip = get_ip(url, version)
        if ip:
            print(f"{version} Address: {ip}")
            print("\nDetailed IP information:")
            info = get_ip_information(ip)
            if info:
                print_info(info)
                results[version] = info

    if args.json:
        save_json(results, args.json)

    print("\n" + "=" * 45)
    print("               LOOKUP COMPLETED")
    print("=" * 45)
    return results


if __name__ == "__main__":
    main()