from google.api_core.client_options import ClientOptions
from google.oauth2.service_account import Credentials
from google.cloud import firestore
import json
from dotenv import load_dotenv
import os

load_dotenv()

CRED = Credentials.from_service_account_info(
    json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
)

def get_client(database: str) -> firestore.Client:

    client = firestore.Client(credentials=CRED, database=database)

    return client

