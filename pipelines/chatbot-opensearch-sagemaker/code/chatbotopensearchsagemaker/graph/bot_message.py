from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *

def bot_message(spark: SparkSession, in0: DataFrame):
    in0.writeStream\
        .format("delta")\
        .option("checkpointLocation", "dbfs:/data_engg/datasets/bot_amswers101")\
        .queryName("StreamingTarget_1_7vfVj539dWoKmuy_ZnuRz$$u8khMSATMH7m6BhoqRnpd")\
        .outputMode("append")\
        .toTable("hive_metastore.default.bot_answers101")
