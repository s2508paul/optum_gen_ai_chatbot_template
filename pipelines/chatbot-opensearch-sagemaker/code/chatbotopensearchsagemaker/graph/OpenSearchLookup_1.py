from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def OpenSearchLookup_1(spark: SparkSession, in0: DataFrame) -> DataFrame:
    from pyspark.sql.functions import expr, array, struct
    from spark_ai.dbs.opensearch import OpensearchDB
    from pyspark.dbutils import DBUtils
    OpensearchDB(
          "",
          "us-west-1",
          DBUtils(spark).secrets.get(scope = "opensearch", key = "token"),
          DBUtils(spark).secrets.get(scope = "opensearch", key = "secrets"),
          "aoss"
        )\
        .register_udfs(spark)

    return in0\
        .withColumn("_vector", col(""))\
        .withColumn("_response", expr("opensearch_query(\"\",\"\", \"\", _vector, 3)"))\
        .withColumn("opensearch_matches", col("_response.matches"))\
        .withColumn("opensearch_error", col("_response.error"))\
        .drop("_vector", "_response")
