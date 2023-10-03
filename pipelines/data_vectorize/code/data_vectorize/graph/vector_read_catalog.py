from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def vector_read_catalog(spark: SparkSession) -> DataFrame:
    return spark.read.table("`spark_catalog`.`default`.`content_vectorized`")
