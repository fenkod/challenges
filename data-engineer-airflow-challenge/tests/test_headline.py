#!/usr/bin/env python

from dags.challenge.newsapi_processing import Source_Headlines
import os
import sys
import time
import unittest
sys.path.append('../')

news_challenge = Source_Headlines()

class TestSample(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_transform(self):
        assumed_columns = ['author', 'content', 'description', 'publishedAt',
                           'source.id', 'source.name', 'title', 'url',
                           'urlToImage']
        sample_headlines = news_challenge.headline_transform("abc-news")
        self.assertEqual(sample_headlines.columns.all(), assumed_columns.all())

if __name__ == '__main__':
    unittest.main()
