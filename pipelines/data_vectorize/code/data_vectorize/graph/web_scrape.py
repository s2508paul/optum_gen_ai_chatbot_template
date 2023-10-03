from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def web_scrape(spark: SparkSession) -> DataFrame:
    return spark.read\
        .format("parquet")\
        .schema(
          StructType([
            StructField("id", StringType(), True), StructField("url", StringType(), True), StructField("content_chunk", StringType(), True)
        ])
        )\
        .load("s3://prophecy-demo-optum/web_scrape/")
