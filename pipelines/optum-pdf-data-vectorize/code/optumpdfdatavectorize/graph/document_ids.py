from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from optumpdfdatavectorize.config.ConfigStore import *
from optumpdfdatavectorize.udfs.UDFs import *

def document_ids(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(concat(lit("doc-"), monotonically_increasing_id()).alias("doc_id"), col("path"), col("text"))
