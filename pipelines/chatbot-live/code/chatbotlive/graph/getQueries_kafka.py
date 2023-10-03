from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def getQueries_kafka(spark: SparkSession) -> DataFrame:
    from pyspark.dbutils import DBUtils
    consumer_options = {
        "kafka.sasl.jaas.config": (
          f"kafkashaded.org.apache.kafka.common.security.scram.ScramLoginModule"
          + f' required username="{DBUtils(spark).secrets.get(scope = "confluent", key = "usr")}" password="{DBUtils(spark).secrets.get(scope = "confluent", key = "pass_key")}";'
        ),
        "kafka.sasl.mechanism": "PLAIN",
        "kafka.security.protocol": "SASL_SSL",
        "kafka.bootstrap.servers": "pkc-p11xm.us-east-1.aws.confluent.cloud:9092",
        "kafka.session.timeout.ms": "6000",
        "group.id": "",
    }
    consumer_options["subscribe"] = "prophecy"
    consumer_options["startingOffsets"] = "latest"
    consumer_options["includeHeaders"] = False

    return (spark.readStream\
        .format("kafka")\
        .options(**consumer_options)\
        .load()\
        .withColumn("value", col("value").cast("string"))\
        .withColumn("key", col("key").cast("string")))\
        .withColumn("value", from_json(col("value"), schema_of_json("{\n\t\"msg\" : \"hi\"\n}")))
