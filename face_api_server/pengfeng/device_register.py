import time
import json

import requests

domain = 'localhost:8000/sync/devices/create_or_update_device/'
data = {
    "device_info": {
        "uuid": "51f931ba-18d9-4d2a-b27a-e16a88694988",
        "name": "侧门摄像头1",
        "position": "正门",
        "device_type": "IN"
    }
}

headers = {
    'device-id': '58f931ba-18d9-4d2a-b27a-e16a88694988',
    'Content-Type': 'application/json',
}
response = requests.post(domain, json=data, headers=headers)
print(response.json())
