#coding:utf-8

import warnings
warnings.filterwarnings("ignore")
import inline as inline
import jieba
import numpy
import codecs
import re
import pandas as pd
import matplotlib.pylab as plt
from urllib import request
from bs4 import BeautifulSoup as bs
#%matplotlib inline

import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0,5.0)
from wordcloud import WordCloud

def getNowPlayingMoive_list():
    resp = request.urlopen('https://movie.douban.com/nowplaying/hangzhou/')
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data,'html.parser')
    nowplaying_movie = soup.find_all('div',id='nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li',class_='list-item')
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dict = {}
        nowplaying_dict['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list
def getCommentsById(movieId,pageNum):
    eachCommentList = []
    if pageNum > 0:
        start = (pageNum-1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments' + '?' +  'start=' + str(start) + '&limit=20' + 'sort=new_score' + '&status=P'
    print(requrl)
    resp = request.urlopen(requrl)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data,'html.parser')
    comment_div_lits = soup.find_all('div',class_='comment')
    for item in comment_div_lits:
        if item.find_all('span',class_='short')[0].string is not None:
             #print(item.find_all('span',class_='short')[0].string
             eachCommentList.append(item.find_all('span',class_='short')[0].string)
    #print(eachCommentList)
    return eachCommentList

def main():
    commentList = []
    NowPlayMovie_list = getNowPlayingMoive_list()
    for i in range(100):
        num = i + 1
        commentList_temp = getCommentsById(NowPlayMovie_list[4]['id'],num)
        commentList.append(commentList_temp)
    #print(commentList)

    comments = ''
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()

    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern,comments)
    cleaned_comments = ''.join(filterdata)

    segment = jieba.lcut(cleaned_comments)
    words_df = pd.DataFrame({'segment':segment})

    stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],encoding='utf-8')  # quoting=3全不引用
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]
    words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": numpy.size})
    words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

    wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", max_font_size=80)
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}

    word_frequence_list = []
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)

    wordcloud = wordcloud.fit_words(dict(word_frequence_list))
    plt.imshow(wordcloud)
    plt.savefig("result.jpg")
main()