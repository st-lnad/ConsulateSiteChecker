import os

from flask import Flask, jsonify, request

from src.parser.src.parse import parse_docs_status

application = Flask(__name__)
url = os.environ.get("PARSER_ADDRESS")


@application.route("/parser", methods=['GET', 'PUT'])
def send_request_to_parser():
    data = request.get_json()
    # data = json.loads(data)
    status = parse_docs_status(data)
    return jsonify({"status": status})


if __name__ == '__main__':
    try:
        application.run(host="0.0.0.0", port=8082)
    except Exception:
        os._exit(1)
