from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from gembuildertest.config.ConfigStore import *
from gembuildertest.udfs.UDFs import *

def SimplifiedBedrock_1(spark: SparkSession, in0: DataFrame) -> DataFrame:
    import json
    from typing import List
    import boto3
    from pyspark.sql.types import StructType, StructField, ArrayType, StringType, FloatType
    from pyspark.dbutils import DBUtils
    default_embedding_model = 'amazon.titan-embed-text-v1'

    def embed_texts(texts: List[str], access_key: str, secret_key: str, model: str=default_embedding_model):
        bedrock = boto3.client(
            'bedrock-runtime',
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            region_name = "us-east-1"
        )

        try:
            embeddings = []

            for text in texts:
                body = json.dumps({"inputText" : text})
                content_type = 'application/json'
                response = bedrock.invoke_model(
                    body = body,
                    modelId = model,
                    accept = content_type,
                    contentType = content_type
                )
                embeddings.append(json.loads(response['body'].read().decode('utf-8'))['embedding'])

            return {'embeddings' : embeddings, 'error' : None}
        except Exception as error:
            return {'embeddings' : None, 'error' : "error"}

    spark.udf.register('bedrock_embed_texts', embed_texts)

    return in0\
        .withColumn("_texts", array(col(None)))\
        .withColumn("_embedded", expr(
        "bedrock_embed_texts(_texts,\"{}\",\"{}\")".format(
          DBUtils(spark).secrets.get(scope = "aws", key = "key"), 
          DBUtils(spark).secrets.get(scope = "aws", key = "secret")
        )
    ))
