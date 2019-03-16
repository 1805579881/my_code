import time

import requests

domain = 'http://127.0.0.1:8000/sync/heart_beats/'

while True:
    time.sleep(0.5)
    headers = {
        'device-id': '51f931ba-18d9-4d2a-b27a-e16a88694988',
        'Content-Type': 'application/json',
    }
    response = requests.post(domain, headers=headers)
    print('device 1 done')
    print(response.json())
