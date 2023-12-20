from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from gembuilder.config.ConfigStore import *
from gembuilder.udfs.UDFs import *

def Bedrock_script_2(spark: SparkSession, in0: DataFrame) -> DataFrame:
    import json
    from typing import List
    import boto3
    from pyspark.sql import *
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
                response = bedrock.invoke_model(body = body, modelId = model, accept = content_type, contentType = content_type)
                embeddings.append(json.loads(response['body'].read().decode('utf-8'))['embedding'])

            return {'embeddings' : embeddings, 'error' : None}
        except Exception as error:
            return {'embeddings' : None, 'error' : str(error)}

    spark.udf.register('bedrock_embed_texts', embed_texts)
    out0 = in0\
               .withColumn("_texts", array(col("result_chunks")))\
               .withColumn("_embedded", expr(f"bedrock_embed_texts(_texts,\"{Config.access_key}\",\"{Config.secret_key}\")"))\
               .drop(col("_texts"))

    return out0
