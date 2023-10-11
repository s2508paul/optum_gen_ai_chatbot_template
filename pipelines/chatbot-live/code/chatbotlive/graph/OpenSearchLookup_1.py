from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def OpenSearchLookup_1(spark: SparkSession, in0: DataFrame) -> DataFrame:
    from pyspark.sql.functions import expr, array, struct
    from spark_ai.dbs.opensearch import OpensearchDB
    from pyspark.dbutils import DBUtils
    OpensearchDB(
          "vrq94ns7ekrnmygy1lx6.eu-west-1.aoss.amazonaws.com",
          "eu-west-1",
          DBUtils(spark).secrets.get(scope = "opensearch_serverless", key = "access_key"),
          DBUtils(spark).secrets.get(scope = "opensearch_serverless", key = "secret"),
          "aoss"
        )\
        .register_udfs(spark)

    return in0\
        .withColumn("_vector", col("optum-embeddings"))\
        .withColumn("_response", expr("opensearch_query(\"optum-gen-ai-index\", \"optum-embeddings\", _vector, 3)"))\
        .withColumn("opensearch_matches", col("_response.matches"))\
        .withColumn("opensearch_error", col("_response.error"))\
        .drop("_vector", "_response")
