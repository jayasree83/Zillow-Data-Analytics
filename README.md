# Zillow-Data-Analytics - End to End Data Pipeline and Analytics on AWS
This project implements an end-to-end data pipeline for processing and analyzing property listings from the Zillow API. Hosted on AWS, it automates data ingestion, processing, transformation, and visualization.

# Key Features
- **Data Ingestion**: Fetches property data from Zillow API using AWS Lambda.
- **Data Lake Setup**: Utilizes S3 for raw, cleansed, and analytical data storage.
- **Data Transformation**: Converts **raw JSON to Parquet format**, cleanses, and **partitions** the data using AWS Glue ETL jobs.
- **Data Analysis & Visualization**: Visualizes data through Amazon QuickSight, powered by Athena queries on Glue Data Catalog.
- **Monitoring**: CloudWatch tracks Lambda functions and Glue jobs.
- **Access Control**: IAM roles and policies ensure secure interactions between AWS services.

# Services Used
- **AWS Lambda**: Data ingestion and transformation
- **Amazon S3**: Data storage
- **AWS Glue**: Schema detection, ETL jobs, data catalog
- **Athena**: SQL-based querying and analysis
- **Amazon QuickSight**: Data visualization and reporting
- **CloudWatch**: Monitoring and logging
- **IAM**: Access control

# Architecture
![image](https://github.com/user-attachments/assets/c2b39154-eba7-45f6-8f63-6ada32749fde)


# Workflow
1. **Data Ingestion**: AWS Lambda fetches real-time property data (JSON format) from Zillow API and stores it in S3.
2. **Data Classification**: AWS Glue crawlers infer schema and catalog raw data.
3. **Data Transformation**: AWS Glue ETL jobs clean and transform data, storing results in S3 as Parquet files.
4. **Visualization**: Amazon QuickSight queries Athena for insights, creating dashboards for analysis.
5. **Access Control**: IAM usergroups, users, roles, policies restrict access following principle of least privilege allowing only minimal required access for every service throughout.
