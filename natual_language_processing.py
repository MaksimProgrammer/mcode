import re
import os
import math

abspath = os.path.dirname(os.path.abspath(__file__))
text_path = input("Please enter the text that you wanna process:\n")
with open(text_path, mode='rt', encoding='utf-8') as f:
    data = f.read()


# 输入单词的小写字符串，计算该单词的IDF
def idf_cal(w):
    i = 0
    j = 0
    corpus_path = os.path.join(abspath, 'corpus')
    for root, dirs, files in os.walk(corpus_path):
        for file in files:
            j += 1
            with open(os.path.join(corpus_path, file), mode='rt', encoding='utf-8') as file_object:
                t_data = file_object.read().lower()
                if re.findall(w, t_data):
                    i += 1
    return math.log(j / (i + 1))


# task 1 文本预处理
def split_sents(text):
    text = re.sub('(\\+86-1|1)\\d{9,10}', '(phone)', text)
    text = re.sub('\\w+@(\\w+\\.)+\\w+', '(email)', text)
    data_list_pre = re.split("(?<=[.?!])\\s*(?=[A-Z]\\w*)", text)
    data_list = []
    data_list_pre_cookie = []
    # 在单词和与单词直接相连的标点符号之间加上一个空格
    for index, s in enumerate(data_list_pre):
        data_list_pre_cookie.append(re.sub('(?<=[a-zA-Z])+!', ' !',
                                           re.sub('(?<=[a-zA-Z])+\\?', ' ?', re.sub('(?<=[a-zA-Z])+,', ' ,',
                                                                                    re.sub('(?<=[a-zA-Z])+\\.',
                                                                                           ' .', s)))).lower())
    # 根据空格拆分句子
    for s in data_list_pre_cookie:
        data_list.append(re.split('\\s+', s))

    return data_list_pre, data_list


# task 2 生成关键词
def keywords_extraction(text):
    # 获得文本中的单词列表（有重复），和单词集合（无重复），单词以小写字母构成
    word_list = re.findall('\\w+', text.lower())
    word_num = len(word_list)
    word_set = set(word_list)
    dif_word_num = len(word_set)

    # 计算单词的tf-idf，并根据tf-idf排序
    word_list_sort = []
    for word in word_set:
        tf_idf = (word_list.count(word) / word_num) * idf_cal(word)
        word_list_sort.append((tf_idf, word))
    word_list_sort.sort()

    # 打开停用词表，筛选5%非停用词的关键词
    with open(os.path.join(abspath, 'stop_list.txt')) as stop_list_object:
        stop_list = stop_list_object.read().split(' ')

    i = 0
    key_word_list = []
    while True:
        word_group = word_list_sort.pop()
        if word_group[1] not in stop_list:
            i += 1
            key_word_list.append(word_group[1])
        if i / dif_word_num >= 0.05:
            break

    with open(os.path.join(abspath, 'key_word.txt'), mode='wt', encoding='utf-8') as file_object:
        for word in key_word_list:
            file_object.write(word + ' ')

    return key_word_list


def keysentences_extraction(slist, sflist, kwlist):
    index_list = []
    i = -1
    sent_num = len(slist)
    for sent_fragment in sflist:
        i += 1
        j = 0
        for word in sent_fragment:
            if word in kwlist:
                j += 1
        index_list.append((j, i))

    index_list.sort(reverse=True)
    key_sentence_list = []

    with open(os.path.join(abspath, 'key_sentence.txt'), mode='wt', encoding='utf-8') as file_object:
        i = 0
        for group in index_list:
            file_object.write(slist[group[1]] + '\n')
            key_sentence_list.append(slist[group[1]])
            i += 1
            if i / sent_num >= 0.25:
                break

    return key_sentence_list


# 预处理结果
result = split_sents(data)
sent_list = result[0]
sent_fragment_list = result[1]

# 获取关键词列表以备用
k_w_list = keywords_extraction(data)

# 获取关键句列表
k_s_list = keysentences_extraction(sent_list, sent_fragment_list, k_w_list)
