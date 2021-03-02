from urllib.parse import urlencode
import hashlib
import os
from common.dynamodb_queries import get_url_from_dynamodb, create_url_in_dynamodb

REDIRECT_SERVICE_BASE_URL = os.environ['REDIRECT_SERVICE_BASE_URL']
CV_VERSION  = os.environ['CV_VERSION']
url_memo = {}

def create_redirect( url, params ):

  # e.g. tel: & mailto:
  if not url.startswith( 'http' ):
    return url
  
  cv_receiver = params['cv_receiver']
  cv_receiver_hash = params['cv_receiver_hash']
  utm_params = params['utm']

  url_object = {
    'urlId': None,
    'createdAt': None,
    'redirectUrl': None,
    'originalUrl': None,
    'trackingUrl': None,
    'cvReceiver': cv_receiver,
    'cvReceiverHash': cv_receiver_hash,
    'version': CV_VERSION,
  }

  original_url = url
  url_with_utm_params = original_url + "?" + urlencode(utm_params)
  hash_object = hashlib.md5(url_with_utm_params.encode())
  url_id = hash_object.hexdigest()

  url_object.update({
    'urlId': url_id,
    'createdAt': None,
    'redirectUrl': url_with_utm_params,
    'originalUrl': original_url,
    'trackingUrl': REDIRECT_SERVICE_BASE_URL + "/" + url_id,
  })

  if url_id not in url_memo:

    url_from_dynamo_db = get_url_from_dynamodb(url_id)
    if url_from_dynamo_db:
      print("😎 From DynamoDB", original_url)
      url_memo[url_id] = url_from_dynamo_db
    else:
      result = create_url_in_dynamodb(  url_object )
      print("🎉 Created new Url in DynamoDB", original_url)
      url_memo[url_id] = url_object     
  else:
    print("😉 From Memo Cache", original_url)
  
  tracking_url = url_object['trackingUrl']
  return tracking_url
