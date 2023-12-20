from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def getQueries_msk(spark: SparkSession) -> DataFrame:
    from pyspark.dbutils import DBUtils
    consumer_options = {
        "kafka.sasl.jaas.config": (
          f"kafkashaded.org.apache.kafka.common.security.scram.ScramLoginModule"
          + f' required username="{DBUtils(spark).secrets.get(scope = "msk", key = "usr")}" password="{DBUtils(spark).secrets.get(scope = "msk", key = "pass_key")}";'
        ),
        "kafka.sasl.mechanism": "SCRAM-SHA-512",
        "kafka.security.protocol": "SASL_SSL",
        "kafka.bootstrap.servers": "b-1.testvpc.zo3f1z.c4.kafka.eu-west-1.amazonaws.com:9096,b-2.testvpc.zo3f1z.c4.kafka.eu-west-1.amazonaws.com:9096",
        "kafka.session.timeout.ms": "6000",
        "group.id": "",
    }
    consumer_options["subscribe"] = "prophecy-gen-ai"
    consumer_options["startingOffsets"] = "earliest"
    consumer_options["includeHeaders"] = False

    return (spark.readStream\
        .format("kafka")\
        .options(**consumer_options)\
        .load()\
        .withColumn("value", col("value").cast("string"))\
        .withColumn("key", col("key").cast("string")))\
        .withColumn("value", from_json(col("value"), schema_of_json("""{
\t\"msg\" : \"hi\"
}""")))
