
import os
from ipdata import ipdata
from pprint import pprint
import json
from dotenv import load_dotenv
load_dotenv()

from common.dynamodb_queries import get_ip, save_ip, parse_dynamo_item, update_tracking_event

IPDATA_API_KEY = os.environ['IPDATA_API_KEY']


def whois(event, context):
   
    records = event['Records'] or []
    
    for r in records:
      # ignore all events except insert
      if r.get('eventName') != 'INSERT':
        continue
      
      #format record
      dynamodb = parse_dynamo_item(r['dynamodb']['NewImage']) 
      ip = dynamodb['ip']

      #lookup in ipTable if we already have the data
      ip_data = get_ip(ip)
      
      # fetch from ipdata API if not
      if not ip_data:
        ipdata_client = ipdata.IPData(IPDATA_API_KEY)
        ip_data = ipdata_client.lookup(
            ip, fields=['ip', 'asn', 'country_name', 'city'])
        
        save_ip(ip, ip_data)

      # update tracking event
      name = ip_data['name']
      industry = ip_data['type']
      city = ip_data['city']
      country = ip_data['country']
      update_tracking_event(event=dynamodb, name=name, industry=industry, city=city, country=country)



if __name__ == "__main__":
    event = {
        "Records":[
            {
              "eventID":"7fde6decdaa179a2d45a742c2acc70d0",
              "eventName":"INSERT",
              "eventVersion":"1.1",
              "eventSource":"aws:dynamodb",
              "awsRegion":"eu-central-1",
              "dynamodb":{
                  "ApproximateCreationDateTime":1614692798.0,
                  "Keys":{
                    "eventId":{
                        "S":"176dfb48abe94ea4884e43bb2c0200a2"
                    },
                    "createdAt":{
                        "S":"2021-03-02 13:46:38"
                    }
                  },
                  "NewImage":{
                    "createdAt":{
                        "S":"2021-03-02 13:46:38"
                    },
                    "eventId":{
                        "S":"176dfb48abe94ea4884e43bb2c0200a2"
                    },
                    "redirectUrl":{
                        "S":"https://thomaszipner.com?utm_source=cv&utm_medium=cv-v1.0&utm_campaign=9ffb2ffb0eadb531577c39040186192a"
                    },
                    "trackingUrl":{
                        "S":"https://rdr.thomaszipner.com/786230d2e26fc0a62d01f2e619cc021b"
                    },
                    "ip":{
                        "S":"176.199.210.252"
                    },
                    "cvReceiver":{
                        "S":"Thommy"
                    },
                    "userAgent":{
                        "S":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
                    },
                    "originalUrl":{
                        "S":"https://thomaszipner.com"
                    }
                  },
                  "SequenceNumber":"100000000011250539294",
                  "SizeBytes":518,
                  "StreamViewType":"NEW_AND_OLD_IMAGES"
              },
              "eventSourceARN":"arn:aws:dynamodb:eu-central-1:197483251147:table/redirectTrackingTable/stream/2021-03-02T13:37:29.587"
            }
        ]
      }
    whois(event, {})
