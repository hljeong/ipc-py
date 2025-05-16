from flask import Flask, jsonify, request
from pydantic import validate_call
import threading

app = Flask(__name__)


class Channel:
    def __init__(self, name: str):
        self.name: str = name
        self.seq: int = 0
        self.message: str = ""
        self.cond: threading.Condition = threading.Condition()

    def listen(self) -> str:
        cur_seq: int = self.seq
        with self.cond:
            self.cond.wait_for(lambda: self.seq > cur_seq)
            return self.message

    def send(self, message: str):
        with self.cond:
            self.message = message
            self.seq += 1
            self.cond.notify_all()


channels: dict[str, Channel] = {}


def get_channel(name: str):
    if name not in channels:
        channels[name] = Channel(name)
    return channels[name]


def ok(value):
    return jsonify(status="ok", value=value)


def error(error):
    if str(error) == "":
        return jsonify(status="bad", reason=type(error).__name__)

    else:
        return jsonify(status="bad", reason=str(error))


def rpc(route, methods):
    def decorator(func):
        def wrapped():
            try:
                args = request.get_json()
                return ok(validate_call(func)(**args))
            except Exception as e:
                return error(e)

        wrapped.__name__ = func.__name__
        return app.route(route, methods=methods)(wrapped)

    return decorator


def get(route):
    return rpc(route, ["GET"])


def post(route):
    return rpc(route, ["POST"])


@get("/listen")
def listen(channel: str):
    return get_channel(channel).listen()


@post("/send")
def send(message: str, channel: str):
    return get_channel(channel).send(message)
