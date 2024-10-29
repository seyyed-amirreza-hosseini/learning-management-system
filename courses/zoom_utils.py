from django.conf import settings
import requests
import logging
import base64


def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    client_id = settings.ZOOM_CLIENT_ID
    client_secret = settings.ZOOM_CLIENT_SECRET
    account_id = settings.ZOOM_ACCOUNT_ID

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "account_credentials",
        "account_id": account_id
    }

    response = requests.post(url, headers=headers, data=data)

    # Debugging output for response status and data
    logging.info("Request URL: %s", url)
    logging.info("Request Headers: %s", headers)
    logging.info("Request Data: %s", data)
    logging.info("Response Status Code: %d", response.status_code)
    logging.info("Response JSON: %s", response.json())

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        logging.error(f"Failed to get access token: {response.json()}")
        raise Exception(f"Failed to get access token: {response.json()}")

def create_meeting(topic, start_time):
    token = get_zoom_access_token()
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": 60,
        "timezone": "UTC",
        "agenda": "Your meeting agenda"
    }
    response = requests.post(url, headers=headers, json=payload)

    # Log request details and response for debugging
    logging.info("Request URL: %s", url)
    logging.info("Request Headers: %s", headers)
    logging.info("Request Payload: %s", payload)
    logging.info("Response Status Code: %d", response.status_code)
    logging.info("Response JSON: %s", response.json())

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create meeting: {response.json()}")
