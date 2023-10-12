from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def flatten_chunks(spark: SparkSession, in0: DataFrame) -> DataFrame:
    flt_col = in0.withColumn("result_chunks", explode_outer("result_chunks")).columns
    selectCols = [col("path") if "path" in flt_col else col("path"),                   col("result_chunks") if "result_chunks" in flt_col else col("result_chunks")]

    return in0.withColumn("result_chunks", explode_outer("result_chunks")).select(*selectCols)
