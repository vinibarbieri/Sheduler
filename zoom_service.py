import requests
import json
import base64
import os
import datetime

ZOOM_CONFIG = {
    "scheduler_1": {

        "CLIENT_ID": '', # Usar .env
        "CLIENT_SECRET": '', # Usar .env
        "TOKEN_FILE": 'zoom_token_1.json'
    },
    "scheduler_2": {
        "CLIENT_ID": '', # Usar .env
        "CLIENT_SECRET": '', # Usar .env
        "TOKEN_FILE": 'zoom_token_2.json'
    }
}

TOKEN_FILE = 'zoom_token'

REDIRECT_URI = 'http://localhost:5000/callback'
TOKEN_URL = 'https://zoom.us/oauth/token'

def get_zoom_authorization_url(scheduler_type, client_id, redirect_uri):
    AUTH_URL = 'https://zoom.us/oauth/authorize'
    return f'{AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}'

def save_tokens(tokens, scheduler_type):
    with open(f'{TOKEN_FILE}_{scheduler_type}', 'w') as f:
        json.dump(tokens, f)

def load_tokens(scheduler_type):
    if os.path.exists(f'{TOKEN_FILE}_{scheduler_type}'):
        with open(f'{TOKEN_FILE}_{scheduler_type}', 'r') as f:
            return json.load(f)
    return None

def refresh_zoom_token(scheduler_type, refresh_token):
    config = ZOOM_CONFIG[scheduler_type]
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    client_creds = f"{config['CLIENT_ID']}:{config['CLIENT_SECRET']}"
    encoded_creds = base64.b64encode(client_creds.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        tokens['expires_at'] = (datetime.datetime.utcnow() + datetime.timedelta(seconds=tokens.get('expires_in'))).isoformat()
        save_tokens(scheduler_type, tokens)
        return tokens
    else:
        raise Exception(f"Failed to refresh access token: {response.status_code} - {response.text}")

def get_access_token(scheduler_type):
    tokens = load_tokens(scheduler_type)
    if tokens:
        access_token = tokens.get('access_token')
        expires_at = tokens.get('expires_at')
        if datetime.datetime.utcnow() < datetime.datetime.fromisoformat(expires_at):
            return access_token
        else:
            new_tokens = refresh_zoom_token(scheduler_type, tokens.get('refresh_token'))
            save_tokens(scheduler_type, new_tokens)
            return new_tokens.get('access_token')
    else:
        return None

def get_zoom_tokens(auth_code, client_id, client_secret, redirect_uri, scheduler_type):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    client_creds = f"{client_id}:{client_secret}"
    encoded_creds = base64.b64encode(client_creds.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        tokens['expires_at'] = (datetime.datetime.utcnow() + datetime.timedelta(seconds=tokens.get('expires_in'))).isoformat()
        save_tokens(tokens, scheduler_type)
        return tokens
    else:
        raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")

def create_zoom_meeting(scheduler_type, topic, start_time="2023-08-15T10:00:00Z", duration=30, timezone="UTC"):
    access_token = get_access_token(scheduler_type)
    if not access_token:

        raise Exception("No valid access token found. Please authenticate with Zoom.")
        
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    meeting_details = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
        "duration": duration,
        "timezone": timezone,
        "agenda": "Discuss about the scheduler integration",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "watermark": False,
            "use_pmi": False,
            "approval_type": 2,
            "registration_type": 1,
            "audio": "both",
            "auto_recording": "none"
        }
    }
    response = requests.post(
        'https://api.zoom.us/v2/users/me/meetings',
        headers=headers,
        data=json.dumps(meeting_details)
    )
    if response.status_code == 201:
        return response.json().get('join_url')
    else:
        raise Exception(f"Failed to create Zoom meeting: {response.status_code} - {response.text}")
