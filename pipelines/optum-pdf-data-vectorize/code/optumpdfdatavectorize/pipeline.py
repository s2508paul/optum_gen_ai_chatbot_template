from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from prophecy.utils import *
from optumpdfdatavectorize.config.ConfigStore import *
from optumpdfdatavectorize.udfs.UDFs import *
from prophecy.utils import *
from optumpdfdatavectorize.graph import *

def pipeline(spark: SparkSession) -> None:
    df_read_pdf = read_pdf(spark)
    df_parse_pdf = parse_pdf(spark, df_read_pdf)
    df_explode = explode(spark, df_parse_pdf)
    df_document_ids = document_ids(spark, df_explode)
    df_chunkify = chunkify(spark, df_document_ids)
    df_flatten_chunks = flatten_chunks(spark, df_chunkify)
    df_get_ids = get_ids(spark, df_flatten_chunks)
    df_bedrock_embeddings = bedrock_embeddings(spark, df_get_ids)
    df_remove_nulls = remove_nulls(spark, df_bedrock_embeddings)
    df_rename = rename(spark, df_remove_nulls)

def main():
    spark = SparkSession.builder\
                .config("spark.default.parallelism", "4")\
                .config("spark.sql.legacy.allowUntypedScalaUDF", "true")\
                .enableHiveSupport()\
                .appName("Prophecy Pipeline")\
                .getOrCreate()\
                .newSession()
    Utils.initializeFromArgs(spark, parse_args())
    spark.conf.set("prophecy.metadata.pipeline.uri", "pipelines/optum-pdf-data-vectorize")
    registerUDFs(spark)

    try:
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/optum-pdf-data-vectorize", config = Config)
    except :
        
        MetricsCollector.start(spark = spark, pipelineId = "pipelines/optum-pdf-data-vectorize")

    pipeline(spark)
    MetricsCollector.end(spark)

if __name__ == "__main__":
    main()
