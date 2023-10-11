from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def Reformat_1(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(
        col("text"), 
        col("ts"), 
        col("create_time"), 
        col("openai_embedding").alias("optum-embeddings"), 
        col("openai_error")
    )
