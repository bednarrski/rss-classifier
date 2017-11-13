# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

# {'userId': '1005689817', 'userName': 'piotrbednarski', 'userProfileId': '1005689817', 'userEmail': 'piotrbednarski@outlook.com', 'isBloggerUser': False, 'signupTimeSec': 1434090152, 'isMultiLoginEnabled': False}

def inoreader_request(request):
    print("\nRequesting: {0}".format(request))
    
    url = 'https://www.inoreader.com/reader/api/0/'+request
    headers = {
        'Authorization' : 'GoogleLogin auth=14PITym6qD9nKTCXMIdGKToekweKOxag',
        'AppId' : '1000000409',
        'AppKey': '8MWwXKpgOW00SdAZb67EnoRaEnjAUYTS'
    }
    r = requests.get(url, headers=headers)

    print(r.status_code, r.reason)
    resp = r.json()
    return resp

if __name__ == '__main__':

    inputs = ['user-info']

    for sample_input in inputs:
        test = inoreader_request(sample_input)
        print(test)
