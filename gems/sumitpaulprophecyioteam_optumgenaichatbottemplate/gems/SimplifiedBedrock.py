from prophecy.cb.server.base.ComponentBuilderBase import *
from pyspark.sql import *
from pyspark.sql.functions import *

from prophecy.cb.server.base import WorkflowContext
from prophecy.cb.server.base.datatypes import SInt, SString
from prophecy.cb.ui.uispec import *


class SimplifiedBedrock(ComponentSpec):
    name: str = "SimplifiedBedrock"
    category: str = "Machine Learning"

    def optimizeCode(self) -> bool:
        return True

    @dataclass(frozen=True)
    class SimplifiedBedrockProperties(ComponentProperties):
        credential_db_scope: Optional[str] = "aws"
        credential_db_key: Optional[str] = "key"
        credential_db_secret: Optional[str] = "secret"        
        operation: str = "embed_texts"
        embed_text_column_name: Optional[str] = None
        aws_region: Optional[str] = "us-east-1"

    def dialog(self) -> Dialog:
        
        def iff(property_name: str, value, then: Atom) -> Condition: 
            value_expr = BooleanExpr(value) if isinstance(value, bool) else StringExpr(str(value))
            return Condition().ifEqual(PropExpr(f"component.properties.{property_name}"), value_expr).then(then)
            
        credential_db = ColumnsLayout(gap="1rem") \
            .addElement(TextBox("Databricks Scope").bindProperty("credential_db_scope")) \
            .addElement(TextBox("Databricks Secret Key Name").bindProperty("credential_db_key")) \
            .addElement(TextBox("Databricks Secret Value Name").bindProperty("credential_db_secret"))
        
        credential = StackLayout() \
            .addElement(TitleElement("Credential")) \
            .addElement(credential_db)
        
        operation_selector = SelectBox("Operation type") \
            .addOption("Compute text embeddings", "embed_texts") \
            .bindProperty("operation")

        # Text embedding properties 
        embed_text_column_selector = SchemaColumnsDropdown("Text column") \
            .bindSchema("component.ports.inputs[0].schema") \
            .bindProperty("embed_text_column_name") \
            .showErrorsFor("embed_text_column_name")
        
        operation_container = StackLayout(gap="1rem") \
            .addElement(TitleElement("Operation")) \
            .addElement(operation_selector) \
            .addElement(iff("operation", "embed_texts", embed_text_column_selector))


        # Model container
        aws_region = SelectBox("AWS Region") \
            .addOption("us-east-1 - US East (N. Virginia)", "us-east-1") \
            .addOption("us-west-2 - US West (Oregon)", "us-west-2") \
            .addOption("ap-southeast-1 - Asia Pacific (Singapore)", "ap-southeast-1") \
            .addOption("ap-northeast-1 - Asia Pacific (Tokyo)", "ap-northeast-1") \
            .bindProperty("aws_region")

        model_container = StackLayout(gap="1rem") \
            .addElement(TitleElement("Model Properties")) \
            .addElement(aws_region)

        # Main container
        main_container = StackLayout(padding="1rem", gap="2rem") \
            .addElement(credential) \
            .addElement(operation_container) \
            .addElement(model_container)
        main_container.padding = "1rem"
        main_container.gap = "3rem"

        return Dialog("SimplifiedBedrock").addElement(
            ColumnsLayout(gap="1rem", height="100%")
            .addColumn(PortSchemaTabs().importSchema(), "2fr")
            .addColumn(main_container, "5fr")
        )


    def validate(self, context: WorkflowContext, component: Component[SimplifiedBedrockProperties]) -> List[Diagnostic]:
        return []

    def onChange(self, context: WorkflowContext, oldState: Component[SimplifiedBedrockProperties], newState: Component[SimplifiedBedrockProperties]) -> Component[
    SimplifiedBedrockProperties]:
        return newState


    class SimplifiedBedrockCode(ComponentCode):
        def __init__(self, newProps):
            self.props: SimplifiedBedrock.SimplifiedBedrockProperties = newProps

        def apply(self, spark: SparkSession, in0: DataFrame) -> DataFrame:
            import json
            from typing import List
            import boto3            
            from pyspark.sql.types import StructType, StructField, ArrayType, StringType, FloatType
            from pyspark.dbutils import DBUtils

            default_embedding_model = 'amazon.titan-embed-text-v1'

            def embed_texts(texts: List[str], access_key:str, secret_key:str, model: str = default_embedding_model):
    
                bedrock = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name="us-east-1"
                )

                try:
                    embeddings = []
                    for text in texts:
                        body = json.dumps({"inputText": text})
                        content_type = 'application/json'

                        response = bedrock.invoke_model(body=body, modelId=model, accept=content_type, contentType=content_type)
                        embeddings.append(json.loads(response['body'].read().decode('utf-8'))['embedding'])

                    return {'embeddings': embeddings, 'error': None}
                except Exception as error:
                    return {'embeddings': None, 'error': str(error)}


            spark.udf.register('bedrock_embed_texts', embed_texts)
            
            dbutils = DBUtils(spark)
            access_key = dbutils.secrets.get(scope=self.props.credential_db_scope, key=self.props.credential_db_key)
            access_secret = dbutils.secrets.get(scope=self.props.credential_db_scope, key=self.props.credential_db_secret)

            return in0 \
                .withColumn("_texts", array(col(self.props.embed_text_column_name))) \
                .withColumn("_embedded", expr(f"bedrock_embed_texts(_texts,\"{access_key}\",\"{access_secret}\")"))
