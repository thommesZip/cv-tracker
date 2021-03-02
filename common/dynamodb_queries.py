import os
import boto3
import time
import uuid
import json

client = boto3.client('dynamodb')
REDIRECT_URLS_TABLE = os.environ['REDIRECT_URLS_TABLE']
REDIRECT_TRACKING_TABLE = os.environ['REDIRECT_TRACKING_TABLE']
IP_TABLE = os.environ['IP_TABLE']


def get_url_from_dynamodb(url_id):

    resp = client.get_item(
        TableName=REDIRECT_URLS_TABLE,
        Key={
            'urlId': {'S': url_id},
            # 'createdAt': {'S': '' },
        }
    )
    item = resp.get('Item')
    return parse_dynamo_item(item)


def create_url_in_dynamodb(url_object):

    resp = client.put_item(
        TableName=REDIRECT_URLS_TABLE,
        Item={
            'urlId': {'S': url_object['urlId']},
            'createdAt': {'S': time.strftime('%Y-%m-%d %H:%M:%S')},
            'redirectUrl': {'S': url_object['redirectUrl']},
            'originalUrl': {'S': url_object['originalUrl']},
            'trackingUrl': {'S': url_object['trackingUrl']},
            'cvReceiver': {'S': url_object['cvReceiver']},
            'cvReceiverHash': {'S': url_object['cvReceiverHash']},
        }
    )

    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Sorry, could not create trackingUrl", {
            'urlId': {'S': url_object['urlId']},
            'createdAt': {'S': time.strftime('%Y-%m-%d %H:%M:%S')},
            'redirectUrl': {'S': url_object['redirectUrl']},
            'originalUrl': {'S': url_object['originalUrl']},
            'trackingUrl': {'S': url_object['trackingUrl']},
            'cvReceiver': {'S': url_object['cvReceiver']},
        })
    return True


def track(url_object, user_info):

    item = {
        'eventId': {'S': uuid.uuid4().hex},
        'createdAt': {'S': time.strftime('%Y-%m-%d %H:%M:%S')},
        'redirectUrl': {'S': url_object['redirectUrl']},
        'originalUrl': {'S': url_object['originalUrl']},
        'trackingUrl': {'S': url_object['trackingUrl']},
        'cvReceiver': {'S': url_object['cvReceiver']},
        'ip': {'S': user_info['ip']},
        'userAgent': {'S': user_info['userAgent']}
        }

    resp = client.put_item(
        TableName=REDIRECT_TRACKING_TABLE,
        Item=item
    )

    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Sorry, could not track", item)
    return True


def update_tracking_event(event, name="", industry="", city="", country=""):

    resp = client.update_item(
        TableName=REDIRECT_TRACKING_TABLE,
        Key={
            'eventId': {'S': event['eventId']},
            'createdAt': {'S': event['createdAt']}
        },
        ReturnValues='UPDATED_NEW',
        ExpressionAttributeNames={
            '#CN': 'ipName',
            '#CT': 'ipType',
            '#CI': 'city',
            '#CC': 'country',
        },
        ExpressionAttributeValues={
            ':cn': {
                'S': name or "",
            },
            ':ct': {
                'S': industry or "",
            },
            ':ci': {
                'S': city or "",
            },
            ':cc': {
                'S': country or "",
            },
        },
        UpdateExpression='SET #CN = :cn, #CT = :ct, #CI = :ci, #CC = :cc',
    )

    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Sorry, could not update tracking event")
    return True


def get_ip(ip):
    resp = client.get_item(
        TableName=IP_TABLE,
        Key={
            'ip': {'S': ip},
            # 'createdAt': {'S': '' },
        }
    )
    item = resp.get('Item')
    return parse_dynamo_item(item)


def save_ip(ip, info):

    ip_object = {
        'ip': {'S': ip},
        'createdAt': {'S': time.strftime('%Y-%m-%d %H:%M:%S')},
    }

    ip_object.update({
        'name': {'S': info['asn']['name'] or ''},
        'country': {'S': info['country_name'] or ''},
        'city': {'S': info['city'] or ''},
        'type': {'S': json.dumps(info['asn']['type']) or ''},
        'asn': {'S': json.dumps(info['asn']) or ''},
    })

    resp = client.put_item(
        TableName=IP_TABLE,
        Item=ip_object
    )

    if resp['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Sorry, could not save ip object", ip_object)

    return True


def parse_dynamo_item(item):
    resp = {}
    if not item:
        return resp

    if type(item) is str:
        return item
    for key, struct in item.items():
        if type(struct) is str:
            if key == 'I':
                return int(struct)
            else:
                return struct
        else:
            for k, v in struct.items():
                if k == 'L':
                    value = []
                    for i in v:
                        value.append(parse_dynamo_item(i))
                elif k == 'S':
                    value = str(v)
                elif k == 'I':
                    value = int(v)
                elif k == 'M':
                    value = {}
                    for a, b in v.items():
                        value[a] = parse_dynamo_item(b)
                else:
                    key = k
                    value = parse_dynamo_item(v)

                resp[key] = value

    return resp
