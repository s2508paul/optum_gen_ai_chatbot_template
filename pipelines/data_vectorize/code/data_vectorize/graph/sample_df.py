from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def sample_df(spark: SparkSession) -> DataFrame:
    data = [("A bunch of scientists bring back dinosaurs and mayhem breaks loose. Leo DiCaprio gets lost in a dream within a dream within a dream within a ... A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea.")]
    schema = StructType([StructField("col1", StringType(), True)])
    df = spark.createDataFrame([(value, ) for value in data], schema = schema)

    return df

    return out0
