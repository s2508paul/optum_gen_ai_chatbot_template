from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import row_number, ceil, collect_list
from pyspark.sql.types import StructType, ArrayType, StringType, StructField, IntegerType, FloatType

from prophecy.cb.server.base import WorkflowContext
from prophecy.cb.server.base.ComponentBuilderBase import ComponentCode, Diagnostic, SeverityLevelEnum
from prophecy.cb.server.base.DatasetBuilderBase import DatasetSpec, DatasetProperties, Component
from prophecy.cb.ui.uispec import *


class OpenSearchFormat(DatasetSpec):
    name: str = "OpenSearch"
    datasetType: str = "Warehouse"
    mode: str = "batch"
    

    def optimizeCode(self) -> bool:
        return True

    @dataclass(frozen=True)
    class OpenSearchProperties(DatasetProperties):
        schema: Optional[StructType] = None
        description: Optional[str] = ""

        credential_type: Optional[str] = "databricks"
        credential_db_scope: Optional[str] = "opensearch"
        credential_db_key: Optional[str] = "token"
        credential_db_secrets: Optional[str] = "secrets"

        credential_manual_api_key: Optional[str] = ""
        credential_manual_api_secrets: Optional[str] = ""

        host: Optional[str] = ""
        region: Optional[str] = "us-west-1"
        service: Optional[str] = "aoss"
        index_name: Optional[str] = ""

        vector_id_column_name: Optional[str] = ""
        vector_content_column_name: Optional[str] = ""
        
        status: bool = True
        status_is_uc: Optional[bool] = None
        status_catalog: Optional[str] = None
        status_database: str = ""
        status_table: str = ""

        path: str = ""
        uri: Optional[str] = None

    def sourceDialog(self) -> DatasetDialog:
        return DatasetDialog("OpenSearch")

    def targetDialog(self) -> DatasetDialog:
            def iff(property_name: str, value, then: Atom) -> Condition:
                value_expr = BooleanExpr(value) if isinstance(value, bool) else StringExpr(str(value))
                return Condition().ifEqual(PropExpr(f"component.properties.{property_name}"), value_expr).then(then)

            credential_type = RadioGroup("Credentials") \
                .addOption("Databricks Secrets (recommended)", "databricks") \
                .addOption("Hardcoded", "manual") \
                .bindProperty("credential_type")

            credential_db = ColumnsLayout(gap="1rem") \
                .addElement(TextBox("Databricks Scope").bindProperty("credential_db_scope")) \
                .addElement(TextBox("Databricks Key").bindProperty("credential_db_key")) \
                .addElement(TextBox("Databricks Secrets").bindProperty("credential_db_secrets"))

            credential_manual = ColumnsLayout(gap="1rem") \
                .addElement(TextBox("Key").bindPlaceholder("80******-****-****-****-************").bindProperty("credential_manual_api_key")) \
                .addElement(TextBox("Secrets").bindProperty("credential_manual_api_secrets"))
            

            credential_db_or_manual = Condition() \
                .ifEqual(PropExpr("component.properties.credential_type"), StringExpr("databricks")) \
                .then(credential_db).otherwise(credential_manual)

            credential = StackLayout() \
                .addElement(credential_type) \
                .addElement(credential_db_or_manual)

            # Opensearch host, region & index 
            host = TextBox("Host") \
                .bindPlaceholder("") \
                .bindProperty("host")

            index_selector = TextBox("Index name") \
                .bindProperty("index_name")

            aws_region = TextBox("Aws Region") \
                .bindPlaceholder("us-east-1") \
                .bindProperty("region")

            aws_service = TextBox("Service") \
                .bindPlaceholder("aoss/es") \
                .bindProperty("service")

            location_selector = ColumnsLayout(gap="1rem") \
                .addElement(host) \
                .addElement(index_selector)\
                .addElement(aws_region)\
                .addElement(aws_service)

            location_section = StackLayout() \
                .addElement(TitleElement("Location")) \
                .addElement(location_selector)

            # Status writing
            status_selector = CatalogTableDB("") \
                .bindProperty("status_database") \
                .bindTableProperty("status_table") \
                .bindCatalogProperty("status_catalog") \
                .bindIsCatalogEnabledProperty("status_is_uc")

            status_description = "When this option is enabled, the Target component is going to write the " \
                                "status of Opensearch writes, to a Delta table for further querying."
            status = StackLayout() \
                .addElement(TitleElement("Status writing")) \
                .addElement(NativeText(status_description)) \
                .addElement(Checkbox("Enable status write (recommended)").bindProperty("status")) \
                .addElement(iff("status", True, status_selector))

            location = StackLayout() \
                .addElement(credential) \
                .addElement(location_section) \
                .addElement(status)

            location.padding = "1rem"
            location.gap = "3rem"

            # -------------------
            # PROPERTIES SECTION
            # -------------------

            id_column_selector = SchemaColumnsDropdown("Vector id column (expected type: str)") \
                .bindSchema("component.ports.inputs[0].schema") \
                .bindProperty("vector_id_column_name") \
                .showErrorsFor("vector_id_column_name")

            content_column_selector = SchemaColumnsDropdown("Vector content column (expected type: array<float>)") \
                .bindSchema("component.ports.inputs[0].schema") \
                .bindProperty("vector_content_column_name") \
                .showErrorsFor("vector_content_column_name")

            # columns_selector = ColumnsLayout(gap="1rem", height="80px") \
            #     .addElement(id_column_selector) \
            #     .addElement(content_column_selector)

            return DatasetDialog("OpenSearch") \
                .addSection("LOCATION", location) \
                .addSection(
                "PROPERTIES",
                ColumnsLayout(gap=("1rem"), height=("100%"))
                .addColumn(
                    ScrollBox().addElement(
                        StackLayout(height=("100%"))
                        .addElement(
                            StackItem(grow=(1))
                            .addElement(
                                FieldPicker(height=("100%"))
                                .addField(
                                    TextArea("Description", 2, placeholder="Dataset description..."),
                                    "description",
                                    True
                                )
                                .addField(id_column_selector, "vector_id_column_name", True)
                                .addField(content_column_selector, "vector_content_column_name", True)
                            )
                        )
                    ),
                    "auto"
                )
                .addColumn(SchemaTable("").withoutInferSchema().bindProperty("schema"), "5fr")
            ) \
                .addSection(
                "PREVIEW",
                PreviewTable("").bindProperty("schema")
            )

    def validate(self, context: WorkflowContext, component: Component) -> list:
        return super(OpenSearchFormat, self).validate(context, component)

    def onChange(self, context: WorkflowContext, oldState: Component, newState: Component) -> Component:
        return newState

    class OpenSearchFormatCode(ComponentCode):
        def __init__(self, props):
            self.props: OpenSearchFormat.OpenSearchProperties = props

        def sourceApply(self, spark: SparkSession) -> DataFrame:
            return spark.range(0)

        def targetApply(self, spark: SparkSession, in0: DataFrame):
            from pyspark.sql.functions import expr, array, struct
            from spark_ai.dbs.opensearch import OpensearchDB

            if self.props.credential_type == "databricks":
                from pyspark.dbutils import DBUtils
                dbutils = DBUtils(spark)
                usr = dbutils.secrets.get(scope=self.props.credential_db_scope, key=self.props.credential_db_key)
                secrets = dbutils.secrets.get(scope=self.props.credential_db_scope, key=self.props.credential_db_secrets)
            else:
                usr = self.props.credential_manual_api_key
                secrets = self.props.credential_manual_api_secrets

            host = self.props.host
            region = self.props.region
            service = self.props.service

            OpensearchDB(host,region,usr,secrets,service).register_udfs(spark)

            df_upserted = in0 \
                .withColumn("_row_num",row_number().over(Window.partitionBy().orderBy(col(self.props.vector_id_column_name)))) \
                .withColumn("_group_num", ceil(col("_row_num") / 20)) \
                .withColumn("_id_vector", struct(lit(self.props.index_name).alias("_index"),col(self.props.vector_id_column_name).alias(self.props.vector_id_column_name),col(self.props.vector_content_column_name).alias(self.props.vector_content_column_name))) \
                .withColumn("_id_vectors",to_json(col("_id_vector")))\
                .groupBy(col("_group_num")) \
                .agg(collect_list(col("_id_vectors")).alias("id_vectors")) \
                .withColumn("upserted", expr("opensearch_upsert(id_vectors)")) \
                .select(col("*"), col("upserted.*"))
            
            if self.props.status:
                status_table = f"{self.props.status_catalog}.{self.props.status_database}.{self.props.status_table}" if self.props.status_is_uc else f"{self.props.status_database}.{self.props.status_table}"
                if spark.catalog.tableExists(status_table):
                    df_upserted.write.format("delta").insertInto(status_table)
                else:
                    df_upserted.write.format("delta").mode("overwrite").saveAsTable(status_table)
            else:
                df_upserted.count()




                
            



