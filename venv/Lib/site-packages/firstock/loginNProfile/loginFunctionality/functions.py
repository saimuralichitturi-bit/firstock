import hashlib
import json
import os
import ast
import requests
from firstock.Variables.common_imports import *
from firstock.loginNProfile.loginFunctionality.base import *

def encodePwd(pwd):
    """
    Encode password using SHA256.
    
    :param pwd: Plain text password
    :return: Hexadecimal string of hashed password
    """
    return hashlib.sha256(pwd.encode()).hexdigest()

class ApiRequests(FirstockAPI):
    def firstockLogin(self, uid: str, pwd: str, factor2: str, vc: str, appkey: str):
        """
        Perform login and store user token in config.json.
        
        :param uid: User ID
        :param pwd: Password
        :param factor2: TOTP factor
        :param vc: Vendor code
        :param appkey: API key
        :return: JSON response from the login request
        """
        url = LOGIN
        encrypted_password = encodePwd(pwd)

        payload = {
            "userId": uid,
            "password": encrypted_password,
            "TOTP": factor2,
            "vendorCode": vc,
            "apiKey": appkey
        }

        try:
            result = requests.post(url, json=payload)
            result.raise_for_status()  # Raise exception for HTTP errors
            json_string = result.content.decode("utf-8")
            final_result = ast.literal_eval(json_string)

            if "status" in final_result and final_result["status"] == "success":
                # Ensure config.json exists
                config_path = CONFIG_PATH
                if not os.path.exists(config_path):
                    with open(config_path, "w") as config_file:
                        json.dump({}, config_file)

                # Read existing config or create new if empty/invalid
                try:
                    with open(config_path, "r") as infile:
                        try:
                            config_data = json.load(infile)
                        except json.JSONDecodeError:
                            config_data = {}
                except FileNotFoundError:
                    config_data = {}

                # Update config with user data
                config_data[uid] = {"jKey": final_result["data"]["susertoken"]}

                # Write updated config back to file
                with open(config_path, "w") as outfile:
                    json.dump(config_data, outfile, indent=4)

                return final_result
            else:
                return final_result

        except requests.RequestException as e:
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            return {"status": "failed", "message": f"Unexpected error: {str(e)}"}