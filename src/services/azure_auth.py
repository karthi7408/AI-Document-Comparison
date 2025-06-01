import os
from dotenv import load_dotenv

load_dotenv()


class AzureAuth:
    def __init__(self, client_id=None, client_secret=None, tenant_id=None):
        self.client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        self.token = None

    def authenticate(self):
        import requests

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://<your-resource>.azure.com/.default"
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            raise Exception("Authentication failed: " + response.text)

    def get_access_token(self):
        if not self.token:
            self.authenticate()
        return self.token

    def is_token_valid(self):
        """
        Checks if the current token is valid (not expired).
        For simplicity, this just checks if token exists.
        """
        return self.token is not None

    def refresh_token(self):
        """
        Force refresh the access token.
        """
        self.token = None
        return self.get_access_token()

    def get_authorization_header(self):
        """
        Returns the Authorization header for Azure API requests.
        """
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def test_authentication(self):
        """
        Test if authentication works and token is valid.
        Returns True if successful, raises Exception otherwise.
        """
        token = self.get_access_token()
        if not token or not isinstance(token, str):
            raise Exception("Invalid Azure access token.")
        return True