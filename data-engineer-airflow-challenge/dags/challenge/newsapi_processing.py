import os
import pandas as pd
import boto3 as boto
from newsapi import NewsApiClient
from pandas.io.json import json_normalize
from datetime import datetime, timedelta, date
from io import StringIO

# Environment variables are loaded into Docker container through env file

# To-Do: Add logging to the fucntions to debug issues.
# To-Do: Bonus inclusion of additional keywords.
# To-Do: Implement the error handling from the newsapi library
# To-Do: Terraform to create the S3 bucket with the appropriate IAM role
# To-Do: Utilize xcom context passing to reduce the need for class instantiation

class Source_Headlines(object):
    def __init__(self):
        super(Source_Headlines,self).__init__()
        self.newsapi=NewsApiClient(api_key=os.environ["NEWS_API"])
        self.s3bucket = boto.resource('s3',
                                      aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                                      region_name='us-west-2')
        self.sources=pd.DataFrame()
        self.headlines=pd.DataFrame()
        self.bucket="dfenko-tempus"

    # Connects to the News API and gets sources
    def get_sources(self):
        en_sources=newsapi.get_sources(language="en")
        self.sources=json_normalize(en_sources['sources'])
        return(self.sources)

    # Specific function to handle the pull of headlines and json normalization
    # Separated for testability - invoked by store_headlines
    @staticmethod
    def headline_transform(source):
        source_headlines=pd.DataFrame()
        page_num=1
        results=self.newsapi.get_top_headlines(sources=source)
        num_results=results['totalResults']
        while len(source_headlines) > num_results:
            fetch=self.newsapi.get_top_headlines(sources=source,
                                                 page_size=100,
                                                 page=page_num)
            fetch=json_normalize(fetch['articles'])
            source_headlines=source_headlines.append(fetch,
                                                     ignore_index=True,
                                                     sort=True)
        return(source_headlines)

    def store_headlines(self):
        # Iterate over the ID column of the sources dataframe
        # Submit source to the transform functions
        # Upload to S3
        for source in self.sources['id']:
            csv_buffer=StringIO
            self.headlines=headline_transform(source)
            self.headlines.to_csv(csv_buffer)
            s3_load.Object(self.bucket,
                           id + "/" + str(date.today()) + \
                           "_top_headlines.csv").put(Body=csv.buffer.getvalue())
            # Clear self.headlines for the next source iteration
            self.headlines=pd.DataFrame()
