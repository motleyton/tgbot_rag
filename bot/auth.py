import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def authenticate_google_api(credentials_path, token_path, scopes):
    creds = None
    # Загрузка существующего токена, если он есть
    if os.path.exists(token_path):
        with open(token_path, 'r') as token:
            creds = Credentials.from_authorized_user_file(token_path, scopes)

    # Если токен не существует или недействителен, выполните аутентификацию
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        # Сохраните токен для последующего использования
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


# Замените на ваш путь к файлу credentials.json
credentials_path = '/home/bmf/Desktop/freelance/tgbot_rag/Credentials.json'
# Замените на путь, где хотите сохранить token.json
token_path = '/home/bmf/Desktop/freelance/tgbot_rag/token.json'
# Укажите нужные вам разрешения (scopes)
scopes = ['https://www.googleapis.com/auth/drive']

# Выполните аутентификацию и получите токен
authenticate_google_api(credentials_path, token_path, scopes)
