# Project-Group-09
This is Group 9. 
Our problem statement is to implement a big data problem on any target platform.

Contributors: Sahana Srinivasan and Swathi Shree


## BIG DATA AND PROCESSING WITH MAPREDUCE ##

Amazon Customer Sentimental Analysis using Spark and Python on Google Colab


REQUIREMENTS: Spark 3.1.1, Hadoop 2.7

TARGET PLATFORM: Cloud Systems, implemented using Google Colab 

LANGUAGE: Python

PRIMARY LIBRARY: PySpark


DATASET: Amazon's Jewelry Review dataset

Dataset can be downloaded from: https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Jewelry_v1_00.tsv.gz



Steps to running the program:

1. Download the dataset from the above link and mount it onto a location on your Google Drive 
3. Set up Spark on Google Colab using the Java JVM and Python to set up Pyspark
4. Start a Spark session
2. To load dataset in notebook, replace the path for loaded_info = spark.read.csv('path of downloaded dataset',sep='\t', inferSchema=True, header=True)
6. Gather and analyse columns as needed



