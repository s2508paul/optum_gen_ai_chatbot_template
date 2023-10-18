from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from optumpdfdatavectorize.config.ConfigStore import *
from optumpdfdatavectorize.udfs.UDFs import *

def read_pdf(spark: SparkSession) -> DataFrame:
    return spark.read\
        .format("binaryFile")\
        .schema(
          StructType([
            StructField("path", StringType(), True), StructField("modificationTime", TimestampType(), True), StructField("length", LongType(), True), StructField("content", BinaryType(), True)
        ])
        )\
        .load("dbfs:/FileStore/data_engg/optum/pdf/")
