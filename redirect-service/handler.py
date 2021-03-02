import sys
import os
import json
# import boto3
import uuid
import time
from common.dynamodb_queries import get_url_from_dynamodb, track

URL_NOT_FOUND_REDIRECT = os.environ['URL_NOT_FOUND_REDIRECT']

errorResponse = {
            "statusCode": 302,
            "headers": {
                'Location': URL_NOT_FOUND_REDIRECT
                },
            "body": ""
        }

def get_redirect_response(url_object):
    return {
            "statusCode": 302,
            "headers": {
                'Location': url_object['redirectUrl']
                },
            "body": ""
        }

def redirect(event, context):

    response = {}
    if not event['path'] or len(event['path']) < 2:
        return errorResponse

    url_id = event['path'].rsplit('/', 1)[-1]
    url_object = get_url_from_dynamodb(url_id)

    if not url_object:
        return errorResponse
    
    user_info = {
        'ip' : event['requestContext']['identity']['sourceIp'],
        'userAgent' : event['requestContext']['identity']['userAgent']
    }


    track(url_object, user_info)

    # testResponse = {
    #         "statusCode": 200,
    #         "body":  json.dumps({
    #             'user_info':user_info
    #         })
    #     }
    # return testResponse
    return get_redirect_response( url_object )
    

if __name__ == "__main__":
    redirect({'path': 'some/path'},{})


