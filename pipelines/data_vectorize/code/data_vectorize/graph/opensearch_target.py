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

    if spark.catalog.tableExists("hive_metastore.default.sumitpOpensearch"):
        in0\
            .withColumn("_row_num", row_number().over(Window.partitionBy().orderBy(col("id"))))\
            .withColumn("_group_num", ceil(col("_row_num") / 20))\
            .withColumn("_id_vector", struct(lit("optum-index-metadata-dbx").alias("_index"), col("id"), col("embedding")))\
            .withColumn("_id_vectors", to_json(col("_id_vector")))\
            .groupBy(col("_group_num"))\
            .agg(collect_list(col("_id_vectors")).alias("id_vectors"))\
            .withColumn("upserted", expr("opensearch_upsert(id_vectors)"))\
            .select(col("*"), col("upserted.*"))\
            .write\
            .format("delta")\
            .insertInto("hive_metastore.default.sumitpOpensearch")
    else:
        in0\
            .withColumn("_row_num", row_number().over(Window.partitionBy().orderBy(col("id"))))\
            .withColumn("_group_num", ceil(col("_row_num") / 20))\
            .withColumn("_id_vector", struct(lit("optum-index-metadata-dbx").alias("_index"), col("id"), col("embedding")))\
            .withColumn("_id_vectors", to_json(col("_id_vector")))\
            .groupBy(col("_group_num"))\
            .agg(collect_list(col("_id_vectors")).alias("id_vectors"))\
            .withColumn("upserted", expr("opensearch_upsert(id_vectors)"))\
            .select(col("*"), col("upserted.*"))\
            .write\
            .format("delta")\
            .mode("overwrite")\
            .saveAsTable("hive_metastore.default.sumitpOpensearch")
