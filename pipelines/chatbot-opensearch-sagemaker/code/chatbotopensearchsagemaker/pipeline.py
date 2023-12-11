from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from chatbotopensearchsagemaker.config.ConfigStore import *
from chatbotopensearchsagemaker.udfs.UDFs import *
from prophecy.utils import *
from chatbotopensearchsagemaker.graph import *

def pipeline(spark: SparkSession) -> None:
    df_getQueries_msk = getQueries_msk(spark)
    df_extract_fields = extract_fields(spark, df_getQueries_msk)
    df_formatting_timestamp = formatting_timestamp(spark)
    df_collect_results = collect_results(spark, df_formatting_timestamp)
    df_SageMakerEndpoint_1 = SageMakerEndpoint_1(spark, df_collect_results)
    df_formatting = formatting(spark, df_extract_fields)
    df_Bedrock_1 = Bedrock_1(spark)
    df_Reformat = Reformat(spark, df_Bedrock_1)
    df_OpenSearchLookup_1 = OpenSearchLookup_1(spark, df_Reformat)
    df_explode_matches = explode_matches(spark, df_OpenSearchLookup_1)
    df_content_vectorized = content_vectorized(spark)
    df_prepare_payload = prepare_payload(spark)
    bot_message(spark, df_prepare_payload)
    df_with_original_content = with_original_content(spark, df_explode_matches, df_content_vectorized)
    df_Watermark_1 = Watermark_1(spark, df_with_original_content)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/chatbot-opensearch-sagemaker")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-opensearch-sagemaker", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-opensearch-sagemaker")

    pipeline(spark)
    
    spark.streams.resetTerminated()
    spark.streams.awaitAnyTermination()
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
