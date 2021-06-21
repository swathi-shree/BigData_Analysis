# -*- coding: utf-8 -*-
"""bigdata_shared.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sffYecjxWs-uZv-WbkJI87PrvrBchYxB

# Amazon Customer Sentimental Analysis using Spark and Python on Google Colab

## Project Setup

We can use this information to analyze Amazon’s most successful jewellery product launches, discover insights into consumer reviews and personal favourites and assist with ML models.

In order to start any big data computations or analysis, we need to install the necessary components for Google Colaboratory, decompress them and install modules for our IDE.

We aim to use Python to code our Spark programs, but because Spark setup is mainly set up on Scala, we need to use the JDK for Java to set up the Java VM.
"""

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz
!tar -xvf spark-3.1.1-bin-hadoop2.7.tgz
!pip install -q findspark
!pip install pyspark

"""This installs all the necessary dependencies in Colab. Now, we can set the environment variables to point to this virtual machine and and use the downloaded Spark path. This will enable us to run Pyspark in the Colab environment."""

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.1-bin-hadoop2.7"

"""We then locate Spark on the Drive."""

import findspark
findspark.init()

"""Once Spark has been located, we can start a SparkSession with PySpark. A SparkSession is the entry point of an application and can handle operations in the scope of the application.  """

# import from pyspark library
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").getOrCreate()

"""We use the spark.sql.shuffle.partitions to redistribute data across the RDD (a Spark database) frame."""

spark = SparkSession \
    .builder \
    .appName("Spark Customer Review Analysis for Amazon") \
    .config("spark.sql.shuffle.partitions", "100")\
    .getOrCreate()

"""A Spark application called "Spark Review Analysis for Amazon" should be running on the server. Now, let's try loading the dataset. Our dataset is a structured file (.csv), which makes it easier to analyse large amounts of data as well. The dataset is stored on a shared Google Drive folder, but the file might need to be publicly accessible.  """

import pandas as pd
import io

from google.colab import drive
drive.mount('/content/gdrive')

"""The dataset we are using is a .tsv file obtained from Amazon's Jewelry Review dataset on: https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Jewelry_v1_00.tsv.gz. Because this is a .tsv file instead of a .csv, we need to explicitly declare the separator to be a TAB space instead of a COMMA separator.  """

#upload the Kaggle downloaded dataset - Swathi 
loaded_info =spark.read.csv('/content/gdrive/My Drive/751/amazon_reviews_us_Jewelry_v1_00.tsv', sep='\t', inferSchema=True, header=True)

#upload the Kaggle downloaded dataset - Sahana
loaded_info = spark.read.csv('/content/gdrive/MyDrive/SOFTENG 751/amazon_reviews_us_Jewelry_v1_00.tsv',
                  sep='\t', inferSchema=True, header=True)

"""The dataset should now be loaded. printSchema() should show the columns and their data types as a hierarchy arising from 'root'."""

loaded_info.printSchema()

"""---
---

## Dataset Analysis


Let's have a look at what the loaded dataset looks like as a table, and what values the columns have. 
"""

# show() is a function that displays the top 20 rows of a dataset
loaded_info.show()

"""From the dataset, we can see that the review ID is unique in the table. This is the primary key. The customer ID is unique to each customer submitting their review, and the product ID is unique to each product.

## Exploratory Analysis

Getting a general overview on what reviews are like helps Amazon better understand what sort of product must be featured as a popular choice and what mustn't.

#### Total Reviews in Database

We assume that, for the scope of this project, every review has a star rating of 1 - 5. This means we would have to clean out records that are invalid (NULL, or other types).
"""

import pyspark.sql.functions as F

# Taking invalid star ratings out of our dataset 
loaded_info = loaded_info.filter(F.col("star_rating").cast("int").isNotNull()) 

ratings_df = loaded_info.groupBy("star_rating").count().withColumnRenamed("count","num_ratings")
ratings_df.show()

"""We can plot the distribution of ratings from 1-5 using the pandas module in Python."""

import matplotlib.pyplot as plt
import pandas as pd

ratings_plot = pd.DataFrame(ratings_df.collect())
ratings_plot.columns = ['star_rating','num_ratings']
ratings_plot.sort_values(by=['star_rating'], inplace=True)

ratings_plot.plot(kind='bar',x='star_rating',y='num_ratings',color='green')
plt.show()

"""We can also find the number of records in this cleaned dataset to obtain the total number of reviews in the dataset."""

# count the number of valid reviews in the dataset
print("There are %d reviews in the cleaned dataset." % loaded_info.count())

"""#### Reviews Per Unique Product

The number of reviews per product can be obtained by creating a collection of records that fall under the same product IDs. The groupBy() function makes a collection. withColumnRenamed() takes in the column that needs to be changed, and changes it to the parameter inserted second.
"""

# categorise reviews by the product's id (which is unique) and create a dataframe product_reviews
product_reviews = loaded_info.groupBy("product_id").count().withColumnRenamed("count","product_reviews")
product_reviews.show()

"""#### Number of Products"""

# count how many products there are
print("There are %d products in the cleaned database" % product_reviews.count())

"""#### 5 Highest Reviewed Jewellery Products

We can use sort() to a dataframe to arrange the rows in a particular order. We want the highest records to be on top, so we use ascending=False. take(5) grabs the first 5 records as objects in a list. In order to display it as a table, we need to convert it back to a dataframe using spark.createDataFrame().
"""

# from the dataframe, obtain the 5 highest reviewed products 
top_products = product_reviews.sort("product_reviews",ascending=False).take(5)

# change the list back to dataframe
top_products = spark.createDataFrame(top_products)
top_products.show()

"""#### Details of Highest Reviewed Product"""

top_products.join(loaded_info,"product_id","left").select("product_id","product_reviews","marketplace","product_title","product_category").show(1)

"""#### Summary of Product Reviews

We use summary() to extract the largest number of products, which is in the field 'count', the mean product reviews, the standard deviation of reviews, and the median number of reviews in which is in the field '50%'.
"""

product_reviews.select('product_reviews').summary().show()

"""#### Number of Reviews Per Customer"""

# Create the consumer_table DataFrame
customer_reviews = loaded_info.groupBy('customer_id').count().withColumnRenamed("count", "customer_reviews").cache()
customer_reviews.show()

"""#### 5 Customers That Reviewed The Most"""

# obtain the top 5 records of sorted dataframe
top_customers = customer_reviews.sort("customer_reviews",ascending=False).take(5)
# change the list back to dataframe
top_customers = spark.createDataFrame(top_customers)
top_customers.show()

"""### Most Influential Customer

The most influential customer, according to our scope, is the customer that has reviewed the most.
"""

top_customers.show(1)

"""## Review Analysis

Review Analysis can be very critical for statistical computations or analysis. Verifying calculations also becomes easy with these metrics.

### Selecting Positive Reviews

Positive reviews are considered to be reviews whose star_rating is either 4 stars or 5 stars, on a scale of 1 star to 5 stars.
"""

# select all reviews in the top 10000 records that are over 3 stars
tenthous_positive_readings = spark.createDataFrame(loaded_info.take(10000)).filter("star_rating >= 4")
print("The number of reviews exceeding 3 stars for the first 10000 records are %d." % tenthous_positive_readings.count())

"""#### Positive Reviews of 5th Most Popular Product

We are selecting the product that is the 5th popular one, row index 4 of the dataframe.
"""

# obtain the product id of the 5th element from the set of top products reviewed
product_id = list(top_products.select("product_id").take(5))

# filter positive readings for particular product_id by star_rating
positive_readings = loaded_info.filter("product_id = '%s' and star_rating >= 4" % product_id[4][0])\
                .groupBy("star_rating").count().withColumnRenamed("count","positive_reviews")
print("The product being analysed is '%s'" % product_id[4][0])
positive_readings.show()

"""#### 5 Highest Positively Reviewed Products

For the dataframe that has records with star_rating >=4, every record is collected by product_id (which is unique). The count() function counts the number of reviews every product has, and the whole collection is sorted in descending order to display highest reviewed products.

We're only displaying the first 5, and hence show(5).
"""

highest_positives = loaded_info.filter("star_rating >=4").groupBy("product_id") \
                   .count().withColumnRenamed("count","positive_reviews") \
                   .sort("positive_reviews",ascending=False)
highest_positives.show(5)

"""### Selecting Negative Reviews

Negative reviews are considered to be reviews whose star_rating is either 1 star or 2 stars, on a scale of 1 star to 5 stars.
"""

# select all reviews in the top 10000 under 3 stars as negative
tenthous_negative_readings = spark.createDataFrame(loaded_info.take(10000)).filter("star_rating <= 2")
print("The number of reviews under 3 stars for the first 10000 records are %d." % tenthous_negative_readings.count())

"""#### Negative Reviews for Most Popular Product

Let's analyse the most popular product for its negative reviews.
"""

# obtain the product id of the most popular product ([0][0] for top_products) from the set of trending reviews
product_id = list(top_products.select("product_id").take(1))

# filter negative readings for particular product_id by star_rating
negative_readings = loaded_info.filter("product_id = '%s' and star_rating <= 2" % product_id[0][0])\
                .groupBy("star_rating").count().withColumnRenamed("count","negative_reviews")
print("The product being analysed is '%s'" % product_id[0][0])
negative_readings.show()

"""#### 5 Highest Negatively Reviewed Products"""

highest_negatives = loaded_info.filter("star_rating <=2").groupBy("product_id") \
                   .count().withColumnRenamed("count","negative_reviews") \
                   .sort("negative_reviews",ascending=False)
highest_negatives.show(5)

"""### Is A Product Overall Liked or Not?

For the 5th most popular product, we can say the product is overall liked by customers if the total number of positive reviews > 50% of total reviews.
"""

# obtain total number of reviews for product_id[4][0]
product_id = list(top_products.select("product_id").take(5))
reviews_for_select_product = product_reviews.filter("product_id = '%s'" % product_id[4][0]).collect()

print('The total number of reviews for this product is: ', reviews_for_select_product[0][1])

total_curr_reviews = reviews_for_select_product[0][1]
# find 50% of that value
fifty_percent_curr_reviews = total_curr_reviews/2

# find positive reviews
pos_revs = positive_readings.collect()
total_pos_revs = (pos_revs[0][1] + pos_revs[1][1])

# if positive > 50% of total, mark as popular
if (total_pos_revs > fifty_percent_curr_reviews):
  print('The 5th most popular product is well liked by: {}% reviewers'.format(total_pos_revs*100/total_curr_reviews))
else:
  print('The 5th most popular product is mostly disliked by: {}% reviewers'.format((1-(total_pos_revs/total_curr_reviews))*100))

"""For the most popular product, we can say the product is overall liked by customers if the total number of negative reviews < 50% of total reviews."""

# obtain total number of reviews for product_id[0][0]
reviews_for_select_product = top_products.filter("product_id = '%s'" % product_id[0][0]).collect()

print('The total number of reviews for this product is: ', reviews_for_select_product[0][1])

total_curr_reviews = reviews_for_select_product[0][1]
# find 50% of that value
fifty_percent_curr_reviews = total_curr_reviews/2

# find negative reviews
neg_revs = negative_readings.collect()
total_neg_revs = (neg_revs[0][1] + neg_revs[1][1])

# if negative < 50% of total, mark as popular
if (total_neg_revs < fifty_percent_curr_reviews):
  print('The most popular product is well liked by: {}% reviewers'.format((1-(total_neg_revs/total_curr_reviews))*100))
else:
  print('The most popular product is mostly disliked by: {}% reviewers'.format(total_neg_revs*100/total_curr_reviews))

"""## Review Sentimental Analysis

In order to determine whether reviews are positive, negative or neutral based on review text, sentiment analysis is performed. It can help businesses monitor popularity of certain brands, products or even categories, which can improve customer experience as well as Amazon's market research team.

Some packages need to be downloaded for this. The Natural Language Toolkit (NLTK) is one of Python's most useful AI libraries, that handles a variety of language processing tasks.
"""

import nltk
nltk.download('punkt')
nltk.download('stopwords')
from pyspark.sql import types

"""#### Obtain Review Tags

There are a multitude of models that can assist us with sentimental analysis. For the scope of our project, we will be discussing and implementing the VADER model that is built on a highly text based dataset. It is highly useful in classification problems, and works well on text inputs. 

For the scope of our project, we will be using this analyser to predict the tone of a review. The three categories a review can fall under are 'positive', 'negative' and 'neutral'. 

Therefore, the tags are 'pos', 'neg' and 'neu'.
"""

!pip install vaderSentiment

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# VADER sentiment analysis tool for getting pos, neg and neu tags.
def VADER_sentimental_score(sentence):
    # initialise an analyser for the program
    sent_analyser = SentimentIntensityAnalyzer()
    # obtain polarity scores for the review from the analyser
    vader_scores = sent_analyser.polarity_scores(sentence)
    # 'compound' is the label that stores the overall 'tone' tag and is between 1 and -1
    score = vader_scores['compound']
    if score >= 0.5:
        return 'pos'
    elif (score > -0.5) and (score < 0.5):
        return 'neu'
    elif score <= -0.5:
        return 'neg'

"""Once this function has been created, we can check our dataframe for any NULL values in the review body, and filter them out. This is because we won't be able to analyse reviews of this sort using the analyser. 

Again, we're only examining the first 10000 rows of the dataset for the sake of not hogging Google Colab's resources. 
"""

import numpy
# if the review_body field is empty, filter out because can't perform sentiment analysis on NULL
review_bodies = loaded_info.select("product_id","review_body") \
                .filter("review_body IS NOT NULL").take(10000)

"""For every review that we find, we need to store the product_id (as that is the identifying field), as well as the sentiment tag.  """

# review_bodies is a list
sentiment_score = [[0 for i in range(2)] for j in range(10000)]
for i in range(10000):
  sentiment_score[i][0] = (review_bodies[i][0])
  sentiment_score[i][1] = VADER_sentimental_score(review_bodies[i][1])

"""### Review Comparison - CONFUSION MATRIX

With these sentiment scores, we can combine this dataframe with the review_bodies and a set of star_rating(s) to get a dataframe with three columns.
"""

# with these positive and negative reviews, we can potentially make a new dataframe
review_bodies_df = spark.createDataFrame(review_bodies)

from pyspark.sql.types import StringType
sentiment_score_df = spark.createDataFrame(sentiment_score).withColumnRenamed("_1","product_id").withColumnRenamed("_2","sent_score")
star_rating_df = spark.createDataFrame(loaded_info.select("product_id","star_rating").take(10000))

new_analysis_df = spark.createDataFrame(sentiment_score_df.join(review_bodies_df,"product_id","inner") \
                                     .join(star_rating_df,"product_id","inner").take(10000))
new_analysis_df.show()

"""This table gives us all the fields required to compute a confusion matrix.

We know already that every star_rating of 4 and above is a positive rating. So, we find the number of true positives, by comparing a 4+ star rating with a 'pos' tag.
"""

# select the records that are both pos and above 3 stars
sent_pred_pos_df = new_analysis_df.filter("star_rating >=4")
tot_pos_count = sent_pred_pos_df.count()

sent_pred_pos_df = sent_pred_pos_df.filter("sent_score='pos'")
print("The number of true positive reviews in the database is %d." % sent_pred_pos_df.count())

# find percentage of correct predictions 
print("Percentage of true positive predictions by the VADER analyser for the first 10000 reviews is %f." % (float)(sent_pred_pos_df.count()*100/tot_pos_count))

"""We can find the false positives, by checking for a star_rating of 4+ but with the tag 'neg'."""

# false positives
sent_pred_false_pos_df = new_analysis_df.filter("star_rating >=4").filter("sent_score='neg'")
print("The number of false positive reviews in the database is %d." % sent_pred_false_pos_df.count())

# find percentage of false positives
print("Percentage of false positive predictions by the VADER analyser for the first 10000 reviews is %f." % (float)(sent_pred_false_pos_df.count()*100/tot_pos_count))

"""A similar analysis can be done for negative reviews, where 2- stars are considered absolute negatives. A tag 'neg' with 2- stars is a true negative, while a 'pos' tag with 2- stars is a false negative. """

# select the records that are both neg and below 3 stars
sent_pred_neg_df = new_analysis_df.filter("star_rating <=2")
tot_neg_count = sent_pred_neg_df.count()

sent_pred_neg_df = sent_pred_neg_df.filter("sent_score='neg'")
print("The number of true negative reviews in the database is %d." % sent_pred_neg_df.count())

# find percentage of correct predictions 
print("Percentage of true negative predictions by the VADER analyser for the first 10000 reviews is %f." % (float)(sent_pred_neg_df.count()*100/tot_neg_count))

# false negatives
sent_pred_false_neg_df = new_analysis_df.filter("star_rating <=2").filter("sent_score='pos'")
print("The number of false negative reviews in the database is %d." % sent_pred_false_neg_df.count())

# find percentage of false negatives
print("Percentage of false negative predictions by the VADER analyser for the first 10000 reviews is %f." % (float)(sent_pred_false_neg_df.count()*100/tot_neg_count))

"""We can now compute the confusion matrix. This matrix is detailed in the report rather than being plotted on Colab.

### Creating WordClouds

WordClouds are a great way to visualise most featured keywords from a database. Here, using the 'pos' and 'neg' tags for every review, we are able to tokenise every word of the review and pick out keywords.

Here, the NLTK package comes in handy, with some in-built modules like 'stopwords' and 'word_tokenize' to pick out keywords.
"""

# gather fields that are tagged positive from the first 10000 rows
pos = new_analysis_df.filter(new_analysis_df.sent_score == "pos").select('review_body')
pos = pos.collect()

# gather fields that are tagged negative from the first 10000 rows
neg = new_analysis_df.filter(new_analysis_df.sent_score == "neg").select('review_body')
neg = neg.collect()

from nltk.corpus import stopwords

"""We create a function that takes in a list, finds the review_body from the list and obtains keywords from the review_body."""

# create a function that tokenises words
def create_word_cloud_keywords(row):
    words_tokenised = ''
    for val in row:
        # grab the word from selected column
        text = val[0].lower()
        # clear other punctuations except .
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in string.punctuation]
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        # append selected keywords to words_tokenised
        for words in tokens:
            words_tokenised = words_tokenised + words + ' '
    return words_tokenised

"""By running create_word_cloud_keywords(), we should be able to obtain all the keywords of the list rows inputted. However, if we need to visualise this result, we must plot a WordCloud. Python has a package called wordcloud that creates this image for us. A WordCloud variable has a generate() method, that takes in tokens and outputs an image featuring the most used keywords.  """

from wordcloud import WordCloud
import string

# generate WordClouds 
pos_wordcloud = WordCloud(width=900, height=500, background_color ='white').generate(create_word_cloud_keywords(pos))
neg_wordcloud = WordCloud(width=900, height=500, background_color ='white').generate(create_word_cloud_keywords(neg))

import matplotlib.pyplot as plt

# plot the WordCloud using matplotlib 
def plot_wordCloud(wordCloud):
    plt.figure(figsize=(20,10), facecolor='None')
    plt.imshow(wordCloud)
    plt.tight_layout(pad=0)
    plt.axis("off")
    plt.show()

"""We can now visualise these WordClouds."""

plot_wordCloud(pos_wordcloud)

plot_wordCloud(neg_wordcloud)

"""###Sentiment distribution across each product along with star ratings

Displays star ratings and sentiments side by side for products to see if and how they correlate - might be useful for businesses to understand customer's views
"""

#total number of postive,negative and null reviews for all the products 
new_df = new_analysis_df.groupby("product_id","sent_score","star_rating").count()
#transposes sent_score from row to column 
new_df.groupBy("product_id","star_rating").pivot("sent_score").count().show()

"""### Comparison of sentiments with ratings

Shows the number of sentiment review's the analyser was able to predict accurately by comparing with user given ratings
"""

# select all reviews in the top 10000 records that are 5 stars and are positively rated
pos_df = new_analysis_df.filter("sent_score='pos'")
readings = spark.createDataFrame(pos_df.take(10000)).filter("star_rating >= 5")

# select all reviews in the top 10000 records that are 3 stars and are neutrally rated
neu_df = new_analysis_df.filter("sent_score='neu'")
readings2 = spark.createDataFrame(neu_df.take(10000)).filter("star_rating = 3")


# select all reviews in the top 10000 records that are less than 2 stars and are negatively rated
neg_df = new_analysis_df.filter("sent_score='neg'")
readings3 = spark.createDataFrame(neg_df.take(10000)).filter("star_rating <= 2")

print("Positive sentiments with 5 star rating for the first 10000 records are %d." % readings.count())
print("Neutral sentinments at 3 star rating for the first 10000 records are %d." % readings2.count())
print("Negative sentiments with less than 2 stars for the first 10000 records are %d." % readings3.count())
