from os import environ
import logging
import requests
from cartesi_wallet.util import hex_to_str, str_to_hex
import json
from turtle_plot import draw_with_turtle_to_base64

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    sender = data["metadata"]["msg_sender"].lower()
    payload = hex_to_str(data["payload"])
    logger.info(f"Payload: {payload}")

    try:
        payload = json.loads(payload)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        response = requests.post(rollup_server + "/report", json={"payload": str_to_hex("Invalid JSON format")})
        return "reject"

    method = payload.get("method", {})

    if method == "draw":

        user_code = payload.get("code", {})

        if not user_code:
            logger.error("No code provided in payload")
            response = requests.post(rollup_server + "/report", json={"payload": str_to_hex("User code is NOT provided in payload")})
            return "reject"

        try:
            server_generated_base64 = draw_with_turtle_to_base64(user_code)
            logger.info(f"Image Data: {server_generated_base64}")
            response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(server_generated_base64)})
        except Exception as e:
            logger.error(f"Error in user code execution: {e}")
            response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(f"Error executing draw code: {e}")})
            return "reject"

    else:
        # reject the input
        logger.warn("Invalid method in the input JSON string")
        response = requests.post(rollup_server + "/report", json={"payload": str_to_hex("Invalid method in the input JSON string")})
        return "reject"

    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
