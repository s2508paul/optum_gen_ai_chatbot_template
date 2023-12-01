from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from optumpdfdatavectorize.config.ConfigStore import *
from optumpdfdatavectorize.udfs.UDFs import *

def bedrock_embeddings(spark: SparkSession, in0: DataFrame) -> DataFrame:
    from spark_ai.llms.bedrock import BedrockLLM
    from pyspark.sql.types import StringType
    from pyspark.dbutils import DBUtils
    (BedrockLLM(
          aws_access_key_id = DBUtils(spark).secrets.get(scope = "opensearch_serverless", key = "access_key"),
          aws_secret_access_key = DBUtils(spark).secrets.get(scope = "opensearch_serverless", key = "secret"),
          region_name = "us-east-1"
        )\
        .register_udfs(spark = spark))

    return in0\
        .withColumn("_texts", array(col("result_chunks")))\
        .withColumn("_embedded", expr("bedrock_embed_texts(_texts)"))\
        .withColumn("bedrock_embedding", expr("_embedded.embeddings[0]"))\
        .withColumn("bedrock_error", col("_embedded.error"))\
        .drop("_texts", "_embedded")
