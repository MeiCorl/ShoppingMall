# -*- coding: utf8 -*-
from config import cos_config
from qcloud_cos import CosConfig, CosS3Client

config = CosConfig(Region=cos_config["region"], Secret_id=cos_config["secret_id"],
                   Secret_key=cos_config["secret_key"], Token=cos_config["cos_token"])
cos_client = CosS3Client(config)


def calculate_sign(path=None, method="POST", headers=None, params=None):
    if params is None:
        params = {}
    if headers is None:
        headers = {}
    if path is None:
        path = {}
    sign = cos_client.get_auth(Method=method,
                               Bucket=cos_config["bucket"] + "-" + cos_config["app_id"],
                               Key=path,
                               Headers=headers,
                               Params=params)
    return sign
