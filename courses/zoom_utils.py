import requests
from django.conf import settings

def get_zoom_token():
    url = "https://zoom.us/oauth/token"
    
    headers = {
        "Authorization": f"Basic {settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    }

    data = {
        "grant_type": "account_credentials",
        "account_id": settings.ZOOM_ACCOUNT_ID
    }
    response = requests.post(url=url, headers=headers, data=data)
    return response.json()['access_token']

def create_meeting(topic, start_time):
    token = get_zoom_token()
    url = "https://api.zoom.us/v2/users/me/meetings"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": 60,
        "timezone": "UTC",
        "agenda": "Your meeting agenda"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()