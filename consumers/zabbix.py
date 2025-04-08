import requests
from datetime import datetime, timedelta

class Zabbix:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def login(self):
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"username": self.username, "password": self.password},
            "id": 1,
        }
        auth_response = requests.post(self.host, json=auth_payload)
        return auth_response.json().get("result")
    
    def get_items(self, auth_token, hostname):
        item_payload = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "host": hostname,
                "output": ["itemid", "name", "key_", "lastvalue"]
            },
            "id": 2,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        response = requests.post(self.host, json=item_payload, headers=headers)
        return response.json().get("result", [])
    
    def get_history(self, auth_token, item_id):
        now = int(datetime.now().timestamp())
        one_month_ago = int((datetime.now() - timedelta(days=30)).timestamp())

        history_payload = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": ["clock", "value"],
                "history": 3,  # Tipo 3 = float (CPU e Memória)
                "itemids": item_id,
                "time_from": one_month_ago,
                "time_till": now,
                "sortfield": "clock",
                "sortorder": "ASC",
                "limit": 1000,  # Ajuste conforme necessário
            },
            "id": 3,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }

        history_response = requests.post(self.host, json=history_payload, headers=headers)
        return history_response.json().get("result", [])