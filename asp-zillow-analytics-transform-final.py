import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

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

# Script generated for node Amazon S3
AmazonS3_node1733625160576 = glueContext.create_dynamic_frame.from_options(format_options={}, connection_type="s3", format="parquet", connection_options={"paths": ["s3://aws-project-cleansed-dev"], "recurse": True}, transformation_ctx="AmazonS3_node1733625160576")

# Script generated for node Change Schema
ChangeSchema_node1733625584805 = ApplyMapping.apply(frame=AmazonS3_node1733625160576, mappings=[("zpid", "bigint", "zpid", "string"), ("country", "string", "country", "string"), ("listingdatetimeonzillow", "bigint", "listingdatetimeonzillow", "timestamp"), ("bathrooms", "double", "bathrooms", "float"), ("bedrooms", "double", "bedrooms", "float"), ("livingarea", "bigint", "livingarea", "long"), ("yearbuilt", "bigint", "yearbuilt", "int"), ("propertytype", "string", "propertytype", "string"), ("daysonzillow", "bigint", "daysonzillow", "long"), ("ssid", "bigint", "ssid", "long"), ("location_latitude", "double", "location_latitude", "double"), ("location_longitude", "double", "location_longitude", "double"), ("address_streetaddress", "string", "address_streetaddress", "string"), ("address_zipcode", "string", "address_zipcode", "string"), ("address_city", "string", "address_city", "string"), ("address_state", "string", "address_state", "string"), ("listing_listingstatus", "string", "listing_listingstatus", "string"), ("listing_listingsubtype_isfsba", "boolean", "listing_listingsubtype_isfsba", "boolean"), ("price_value", "bigint", "price_value", "long"), ("price_pricepersquarefoot", "double", "price_pricepersquarefoot", "float"), ("hdpview_price", "bigint", "hdpview_price", "long"), ("propertydisplayrules_listingcategory", "string", "propertydisplayrules_listingcategory", "string"), ("price_changeddate", "double", "price_changeddate", "date"), ("price_pricechange", "double", "price_pricechange", "double"), ("propertydisplayrules_builder_name", "string", "propertydisplayrules_builder_name", "string"), ("estimates_rentzestimate", "double", "estimates_rentzestimate", "float"), ("estimates_zestimate", "double", "estimates_zestimate", "double"), ("address_buildingid", "double", "address_buildingid", "double"), ("region_groupname", "string", "region_groupname", "string")], transformation_ctx="ChangeSchema_node1733625584805")

# Script generated for node Amazon S3
EvaluateDataQuality().process_rows(frame=ChangeSchema_node1733625584805, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1733625152081", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
AmazonS3_node1733626584085 = glueContext.getSink(path="s3://asp-project-analytics", connection_type="s3", updateBehavior="LOG", partitionKeys=["address_state", "propertytype"], enableUpdateCatalog=True, transformation_ctx="AmazonS3_node1733626584085")
AmazonS3_node1733626584085.setCatalogInfo(catalogDatabase="asp_zillow_analytics_db",catalogTableName="final_analytics")
AmazonS3_node1733626584085.setFormat("glueparquet", compression="snappy")
AmazonS3_node1733626584085.writeFrame(ChangeSchema_node1733625584805)
job.commit()