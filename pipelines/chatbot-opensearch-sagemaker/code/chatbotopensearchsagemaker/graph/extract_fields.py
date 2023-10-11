from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def extract_fields(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(col("value.msg").alias("text"), unix_timestamp(col("timestamp")).cast(StringType()).alias("ts"))
