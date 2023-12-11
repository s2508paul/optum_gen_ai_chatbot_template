from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def flatten_docx(spark: SparkSession, in0: DataFrame) -> DataFrame:
    flt_col = in0.columns
    selectCols = [col("doc_id") if "doc_id" in flt_col else col("doc_id"),                   col("path") if "path" in flt_col else col("path"),                   col("result_chunks") if "result_chunks" in flt_col else col("result_chunks")]

    return in0.select(*selectCols)
