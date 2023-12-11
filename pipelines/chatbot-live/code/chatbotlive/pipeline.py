from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *
from prophecy.utils import *
from chatbotlive.graph import *

def pipeline(spark: SparkSession) -> None:
    df_PineconeLookup_1 = PineconeLookup_1(spark)
    df_explode_matches = explode_matches(spark, df_PineconeLookup_1)
    df_content_vectorized = content_vectorized(spark)
    df_with_original_content = with_original_content(spark, df_explode_matches, df_content_vectorized)
    df_Watermark_1 = Watermark_1(spark, df_with_original_content)
    df_formatting_timestamp = formatting_timestamp(spark, df_Watermark_1)
    df_getQueries_msk = getQueries_msk(spark)
    df_extract_fields = extract_fields(spark, df_getQueries_msk)
    df_formatting = formatting(spark, df_extract_fields)
    df_prepare_payload = prepare_payload(spark)
    bot_message(spark, df_prepare_payload)
    df_collect_results = collect_results(spark, df_formatting_timestamp)
    df_OpenAI_2 = OpenAI_2(spark, df_collect_results)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/chatbot-live")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-live", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-live")

    pipeline(spark)
    
    spark.streams.resetTerminated()
    spark.streams.awaitAnyTermination()
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
