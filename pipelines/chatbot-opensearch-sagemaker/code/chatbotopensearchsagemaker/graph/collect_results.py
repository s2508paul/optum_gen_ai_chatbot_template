from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def collect_results(spark: SparkSession, in0: DataFrame) -> DataFrame:
    df1 = in0.groupBy(window(col("create_time"), "1 second").alias("create_time"), col("ts"))

    return df1.agg(
        array_join(collect_list(col("content_chunk")), "; ").alias("content_chunk"), 
        first(col("text")).alias("input")
    )
