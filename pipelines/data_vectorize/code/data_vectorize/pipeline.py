from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from data_vectorize.config.ConfigStore import *
from data_vectorize.udfs.UDFs import *
from prophecy.utils import *
from data_vectorize.graph import *

def pipeline(spark: SparkSession) -> None:
    df_optum_pdf = optum_pdf(spark)
    df_parse_pdf = parse_pdf(spark, df_optum_pdf)
    df_explode = explode(spark, df_parse_pdf)
    df_chunkify = chunkify(spark, df_explode)
    df_flatten_chunks = flatten_chunks(spark, df_chunkify)
    df_get_ids = get_ids(spark, df_flatten_chunks)
    df_bedrock_embeddings = bedrock_embeddings(spark, df_get_ids)
    df_docx_binaries = docx_binaries(spark)
    df_parse_docx = parse_docx(spark, df_docx_binaries)
    df_explode_docx = explode_docx(spark, df_parse_docx)
    df_chunkify_docx = chunkify_docx(spark, df_explode_docx)
    df_vector_read_catalog = vector_read_catalog(spark)
    df_remove_nulls = remove_nulls(spark, df_bedrock_embeddings)
    opensearch_target(spark, df_vector_read_catalog)
    df_flatten_docx = flatten_docx(spark, df_chunkify_docx)
    df_rename = rename(spark, df_remove_nulls)
    write_vector_data(spark, df_rename)

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
