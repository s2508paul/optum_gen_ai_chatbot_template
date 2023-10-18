from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from optumpdfdatavectorize.config.ConfigStore import *
from optumpdfdatavectorize.udfs.UDFs import *

def explode(spark: SparkSession, in0: DataFrame) -> DataFrame:
    return in0.select(col("path"), concat_ws(", ", col("result_content.text")).alias("text"))
