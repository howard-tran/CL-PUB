import sys

sys.path.append("../../..")

from pprint import pprint
import numpy as np
import pandas as pd
from prototype.crawl_init_data.increase_id import cal_next_id

# each JSON is small, there's no need in iterative processing
import json
import sys
import os
import xml
import time

import pyspark
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType, FloatType

import copy
import uuid

os.environ["JAVA_HOME"] = "/opt/corretto-8"
os.environ["HADOOP_CONF_DIR"] = "/recsys/prototype/spark_submit/hdfs_cfg"

JAVA_LIB = "/opt/corretto-8/lib"

spark = SparkSession.builder \
    .config("spark.app.name", "Recsys") \
    .config("spark.master", "local[*]") \
    .config("spark.submit.deployMode", "client") \
    .config("spark.yarn.appMasterEnv.SPARK_HOME", "/opt/spark") \
    .config("spark.yarn.appMasterEnv.PYSPARK_PYTHON", "/virtual/python/bin/python") \
    .config("spark.yarn.jars", "hdfs://128.0.5.3:9000/lib/java/spark/jars/*.jar") \
    .config("spark.sql.legacy.allowNonEmptyLocationInCTAS", "true") \
    .getOrCreate()

paper_schema = StructType([       
    StructField('_id', StringType(), False),
    StructField('_status', IntegerType(), False),
    StructField('_timestamp', LongType(), False),
    StructField('id', StringType(), False),
    StructField('title', StringType(), False),
    StructField('year', FloatType(), False),
])

merge_df = spark.read.schema(paper_schema) \
    .parquet(
        "/data/recsys/arnet/tables/bibtex/production/part-0",
        "/data/recsys/arnet/tables/bibtex/production/part-1",
        "/data/recsys/arnet/tables/bibtex/production/part-10",
        "/data/recsys/arnet/tables/bibtex/production/part-11",
        "/data/recsys/arnet/tables/bibtex/production/part-12",
        "/data/recsys/arnet/tables/bibtex/production/part-13",
        "/data/recsys/arnet/tables/bibtex/production/part-14",
        "/data/recsys/arnet/tables/bibtex/production/part-15",
        "/data/recsys/arnet/tables/bibtex/production/part-16",
        "/data/recsys/arnet/tables/bibtex/production/part-17",
        "/data/recsys/arnet/tables/bibtex/production/part-18",
        "/data/recsys/arnet/tables/bibtex/production/part-19",
        "/data/recsys/arnet/tables/bibtex/production/part-2",
        "/data/recsys/arnet/tables/bibtex/production/part-20",
        "/data/recsys/arnet/tables/bibtex/production/part-21",
        "/data/recsys/arnet/tables/bibtex/production/part-3",
        "/data/recsys/arnet/tables/bibtex/production/part-4",
        "/data/recsys/arnet/tables/bibtex/production/part-5",
        "/data/recsys/arnet/tables/bibtex/production/part-6",
        "/data/recsys/arnet/tables/bibtex/production/part-7",
        "/data/recsys/arnet/tables/bibtex/production/part-8",
        "/data/recsys/arnet/tables/bibtex/production/part-9"
    )

merge_df.createOrReplaceTempView("bibtex_merge")

new_df = spark.sql("""
    select bm._id, bm._status, bm._timestamp, bm.id, bm.title, bm.year
    from bibtex_merge as bm, 
        (select first_value(bm._id) as _id
            from bibtex_merge as bm
            group by bm.id) as bu
    where bu._id = bm._id
""")

new_df.write.mode("overwrite") \
    .format("parquet").save(f"/data/recsys/arnet/tables/bibtex/production/merge-0")