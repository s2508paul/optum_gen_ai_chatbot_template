from prophecy.config import ConfigBase


class SubgraphConfig(ConfigBase):

    def __init__(
            self,
            prophecy_spark=None,
            access_key: str="opensearch_serverless:access_key",
            secret_key: str="opensearch_serverless:secret",
            **kwargs
    ):

        if access_key is not None:
            self.access_key = self.get_dbutils(prophecy_spark).secrets.get(*access_key.split(":"))

        if secret_key is not None:
            self.secret_key = self.get_dbutils(prophecy_spark).secrets.get(*secret_key.split(":"))

        pass

    def update(self, updated_config):
        self.access_key = updated_config.access_key
        self.secret_key = updated_config.secret_key
        pass

Config = SubgraphConfig()
