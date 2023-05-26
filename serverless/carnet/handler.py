import io
import json
from pprint import pprint
from urllib.request import urlopen, Request
import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
from decimal import Decimal
from botocore.vendored import requests
import time
import os
import urllib

carnetdb = os.environ['DYNAMO_DB_TABLEcarnet']
rekognitiondb = os.environ['DYNAMO_DB_TABLErekognition']
s3_client = boto3.client("s3")


def carnet(bucket, object_key, url):
  response = requests.post('https://carnet.ai/recognize-url', data=url)
  status_code = response.status_code
  print(response)
  if status_code == 200:
    data = response.json()
    print(data)
    save_carnet_info_to_dynamodb(data)
  elif status_code == 429:
    print("Bad API response: 429. Retrying after half a second...")
    time.sleep(0.5)
  elif status_code == 500:
    err = "Image doesn't contain a car"
    if response.json()['error'] == err:
      awsrekognition_result = get_image_labels(bucket, object_key)
      print(f"Result from Aws Recognition: {awsrekognition_result}")
      save_aws_rekognition_info_to_dynamodb(awsrekognition_result)
    else:
      print(f"Bad API response: {status_code}")
  else:
    print(f"Bad API response: {status_code}")


def save_aws_rekognition_info_to_dynamodb(data):
  dynamodb = boto3.client('dynamodb')
  timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
  serializer = TypeSerializer()
  dynamo_serialized_data = []
  json_data = json.dumps(data)

  data_ready_to_be_saved = {
    'id': {
      'S': str(uuid.uuid1())
    },
    'createdAt': {
      'S': timestamp
    },
    'updatedAt': {
      'S': timestamp
    },
    'rekognition': {
      'S': json_data
    }
  }

  try:
    dynamodb.put_item(TableName=rekognitiondb, Item=data_ready_to_be_saved)
    pass
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  return


def save_carnet_info_to_dynamodb(data):
  dynamodb = boto3.client('dynamodb')
  timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
  serializer = TypeSerializer()
  dynamo_serialized_data = []

  for item in data.items():
    items_dic = {}
    items_dic[item[0]] = item[1]
    item_str = json.dumps(items_dic)
    print(item_str)
    dynamo_serialized_data.append(items_dic)
  print(dynamo_serialized_data)
  data_ready_to_be_saved = {
    'id': {
      'S': str(uuid.uuid1())
    },
    'createdAt': {
      'S': timestamp
    },
    'updatedAt': {
      'S': timestamp
    },
    'carnet': {
      'S': json.dumps(data)
    }
  }
  print(json.dumps(data_ready_to_be_saved))

  try:
    dynamodb.put_item(TableName=carnetdb, Item=data_ready_to_be_saved)
    pass
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  return


def get_image_labels(bucket, key):
  rekognition_client = boto3.client('rekognition')
  response = rekognition_client.detect_labels(
    Image={'S3Object': {
      'Bucket': bucket,
      'Name': key
    }}, MaxLabels=10)

  return response


def lambda_handler(event, _):
  pprint(event)
  for record in event.get("Records"):
    bucket = record.get("s3").get("bucket").get("name")
    key = record.get("s3").get("object").get("key")
    location = boto3.client('s3').get_bucket_location(
      Bucket=bucket)['LocationConstraint']
    url = f'https://{bucket}.s3.{location}.amazonaws.com/{key}'

    result = carnet(bucket, key, url)

  return {"statusCode": 200, "body": "Done!"}
