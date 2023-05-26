import asyncio
import aiohttp
import os
import zipfile
import boto3
from os import getenv
from dotenv import load_dotenv
import logging
import argparse
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
s3 = boto3.client('s3')
load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument('--download', "-d", nargs='?', const='true', help='download images from myauto' )
parser.add_argument('--upload', "-u", nargs='?', const='true', help='upload to s3 bucket' )
parser.add_argument('--bucket_name', "-bn", type=str, help='Name of S3 bucket')
s3 = boto3.client('s3')
args = parser.parse_args()
# Specify the endpoint URL
auto_page_n = lambda nth_page: f"https://api2.myauto.ge/ka/products?TypeID=0&ForRent=&Mans=&CurrencyID=3&MileageType=1&Page={nth_page}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3"
}

def set_object_access_policy(s3_client, bucket_name, file):
    try:
        response = s3_client.put_object_acl(
            ACL="public-read",
            Bucket=bucket_name,
            Key=file
        )
    except ClientError as e:
        logging.error(e)
        return False
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False
 
    return json.dumps(policy)
def init_client():
    try:
        client = boto3.client("s3",
                              aws_access_key_id=getenv("aws_access_key_id"),
                              aws_secret_access_key=getenv(
                                  "aws_secret_access_key"),
                              aws_session_token=getenv("aws_session_token"),
                              region_name=getenv("aws_region_name")
                              #  config=botocore.client.Config(
                              #      connect_timeout=conf.remote_cfg["remote_timeout"],
                              #      read_timeout=conf.remote_cfg["remote_timeout"],
                              #      region_name=conf.remote_cfg["aws_default_region"],
                              #      retries={
                              #          "max_attempts": conf.remote_cfg["remote_retries"]}
                              )
        # check if credentials are correct
        return client
    except ClientError as e:
        logging.error(e)
    except:
        logging.error("Unexpected error")
if __name__ == "__main__":
    s3_client = init_client()
async def download_image(session, url, save_directory):
    try:
        async with session.get(url) as response:
            response.raise_for_status()

            # Extract the filename from the URL
            filename = os.path.basename(url)

            # Save the image to the specified directory
            save_path = os.path.join(save_directory, filename)
            with open(save_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            print(f"Downloaded: {filename}")
    except aiohttp.ClientError as e:
        print(f"Error downloading image: {e}")


async def main():
    image_urls = []  # List to store image URLs

    async with aiohttp.ClientSession(headers=headers) as session:
        for page_n in range(1):
            response = await session.get(auto_page_n(page_n))
            response.raise_for_status()

            data = await response.json()

            for item in data['data']['items']:
                car_id = item['car_id']
                photo = item['photo']
                picn = item['pic_number']
                print(f"Car ID: {car_id}")
                print("Image URLs:")
                for id in range(1, picn + 1):
                    image_url = f"https://static.my.ge/myauto/photos/{photo}/large/{car_id}_{id}.jpg"
                    image_urls.append(image_url)
                    print(image_url)
                print()

        # Create a folder to store downloaded images
        save_directory = "downloaded_images"
        os.makedirs(save_directory, exist_ok=True)

        # Download images asynchronously
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in image_urls:
                task = asyncio.ensure_future(download_image(session, url, save_directory))
                tasks.append(task)

            await asyncio.gather(*tasks)


      


        total_images = sum(len(files) for _, _, files in os.walk(save_directory))
        print(f"Total number of downloaded images: {total_images}")
def upload(s3_client, bucket_name):
      # Upload images to S3 bucket
        s3 = boto3.client('s3')
        bucket_name = args.bucket_name
        for root, _, files in os.walk("downloaded_images"):
            for file in files:
                with open(os.path.join(root, file), 'rb') as f:
                    s3_client.upload_fileobj(f, bucket_name, file)
                print(f"Uploaded {file} to S3 bucket")
                set_object_access_policy(s3_client, args.bucket_name, file)
if args.download:
    asyncio.run(main())
if args.upload:
    upload(s3_client, args.bucket_name)