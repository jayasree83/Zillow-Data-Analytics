import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# Initialize the Glue context and Spark context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read the data from the cleansed S3 bucket as a DynamicFrame
cleansed_data = glueContext.create_dynamic_frame.from_options(
    connection_type="s3", 
    connection_options={"paths": ["s3://aws-project-cleansed-dev/zillow/"]},
    format="parquet"
)

# inspect the schema to understand the data (for debugging)
cleansed_data.printSchema()

# Convert the DynamicFrame to a DataFrame for easier column selection (DataFrame has more flexibility)
df = cleansed_data.toDF()

# Select only the columns you need (replace with your required columns)
selected_columns_df = df.select("zpid", "bathrooms", "bedrooms", "livingarea", "yearbuilt", "propertytype", "daysonzillow", "address_streetaddress", "address_zipcode", "address_city", "address_state", "lotsizewithunit_lotsize", "listing_listingstatus", "price_value", "price_pricechange", "price_pricepersquarefoot", "taxassessment_taxassessedvalue", "taxassessment_taxassessmentyear")

unique_df = selected_columns_df.dropDuplicates(["zpid"])

# Convert the DataFrame back to a DynamicFrame
selected_dynamic_frame = DynamicFrame.fromDF(unique_df, glueContext, "selected_data")

# Write the transformed data (consolidated Parquet) to the Analytics S3 bucket
glueContext.write_dynamic_frame.from_options(
    selected_dynamic_frame, 
    connection_type="s3", 
    connection_options={"path": "s3://asp-project-analytics/analytical-data/"},
    format="parquet"
)

