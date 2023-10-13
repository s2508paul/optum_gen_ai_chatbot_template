from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def docx_binaries(spark: SparkSession) -> DataFrame:
    return spark.read.format("binaryFile").load("dbfs:/FileStore/data_engg/optum/docx/")
