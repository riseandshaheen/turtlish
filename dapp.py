from os import environ
import logging
import requests
from cartesi_wallet.util import hex_to_str, str_to_hex
import json
from turtle_plot import draw_with_turtle_to_base64
from eth_abi import encode, decode

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

DAPP_CONTRACT_ADDRESS = ""
NFT_CONTRACT_ADDRESS = ""

def binary2hex(binary):
    """
    Encode a binary as an hex string
    """
    return "0x" + binary.hex()

def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    sender = data["metadata"]["msg_sender"].lower()

    # relay dapp address, one time execution 
    if sender == "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE".lower():
        global DAPP_CONTRACT_ADDRESS
        logger.info(f"Received advance request from dapp relayer")
        DAPP_CONTRACT_ADDRESS = data["payload"]
        print(f"Relayed dapp address: {DAPP_CONTRACT_ADDRESS}")
        return "accept"
    
    try:
        payload = hex_to_str(data["payload"])
        logger.info(f"Payload: {payload}")
        payload = json.loads(payload)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        response = requests.post(rollup_server + "/report", json={"payload": str_to_hex("Invalid JSON format")})
        return "reject"

    method = payload.get("method", {})

    # set nft contract address
    if method == "set_nft_address": # {"method":"set_nft_address", "address":"0x1234..."}
        global NFT_CONTRACT_ADDRESS
        NFT_CONTRACT_ADDRESS = payload.get("address", {})
        print(f"nft address set as: {NFT_CONTRACT_ADDRESS}")
        return "accept"

    # draw to mint nft
    elif method == "draw":

        user_code = payload.get("code", {})

        if not user_code:
            logger.error("No code provided in payload")
            response = requests.post(rollup_server + "/report", json={"payload": str_to_hex("User code is NOT provided in payload")})
            return "reject"

        try:
            server_generated_base64 = draw_with_turtle_to_base64(user_code)
            logger.info(f"Image Data: {server_generated_base64}")

            # prepare notice
            notice_json_payload = {
                "creator": sender,
                "image": server_generated_base64
            }
            notice_response = requests.post(rollup_server + "/notice", json={"payload": str_to_hex(json.dumps(notice_json_payload))})
            logger.info(f"Notice Response: {notice_response}")

            # prepare voucher
            MINT_TO_FUNCTION_SELECTOR = b'u^\xdd\x17\xdc\xc4t\x0f\x04w\xcc\xcd\x9e\xfc\xc1\xa5\x07f!\xad\x86\x95\x8f\xfay\xfe\xef\xea\xee\xbf`\xc6'[:4]
            data = encode(['address'], [sender])
            logger.info(f"data encoded :{data}")
            voucher_payload = binary2hex(MINT_TO_FUNCTION_SELECTOR + data)
            voucher_response = requests.post(rollup_server + "/voucher", json={"destination": NFT_CONTRACT_ADDRESS, "payload": voucher_payload})
            logger.info(f"Voucher Response: {voucher_response}")

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
