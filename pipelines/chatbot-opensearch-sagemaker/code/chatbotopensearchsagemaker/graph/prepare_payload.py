from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def prepare_payload(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(
        col("create_time.start").alias("create_time"), 
        col("input"), 
        col("sagemaker_answer.choices")[0].alias("answer")
    )
