import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality
from awsglue.dynamicframe import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

AmazonS3_node1733542300994 = glueContext.create_dynamic_frame.from_catalog(
    database="asp_project_cleaned", 
    table_name="asp_project_dev", 
    transformation_ctx="AmazonS3_node1733542300994"
)

# Evaluate data quality (this part remains unchanged)
EvaluateDataQuality().process_rows(
    frame=AmazonS3_node1733542300994, 
    ruleset=DEFAULT_DATA_QUALITY_RULESET, 
    publishing_options={
        "dataQualityEvaluationContext": "EvaluateDataQuality_node1733542192862", 
        "enableDataQualityResultsPublishing": True
    }, 
    additional_options={
        "dataQualityResultsPublishing.strategy": "BEST_EFFORT", 
        "observations.scope": "ALL"
    }
)

# Convert the DynamicFrame to a DataFrame for easier manipulation (Repartitioning is easier with DataFrame)
df = AmazonS3_node1733542300994.toDF()

# Repartition the DataFrame to 1 partition to ensure only 1 output file
df_single_partition = df.coalesce(1)  # Coalesce to 1 partition (this ensures 1 output file)

# Convert back to DynamicFrame
dynamic_frame_single_partition = DynamicFrame.fromDF(df_single_partition, glueContext, "dynamic_frame_single_partition")

# Write the transformed data (consolidated Parquet) to the Analytics S3 bucket
AmazonS3_node1733542344296 = glueContext.write_dynamic_frame.from_options(
    frame=dynamic_frame_single_partition, 
    connection_type="s3", 
    format="parquet", 
    connection_options={"path": "s3://asp-project-analytics/analytical-data/"},
    format_options={"compression": "snappy"},  # Snappy compression
    transformation_ctx="AmazonS3_node1733542344296"
)

job.commit()