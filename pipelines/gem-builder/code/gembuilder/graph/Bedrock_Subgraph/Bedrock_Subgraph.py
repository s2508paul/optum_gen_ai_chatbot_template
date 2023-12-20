from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from . import *
from .config import *

def Bedrock_Subgraph(spark: SparkSession, subgraph_config: SubgraphConfig, in0: DataFrame) -> DataFrame:
    Config.update(subgraph_config)
    df_Bedrock_script_2_2 = Bedrock_script_2_2(spark, in0)
    subgraph_config.update(Config)

    return df_Bedrock_script_2_2
