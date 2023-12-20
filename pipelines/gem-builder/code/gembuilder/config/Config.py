from gembuilder.graph.Bedrock_Subgraph.config.Config import SubgraphConfig as Bedrock_Subgraph_Config
from prophecy.config import ConfigBase


class Config(ConfigBase):

    def __init__(self, access_key: str=None, secret_key: str=None, Bedrock_Subgraph: dict=None, **kwargs):
        self.spark = None
        self.update(access_key, secret_key, Bedrock_Subgraph)

    def update(
            self,
            access_key: str="opensearch_serverless:access_key",
            secret_key: str="opensearch_serverless:secret",
            Bedrock_Subgraph: dict={},
            **kwargs
    ):
        prophecy_spark = self.spark

        if access_key is not None:
            self.access_key = self.get_dbutils(prophecy_spark).secrets.get(*access_key.split(":"))

        if secret_key is not None:
            self.secret_key = self.get_dbutils(prophecy_spark).secrets.get(*secret_key.split(":"))

        self.Bedrock_Subgraph = self.get_config_object(
            prophecy_spark, 
            Bedrock_Subgraph_Config(prophecy_spark = prophecy_spark), 
            Bedrock_Subgraph, 
            Bedrock_Subgraph_Config
        )
        pass
