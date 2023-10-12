from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def formatting_timestamp(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(
        col("opensearch_matches"), 
        col("text"), 
        col("ts"), 
        date_format(col("create_time"), "yyyy-MM-dd HH:mm:ss").cast(TimestampType()).alias("create_time"), 
        col("id"), 
        col("embedding"), 
        col("content_chunk")
    )
