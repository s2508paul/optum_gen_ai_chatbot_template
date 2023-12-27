from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from . import *
from .config import *

def bedrock_subgraph2(
        spark: SparkSession,
        subgraph_config: SubgraphConfig,
        in0: DataFrame,
        in1: DataFrame
) -> DataFrame:
    Config.update(subgraph_config)
    df_Bedrock_script_1 = Bedrock_script_1(spark, in0, in1)
    df_flatten_chunks_1 = flatten_chunks_1(spark, df_Bedrock_script_1)
    subgraph_config.update(Config)

    return df_flatten_chunks_1
