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
    df_document_ids = document_ids(spark, df_explode)
    df_docx_binaries = docx_binaries(spark)
    df_parse_docx = parse_docx(spark, df_docx_binaries)
    df_explode_docx = explode_docx(spark, df_parse_docx)
    df_document_ids_1 = document_ids_1(spark, df_explode_docx)
    df_chunkify_docx = chunkify_docx(spark, df_document_ids_1)
    df_chunkify = chunkify(spark, df_document_ids)
    df_flatten_chunks = flatten_chunks(spark, df_chunkify)
    df_get_ids = get_ids(spark, df_flatten_chunks)
    df_vector_read_catalog = vector_read_catalog(spark)
    df_Bedrock = Bedrock(spark, df_get_ids)
    df_remove_nulls = remove_nulls(spark, df_Bedrock)
    df_sample_df = sample_df(spark)
    df_test_chunk_overlap = test_chunk_overlap(spark, df_sample_df)
    df_FlattenSchema_1 = FlattenSchema_1(spark, df_test_chunk_overlap)
    df_flatten_docx = flatten_docx(spark, df_chunkify_docx)
    df_rename = rename(spark, df_remove_nulls)
    populate_vector_db(spark, df_rename)

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
