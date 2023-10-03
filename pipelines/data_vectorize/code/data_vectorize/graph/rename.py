from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def rename(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(col("id"), col("openai_embedding").alias("embedding"), col("url"), col("content_chunk"))
