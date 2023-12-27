from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from gembuilder.config.ConfigStore import *
from gembuilder.udfs.UDFs import *
from prophecy.utils import *
from gembuilder.graph import *

def pipeline(spark: SparkSession) -> None:
    df_read_pdf = read_pdf(spark)
    df_parse_pdf = parse_pdf(spark, df_read_pdf)
    df_explode = explode(spark, df_parse_pdf)
    df_chunkify = chunkify(spark, df_explode)
    df_Join_1 = Join_1(spark)
    df_flatten_chunks = flatten_chunks(spark, df_chunkify)
    df_get_ids = get_ids(spark, df_flatten_chunks)
    df_Bedrock_Subgraph = Bedrock_Subgraph(spark, Config.Bedrock_Subgraph, df_get_ids)
    df_Bedrock_script = Bedrock_script(spark, df_get_ids)
    df_Bedrock_1 = Bedrock_1(spark)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/gem-builder")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/gem-builder", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/gem-builder")

    pipeline(spark)
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
