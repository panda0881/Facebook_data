import concurrent.futures
import json
import requests
import re
import os
from collections import Counter

app_id = "1582528948722044"
app_secret = "d42cf977697e2c4c50a1c70b72be4f9b"


class FacebookSpider:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.future_to_item = {}
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = self.app_id + '|' + self.app_secret
        self.s = requests.session()


    def get_user_data(self, user_id):
        data = ''
        return data

    def get_page_from_searching(self, topic):
        page_list = list()
        base = "https://graph.facebook.com/search?"
        q = 'q=' + topic
        searchType = '&type=page'
        test_token = '&access_token=' + self.access_token
        url = base + q + searchType + test_token
        response = self.s.get(url)
        result = json.loads(response.text)
        pages = result['data']
        for page in pages:
            page_list.append((page['name'], page['id']))
        while 'next' in result['paging']:
            url = result['paging']['next']
            response = self.s.get(url)
            result = json.loads(response.text)
            pages = result['data']
            for page in pages:
                page_list.append((page['name'], page['id']))
            print('total number of pages for now: ' + str(len(page_list)))
        return page_list

    def get_status_from_page(self, page_id):
        status_list = list()
        base = "https://graph.facebook.com/v2.7"
        node = "/%s/posts" % page_id
        fields = "/?fields=message,link,created_time,type,name,id," + \
                 "comments.limit(0).summary(true),shares,reactions" + \
                 ".limit(0).summary(true)"

        parameters = "&limit=%s&access_token=%s" % (100, self.access_token)
        url = base + node + fields + parameters
        response = self.s.get(url)
        result = json.loads(response.text)
        statuses = result['data']
        for status in statuses:
            status_list.append(status['id'])
        while 'paging' in result:
            url = result['paging']['next']
            response = self.s.get(url)
            result = json.loads(response.text)
            statuses = result['data']
            for status in statuses:
                status_list.append(status['id'])
            print('total number of pages for now: ' + str(len(status_list)))
        return status_list

