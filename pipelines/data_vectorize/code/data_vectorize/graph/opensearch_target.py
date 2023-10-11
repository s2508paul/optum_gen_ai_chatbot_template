from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *

def opensearch_target(spark: SparkSession, in0: DataFrame):
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

    if spark.catalog.tableExists("hive_metastore.default.opensearch_load_status1"):
        in0.withColumn(
            'upserted',
            expr("opensearch_upsert(\"optum-gen-ai-index-insert\",\"embedd\",embedd, \"embedd\", id)")
        )\
            .write\
            .format("delta")\
            .insertInto("hive_metastore.default.opensearch_load_status1")
    else:
        in0.withColumn(
            'upserted',
            expr("opensearch_upsert(\"optum-gen-ai-index-insert\",\"embedd\",embedd, \"embedd\", id)")
        )\
            .write\
            .format("delta")\
            .mode("overwrite")\
            .saveAsTable("hive_metastore.default.opensearch_load_status1")
