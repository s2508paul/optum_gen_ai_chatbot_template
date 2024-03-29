from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def text_embeddings(spark: SparkSession, in0: DataFrame) -> DataFrame:
    from spark_ai.llms.bedrock import BedrockLLM
    from pyspark.sql.types import StringType
    from pyspark.dbutils import DBUtils
    (BedrockLLM(
          aws_access_key_id = DBUtils(spark).secrets.get(scope = "aws_main", key = "secret_key"),
          aws_secret_access_key = DBUtils(spark).secrets.get(scope = "aws_main", key = "secret_value"),
          region_name = "us-east-1"
        )\
        .register_udfs(spark = spark))

    return in0\
        .withColumn("_texts", array(col("text")))\
        .withColumn("_embedded", expr("bedrock_embed_texts(_texts)"))\
        .withColumn("bedrock_embedding", expr("_embedded.embeddings[0]"))\
        .withColumn("bedrock_error", col("_embedded.error"))\
        .drop("_texts", "_embedded")
