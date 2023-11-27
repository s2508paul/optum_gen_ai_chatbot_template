from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import row_number, ceil, collect_list
from pyspark.sql.types import StructType, ArrayType, StringType, StructField, IntegerType, FloatType

from prophecy.cb.server.base import WorkflowContext
from prophecy.cb.server.base.ComponentBuilderBase import ComponentCode, Diagnostic, SeverityLevelEnum
from prophecy.cb.server.base.DatasetBuilderBase import DatasetSpec, DatasetProperties, Component
from prophecy.cb.ui.uispec import *

from prophecy.cb.server.base.datatypes import SString

class Transformation(ABC):
    pass


class OpenSearchFormat(DatasetSpec):
    name: str = "OpenSearch"
    datasetType: str = "Warehouse"
    mode: str = "batch"
    

    def optimizeCode(self) -> bool:
        return True

    @dataclass(frozen=True)
    class MetadataColumn(Transformation):
        columnName: SString = SString("")
        columnMapping: SString = SString("")

    @dataclass(frozen=True)
    class EmbeddingColumn(Transformation):
        columnName: SString = SString("")
        columnMapping: SString = SString("")


    @dataclass(frozen=True)
    class OpenSearchProperties(DatasetProperties):
        
        transformations: List[Transformation] = field(default_factory=list)

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
        
        vector_id_prop: Optional[str] = ""
        vector_embdd_prop: Optional[str] = ""

        status: bool = True
        status_is_uc: Optional[bool] = None
        status_catalog: Optional[str] = None
        status_database: str = ""
        status_table: str = ""

        path: str = ""
        uri: Optional[str] = None

    def onButtonClick(self, state: Component[OpenSearchProperties]):
        _transformations = state.properties.transformations
        _transformations.append(self.MetadataColumn())
        return state.bindProperties(replace(state.properties, transformations=_transformations))

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

            aws_region = TextBox("Aws Region") \
                .bindPlaceholder("us-east-1") \
                .bindProperty("region")

            aws_service = TextBox("Aws Service") \
                .bindPlaceholder("aoss/es") \
                .bindProperty("service")

            index_selector = TextBox("Index Name") \
                .bindPlaceholder("index name") \
                .bindProperty("index_name")

            location_selector = ColumnsLayout(gap="1rem") \
                .addElement(host) \
                .addElement(index_selector) \
                .addElement(aws_region)\
                .addElement(aws_service)

            location_section = StackLayout() \
                .addElement(TitleElement("Location")) \
                .addElement(location_selector)


            
            
            ##additional metadata 
            selectBox = (SelectBox("Operation")
                     .addOption("Add Metadata Column", "MetadataColumn")
                     .addOption("Add Embedding Column", "EmbeddingColumn")
                     .bindProperty("record.kind"))
            
            add_metadata = Condition() \
            .ifEqual(PropExpr("record.kind"), StringExpr("MetadataColumn")) \
            .then(
                ColumnsLayout(("1rem"), alignY=("end"))
                    .addColumn(
                        ColumnsLayout(("1rem"))
                            .addColumn(selectBox, "0.3fr")
                            .addColumn(
                                TextBox("Metadata Column Name") \
                                .bindPlaceholder("index column name") \
                                .bindProperty("record.MetadataColumn.columnName")
                            )
                            .addColumn(
                                SchemaColumnsDropdown("Metadata Column Mapping") \
                                .bindSchema("component.ports.inputs[0].schema") \
                                .bindProperty("record.MetadataColumn.columnMapping") 
                            ),
                            "1fr",
                            overflow=("visible")
                    )
                    .addColumn(ListItemDelete("delete"), width="content")
            )

            add_embedding = Condition() \
            .ifEqual(PropExpr("record.kind"), StringExpr("EmbeddingColumn")) \
            .then(
                ColumnsLayout(("1rem"), alignY=("end"))
                    .addColumn(
                        ColumnsLayout(("1rem"))
                            .addColumn(selectBox, "0.3fr")
                            .addColumn(
                                TextBox("Embedding Column Name") \
                                .bindPlaceholder("index column name") \
                                .bindProperty("record.EmbeddingColumn.columnName")
                            )
                            .addColumn(
                                SchemaColumnsDropdown("Embedding Column Mapping") \
                                .bindSchema("component.ports.inputs[0].schema") \
                                .bindProperty("record.EmbeddingColumn.columnMapping")
                            ),
                            "1fr",
                            overflow=("visible")
                    )
                    .addColumn(ListItemDelete("delete"), width="content")
            )

            

            transformations = StackLayout(gap=("1rem"), height=("100bh")) \
            .addElement(TitleElement("Transformations")) \
            .addElement(
                    OrderedList("Transformations")
                        .bindProperty("transformations")
                        .setEmptyContainerText("Add Transformations")
                        .addElement(
                            add_embedding
                        )
                        .addElement(
                            add_metadata
                        )
                        
                ) \
            .addElement(SimpleButtonLayout("Add Transformation", self.onButtonClick))

            


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
                .addElement(transformations) \
                .addElement(status)

            location.padding = "1rem"
            location.gap = "3rem"

            # -------------------
            # PROPERTIES SECTION
            # -------------------


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
            
            select_expr_lst=[]
            for transformation in self.props.transformations:
                select_expr_lst.append(col(transformation.columnMapping.value).alias(f"{transformation.columnName.value}"))
            
            df1 = in0.select(*select_expr_lst) \
                .withColumn('_index',lit(self.props.index_name))

            df_upserted = df1 \
                .withColumn('jsn_data',to_json(struct(df1.columns))) \
                .withColumn('upserted',expr("opensearch_upsert(jsn_data)"))        
                
                

            if self.props.status:
                status_table = f"{self.props.status_catalog}.{self.props.status_database}.{self.props.status_table}" if self.props.status_is_uc else f"{self.props.status_database}.{self.props.status_table}"
                if spark.catalog.tableExists(status_table):
                    df_upserted.write.format("delta").insertInto(status_table)
                else:
                    df_upserted.write.format("delta").mode("overwrite").saveAsTable(status_table)
            else:
                df_upserted.count()