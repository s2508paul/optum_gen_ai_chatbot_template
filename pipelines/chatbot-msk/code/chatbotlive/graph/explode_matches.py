from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from prophecy.libs import typed_lit
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *

def explode_matches(spark: SparkSession, in0: DataFrame) -> DataFrame:
    flt_col = in0.withColumn("pinecone_matches", explode_outer("pinecone_matches")).columns
    selectCols = [col("pinecone_matches") if "pinecone_matches" in flt_col else col("pinecone_matches"),                   col("text") if "text" in flt_col else col("text"),                   col("ts") if "ts" in flt_col else col("ts"),                   col("create_time") if "create_time" in flt_col else col("create_time")]

    return in0.withColumn("pinecone_matches", explode_outer("pinecone_matches")).select(*selectCols)
