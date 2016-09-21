from Facebook_Spider import *
import datetime
from pandas import Series,DataFrame
import pandas as pd


def store_status_data(topic, data):
    file_name = 'search_data/' + topic + '_data.json'
    file = open(file_name, 'w')
    json.dump(data, file)
    file.close()


def load_status_data(topic):
    file_name = 'search_data/' + topic + '_data.json'
    file = open(file_name, 'r')
    data = json.load(file)
    file.close()
    return data


def get_data(my_spider, topic):
    file_name = 'search_data/' + topic + '_data.json'
    if os.path.isfile(file_name):
        print('We have already got the data')
        overall_status_data = load_status_data(topic)
    else:
        print('There is no such data')
        overall_status_data = get_data_for_topic(topic=topic, my_spider=my_spider)
        store_status_data(topic=topic, data=overall_status_data)
    return overall_status_data


def unicode_normalize(text):
    return text.translate({0x2018: 0x27, 0x2019: 0x27, 0x201C: 0x22, 0x201D: 0x22,
                           0xa0: 0x20}).encode('utf-8')


def get_num_total_reactions(reaction_type, reactions):
    if reaction_type not in reactions:
        return 0
    else:
        return reactions[reaction_type]['summary']['total_count']


def formalizing_data_about_status(status, spider):
    status_id = status['id']
    status_type = status['type']
    try:
        status_message = unicode_normalize(status['message']).decode('utf-8')
    except KeyError or UnicodeEncodeError or UnicodeDecodeError:
        status_message = ''
    try:
        link_name = unicode_normalize(status['name']).decode('utf-8')
    except KeyError or UnicodeEncodeError or UnicodeDecodeError:
        link_name = ''
    try:
        status_link = unicode_normalize(status['link']).decode('utf-8')
    except KeyError or UnicodeEncodeError or UnicodeDecodeError:
        status_link = ''

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
        status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    # status_published = status_published + datetime.timedelta(hours=-5)  # EST
    status_published = status_published.strftime(
        '%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    try:
        num_reactions = status['reactions']['summary']['total_count']
    except KeyError:
        num_reactions = 0
    try:
        num_comments = status['comments']['summary']['total_count']
    except KeyError:
        num_comments = 0
    try:
        num_shares = status['shares']['count']
    except KeyError:
        num_shares = 0

    # Counts of each reaction separately; good for sentiment
    # Only check for reactions if past date of implementation:
    # http://newsroom.fb.com/news/2016/02/reactions-now-available-globally/

    reactions = spider.get_status_reaction_data(status_id) if \
        status_published > '2016-02-24 00:00:00' else {}

    num_likes = 0 if 'like' not in reactions else \
        reactions['like']['summary']['total_count']

    # Special case: Set number of Likes to Number of reactions for pre-reaction
    # statuses

    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' \
        else num_likes

    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)

    result = dict()
    result['status_id'] = status_id
    result['status_message'] = status_message
    result['status_type'] = status_type
    result['link_name'] = link_name
    result['status_link'] = status_link
    result['status_published'] = status_published
    result['num_reactions'] = num_reactions
    result['num_comments'] = num_comments
    result['num_shares'] = num_shares
    result['num_likes'] = num_likes
    result['num_loves'] = num_loves
    result['num_wows'] = num_wows
    result['num_hahas'] = num_hahas
    result['num_sads'] = num_sads
    result['num_angrys'] = num_angrys

    return result


def get_data_for_topic(topic, my_spider):
    page_list = my_spider.get_page_from_searching(topic)
    print('The total numbers of pages related to this topic is: ' + str(len(page_list)))
    status_data_list = list()
    page_counter = 0
    for page in page_list:
        page_counter += 1
        print('Analyzing statuses for page: ' + page[0] + '(' + str(page_counter) + '/' + str(len(page_list)) + ')')
        status_list = my_spider.get_status_from_page(page[1])
        status_counter = 0
        for status in status_list:
            status_counter += 1
            print('Analyzing data for status: ' + status['id'] + '(' + str(status_counter) + '/' +
                  str(len(status_list)) + ')')
            status_data = formalizing_data_about_status(status, my_spider)
            status_data_list.append(status_data)
    return status_data_list


topic = 'samsung note 7'
facebook_spider = FacebookSpider()
data = get_data(facebook_spider, topic)
d = pd.DataFrame(data)
dropped_column = ['status_link', 'status_type', 'status_id', 'link_name', 'status_message']
d.drop(labels=dropped_column, axis=1, inplace=True)
for item in d.iterrows():
    data = dict((y, x) for x, y in item)
    print(type(item))
    print(type(data))
    print(data)


print(d)

print('end')
