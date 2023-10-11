from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *
from prophecy.utils import *
from data_vectorize.graph import *

def pipeline(spark: SparkSession) -> None:
    df_web_scrape = web_scrape(spark)
    df_vectorize = vectorize(spark, df_web_scrape)
    df_vector_read_catalog = vector_read_catalog(spark)
    df_clean = clean(spark, df_vectorize)
    opensearch_target(spark, df_vector_read_catalog)
    df_rename = rename(spark, df_clean)
    write_vector_data(spark, df_rename)
    vector_db(spark, df_vector_read_catalog)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/data_vectorize")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/data_vectorize", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/data_vectorize")

    pipeline(spark)
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
