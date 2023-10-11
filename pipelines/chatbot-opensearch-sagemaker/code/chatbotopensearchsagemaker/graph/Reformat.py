from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def Reformat(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(
        col("text"), 
        col("ts"), 
        col("create_time"), 
        col("bedrock_embedding").alias("optum-embeddings"), 
        col("bedrock_error")
    )
