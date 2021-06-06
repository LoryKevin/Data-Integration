import pandas as pd
from pandas import Series, DataFrame
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import re
import jieba

# 获取所有的文件
def getfilelist(root_path):
    file_path_list=[]
    file_name=[]
    walk = os.walk(root_path)
    for root, dirs, files in walk:
        for name in files:
            filepath = os.path.join(root, name)
            file_name.append(name)
            file_path_list.append(filepath)
    # print(file_name)
    # print(file_path_list)
    # print(len(file_path_list))
    return file_path_list


class Question_classify():
    def __init__(self):
        # 读取训练数据
        self.train_x,self.train_y=self.read_train_data()
        # 训练模型
        self.model=self.train_model_NB()
    # 获取训练数据
    def read_train_data(self):
        train_x=[]
        train_y=[]
        file_list=getfilelist("./data/question/") # 遍历所有文件
        # 遍历所有文件
        for one_file in file_list:
            # 获取文件名中的数字
            num = re.sub(r'\D', "", one_file) # 替换文件名字符串的非数字字符为空，即提取字符中的数字，'\D'表示非数字字符
            # 如果该文件名有数字，则读取该文件
            if str(num).strip()!="":
                # 设置当前文件下的数据标签，即该文件内数据对应的类别标签，对应训练样本的y数据
                label_num=int(num)
                # 读取文件内容
                with(open(one_file,"r",encoding="utf-8")) as fr:
                    data_list=fr.readlines()
                    for one_line in data_list: # 一行为一条训练样本
                        word_list=list(jieba.cut(str(one_line).strip()))
                        # 将这一行加入结果集，每条训练样本的x数据由通过空格相连的词组构成
                        train_x.append(" ".join(word_list))
                        train_y.append(label_num)
        return train_x,train_y

    # 训练并测试贝叶斯分类器模型-Naive Bayes
    def train_model_NB(self):
        X_train, y_train = self.train_x, self.train_y
        self.tv = TfidfVectorizer()
        train_data = self.tv.fit_transform(X_train).toarray() # tfidf向量化模型是基于全部训练数据训练得到，后续预测的时候也需要使用
        clf = MultinomialNB(alpha=0.01) # 建立MultinomialNB模型
        clf.fit(train_data, y_train) # 训练MultinomialNB模型
        return clf

    # 预测
    def predict(self,question):
        question=[" ".join(list(jieba.cut(question)))]
        test_data=self.tv.transform(question).toarray() # 用训练号的词向量化模型，向量化输入问句
        y_predict = self.model.predict(test_data)[0] # 返回概率最大的预测类别
        # print("question type:",y_predict)
        return y_predict

if __name__ == '__main__':
    qc=Question_classify()
    qc.predict("梁慧在哪里任职？")