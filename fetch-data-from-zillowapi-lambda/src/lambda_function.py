import boto3
import requests
import os
import json
from datetime import datetime

# Fetching environment variables from Lambda configuration
s3_bucket = os.environ['s3_bucket']
s3_prefix = os.environ['s3_prefix']
api_url = os.environ['api_url']
api_key = os.environ['api_key']
api_host = os.environ['api_host']
location = os.environ['location']
results_per_page = os.environ['results_per_page']

# Initializing S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # API request
        querystring = {
            "location": location,
            "resultsPerPage": results_per_page
        }
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api_host
        }

        response = requests.get(api_url, headers=headers, params=querystring)
        
        raw_data = response.json()

        # Generate S3 object key
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        location_clean = location.replace(" ", "_").lower()
        s3_key = f"{s3_prefix}{location_clean}_{timestamp}.json"

        # Upload the raw JSON data to S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=json.dumps(raw_data),
            ContentType='application/json'
        )

        return {
            "statusCode": 200,
            "body": f"Raw JSON data successfully uploaded to s3://{s3_bucket}/{s3_key}"
        }

    except requests.exceptions.RequestException as api_error:
        print(f"API Request Error: {api_error}")
        raise api_error
    except Exception as e:
        print(f"Error: {e}")
        raise e