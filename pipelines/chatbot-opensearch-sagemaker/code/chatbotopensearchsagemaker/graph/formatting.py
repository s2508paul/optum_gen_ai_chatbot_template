from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def formatting(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(col("text"), col("ts"), from_unixtime(col("ts")).cast(TimestampType()).alias("create_time"))
