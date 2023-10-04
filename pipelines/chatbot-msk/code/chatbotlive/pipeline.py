from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from chatbotlive.config.ConfigStore import *
from chatbotlive.udfs.UDFs import *
from prophecy.utils import *
from chatbotlive.graph import *

def pipeline(spark: SparkSession) -> None:
    df_getQueries_msk = getQueries_msk(spark)
    df_extract_fields = extract_fields(spark, df_getQueries_msk)
    df_farmatting = farmatting(spark, df_extract_fields)
    df_vectorize_question = vectorize_question(spark, df_farmatting)
    df_vector_lookup = vector_lookup(spark, df_vectorize_question)
    df_explode_matches = explode_matches(spark, df_vector_lookup)
    df_content_vectorized = content_vectorized(spark)
    df_with_original_content = with_original_content(spark, df_explode_matches, df_content_vectorized)
    df_with_watermark = with_watermark(spark, df_with_original_content)
    df_formatting_timestamp = formatting_timestamp(spark, df_with_watermark)
    df_collect_results = collect_results(spark, df_formatting_timestamp)
    df_answer_question = answer_question(spark, df_collect_results)
    df_prepare_payload = prepare_payload(spark, df_answer_question)
    bot_message(spark)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/chatbot-msk")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-msk", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/chatbot-msk")

    pipeline(spark)
    
    spark.streams.resetTerminated()
    spark.streams.awaitAnyTermination()
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
