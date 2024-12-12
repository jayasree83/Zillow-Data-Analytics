from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
import requests
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

#load config file
with open('/home/ubuntu/airflow/api_config.json', 'r') as config_file:
    api_host_key = json.load(config_file)

now = datetime.now()
dt_now_string = now.strftime("%d%m%Y%H%M%S")

s3_bucket = 'asp-cleaned-data-bucket'

def fetch_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']

    #Extracting location from querystring
    location = querystring.get('location','')

    response = requests.get(url, headers = headers, params=querystring)
    response_data = response.json()
 

    #output file path with loc prefix
    output_file_path = f"/home/ubuntu/response_data_{location}_{dt_string}.json"
    file_str = f"response_data_{location}_{dt_string}.csv"

    #write JSON response to a file
    with open(output_file_path, "w") as output_file:
        json.dump(response_data, output_file, indent=5)

    #File path and filename for next tasks
    output_list = [output_file_path, file_str]
    return output_list

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024,12,2),
    'email': ['jayasree.jas@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(seconds=25)
}


with DAG('zillow_analytics_dag',
        default_args = default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:

        extract_zillow_data = PythonOperator(
            task_id = 'tsk_extract_data',
            python_callable = fetch_zillow_data,
            op_kwargs = {'url':'https://zillow-com4.p.rapidapi.com/properties/search',
                        'querystring':{"location":"WA","resultsPerPage":"250"},
                        'headers': api_host_key,
                        'date_string': dt_now_string
                        }
        )

        load_to_s3 = BashOperator(
            task_id = 'tsk_load_to_s3',
            bash_command = 'aws s3 mv {{ti.xcom_pull("tsk_extract_data")[0]}} s3://asp-project-jayasree/',
        )

        is_file_in_s3 = S3KeySensor(task_id='tsk_is_file_in_s3',
            bucket_key='{{ti.xcom_pull("tsk_extract_data")[0]}}',
            bucket_name=s3_bucket,
            aws_conn_id='aws_s3_conn',
            wildcard_match=False,  
            timeout=120,  
            poke_interval=30,  
        )

	transfer_s3_to_redshift = S3ToRedshiftOperator(
        task_id="tsk_transfer_s3_to_redshift",
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket=s3_bucket,
        s3_key='{{ti.xcom_pull("tsk_extract_zillow_data_var")[1]}}',
        schema="PUBLIC",
        table="zillowdata",
        copy_options=["csv IGNOREHEADER 1"],
    	)


        extract_zillow_data >> load_to_s3 >> is_file_in_s3 >> transfer_s3_to_redshift

        
