import os
import pandas as pd
import boto3 as boto
from newsapi import NewsApiClient
from pandas.io.json import json_normalize
from datetime import datetime, timedelta, date
from io import StringIO

# Environment variables are loaded into Docker container through env file

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


    # Headline collection and upload to S3
    def get_headlines(self):
        # Iterate over the ID column of the sources dataframe
        for source in self.sources['id']:
            page_num=1
            results=self.newsapi.get_top_headlines(sources=source)
            num_results=results['totalResults']
            # Default call is limited to 20 results per page.
            # Several sources have more headlines than the max 100 per page
            # Load the headlines and paginate
            while len(self.headlines) < num_results
                fetch=self.newsapi.get_top_headlines(sources=source,
                                                     page_size=100,
                                                     page=page_num)
                fetch=json_normalize(fetch['articles'])
                # Append results to the source headlines dataframe
                self.headlines=self.headlines.append(fetch,
                                                     ignore_index=True,
                                                     sort=True)
                page+=1
            # Because we are in an iteration of source, we can push
            # to the correct filepath in S3 expediently here.
            # Optimally, the S3 step would be its own subtask
            csv_buffer=StringIO()
            self.headlines.to_csv(csv_buffer)
            s3_load.Object(self.bucket,
                           id + "/" + str(date.today()) + \
                           "_top_headlines.csv").put(Body=csv.buffer.getvalue())
            # Clear self.headlines for the next source iteration
            self.headlines=pd.DataFrame()
