import awswrangler as wr
import boto3
import pandas as pd
import json
import urllib.parse
import os

s3_cleansed_layer = os.environ['s3_cleansed_layer']
glue_catalog_db_name = os.environ['glue_catalog_db_name']
glue_catalog_table_name = os.environ['glue_catalog_table_name']
write_data_operation = os.environ['write_data_operation']

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:

        response = s3_client.get_object(Bucket=bucket, Key=key)
        raw_json = json.loads(response['Body'].read().decode('utf-8'))

        # Extract the "data" field
        if "data" not in raw_json:
            raise ValueError("JSON file does not contain 'data' key.")

        data_list = raw_json["data"]

        # Ensure the data_list is a list of dictionaries
        if not isinstance(data_list, list) or not all(isinstance(item, dict) for item in data_list):
            raise ValueError("'data' field must be a list of dictionaries.")

        # Normalize JSON to flatten nested fields
        df_normalized = pd.json_normalize(data_list)
        
        
        # Write to S3
        wr_response = wr.s3.to_parquet(
            df=df_normalized,
            path=s3_cleansed_layer,
            dataset=True,
            database=glue_catalog_db_name,
            table=glue_catalog_table_name,
            mode=write_data_operation
        )

        return {
            "statusCode": 200,
            "body": "JSON successfully converted to Parquet and stored in S3.",
            "wr_response": wr_response
        }
        
    except Exception as e:
        print(e)
        print(f"Error processing file {key} from bucket {bucket}: {e}")
        raise e
