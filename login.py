import os
import hashlib
from dotenv import load_dotenv
from firstock import firstock

# Load environment variables from .env file
load_dotenv()



def main():
    user_id = os.getenv("FIRSTOCK_USER_ID")
    password = os.getenv("FIRSTOCK_PASSWORD")
    totp = os.getenv("FIRSTOCK_TOTP")
    vendor_code = os.getenv("FIRSTOCK_VENDOR_CODE")
    api_key = os.getenv("FIRSTOCK_API_KEY")

    if not all([user_id, password, totp, vendor_code, api_key]):
        print("Error: Missing credentials in .env file.")
        print("Please ensure FIRSTOCK_USER_ID, FIRSTOCK_PASSWORD, FIRSTOCK_TOTP, FIRSTOCK_VENDOR_CODE, and FIRSTOCK_API_KEY are set.")
        return

    login_request = dict(
        userId=user_id,
        password=password,
        TOTP=totp,
        vendorCode=vendor_code,
        apiKey=api_key
    )

    try:
        print(f"Attempting Firstock login for user: {user_id}...")
        login_response = firstock.login(**login_request)
        print("\nLogin Response:")
        print(login_response)
        
        # Upon success, you'll get a susertoken in the return response data
        if login_response and isinstance(login_response, dict) and login_response.get("status") == "success":
            print("\nLogin successful! Save the 'susertoken' for authenticated endpoints.")
    except Exception as e:
        print(f"\nAn error occurred during login: {e}")

if __name__ == "__main__":
    main()
