from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def content_vectorized(spark: SparkSession) -> DataFrame:
    return spark.read.table("`spark_catalog`.`default`.`text_vectorized`")
