from IPython import embed
import argparse
import requests
import sys


def _request(func, url, **kwargs):
    resp = func(url, json=kwargs)
    if resp.status_code != 200:
        raise Exception(f"http {resp.status_code}")
    json = resp.json()
    if json["status"] != "ok":
        raise Exception(json["reason"])
    return json


def _get(url, **kwargs):
    return _request(requests.get, url, **kwargs)


def _post(url, **kwargs):
    return _request(requests.post, url, **kwargs)


def listen(channel: str = "default"):
    return _get("http://localhost:9728/listen", channel=channel)


def send(message: str, channel: str = "default"):
    return _post("http://localhost:9728/send", message=message, channel=channel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="interactive",
        help="choose from [interactive, cat, read]",
    )
    parser.add_argument("-c", "--channel", type=str, default="default")
    args = parser.parse_args()

    match args.mode:
        case "interactive":
            embed(display_banner=False, colors="neutral")

        case "cat":
            while True:
                print(listen(args.channel)["value"])

        case "read":
            for line in sys.stdin:
                send(line[:-1], args.channel)

        case _:
            raise ValueError(f"unknown mode: {args.mode}")
