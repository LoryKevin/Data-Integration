# 项目说明

> Enterprise Architecture Question Answering System Based on Knowledge Graph  基于知识图谱的企业结构问答系统
>
> 13组 181250096陆志晗 181250104苗轶轩 181250107纳思彧 181250133王博
>
> Git仓库地址：https://github.com/LoryKevin/Data-Integration



## 项目运行

```python
cd EA_QA_with_KQ  # 进入项目文件夹
pip install requirements.txt  # 安装依赖库
python ETL/readjson.py  # 向图数据库中写入数据，需要先行启动Neo4j，默认auth = ("neo4j","123456")；数据量较大，总计共有54934个节点和55831个关系
python code.py 127.0.0.1:1234  # 运行主程序
```



## 项目简介

### 实现功能

对沪深两市上市公司及其管理层相关信息的智能问答，问题包括但不限于：

对公司：查地址；查创办时间；查业务范畴；查股票信息；查管理层名单；查职位上的人

对人员：查职位；查生日；查学历；查重名；查兼职；查公司内任职

### 流程示意图

![流程示意图](https://ftp.bmp.ovh/imgs/2021/06/33cb03022768f6f0.png)

### 主要技术

网络爬虫：Python爬虫 requests库

图数据库：Neo4j

自然语言处理：jieba分词

机器学习：sklearn TF-IDF

### 组内分工

181250096陆志晗：问题处理，分类器训练，前后端对接，说明文档与演示汇报

181250104苗轶轩：数据爬取与清洗，jieba分词及词典数据抽取

181250107纳思彧：Neo4j数据库装载，问答模板设计，Cypher查询语句编写

181250133王博：前端设计与交互，图谱呈现

### 效果图

Neo4j数据库
![数据库](https://i.bmp.ovh/imgs/2021/06/f7b3ebc9a9d2a7ba.png)

Python控制台
![控制台](https://ftp.bmp.ovh/imgs/2021/06/60de9301e35b8b6f.png)

交互界面demo
![前端效果](https://ftp.bmp.ovh/imgs/2021/06/a0b30aab7e0a399a.jpg)



## 代码解析

### ETL部分

数据爬取：EA_QA_with_KQ/ETL/get_data.py

图数据库装载：EA_QA_with_KQ/ETL/readjson.py

### 语义识别部分

命名实体识别（词性标注）

```
# 自定义三种词性
nnc：noun+cooperation 公司名词
nnr：noun+ren 人名名词
nnp：noun+position 职位名词
```

自定义词典（部分示例）：EA_QA_with_KQ/data/extract.txt

```
# 包括数据集中所有公司名、人名、职位名
浦发银行 15 nnc
郑杨 15 nnr
董事长 15 nnp
```

分词与词性标注：EA_QA_with_KQ/preprocess_data.py，line 56-77

```python
def question_posseg(self):
    # 添加自定义词典
    jieba.load_userdict("./data/extract.txt")
    # 去除无用标点符号
    clean_question = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+","",self.raw_question)
    self.clean_question=clean_question
    # 分词
    question_seged=jieba.posseg.cut(str(clean_question))
    result=[]
    question_word, question_flag = [], []
    for w in question_seged:
        temp_word=f"{w.word}/{w.flag}"
        result.append(temp_word)  # result格式为“词/词性”
        # 预处理问题，为后续的预测和查询存储数据
        word, flag = w.word,w.flag
        question_word.append(str(word).strip())  # 删除头尾空格、/n、/t
        question_flag.append(str(flag).strip())
    assert len(question_flag) == len(question_word)  # 一一对应
    self.question_word = question_word  # 词列表
    self.question_flag = question_flag  # 词性列表
    print(result)  # 如：'杨国平/nnr','在/p','哪里/r','任职/v'
    return result
```

### 问题分类部分

抽象问题模板：EA_QA_with_KQ/data/question/question_classification.txt

```
0:nnc 地址
1:nnc 创办时间
2:nnc 业务
3:nnc 股票
4:nnc 人员列表
5:nnc nnp 人员
6:nnr nnc 职位
7:nnr 出生日期
8:nnr 学历
9:nnr 公司
```

问题分类训练集（以类型3为例）：EA_QA_with_KQ/data/question/【3】公司股票信息.txt

```
nnc在哪个股交所上市的
nnc是上市公司吗
nnc是在上交所还是深交所
nnc是哪个板的
nnc的股票在上交所还是深交所
哪里能查到nnc的股票
nnc的股票代码是多少
nnc的股票代码是什么
我要到哪儿买nnc的股票
```

训练分类器模型：EA_QA_with_KQ/question_classification.py，line 32-61

```python
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
```

使用模型进行分类：EA_QA_with_KQ/question_classification.py，line 64-69

```python
def predict(self,question):
    question=[" ".join(list(jieba.cut(question)))]
    test_data=self.tv.transform(question).toarray() # 用训练号的词向量化模型，向量化输入问句
    y_predict = self.model.predict(test_data)[0] # 返回概率最大的预测类别
    # print("question type:",y_predict)
    return y_predict
```

得到模板：EA_QA_with_KQ/preprocess_data.py，line 79-95

```python
def get_question_template(self):
    # 抽象问题
    for item in ['nnc','nnp','nnr']:
        while (item in self.question_flag):
            ix=self.question_flag.index(item) # 查找相应词性的位置
            self.question_word[ix]=item # 词替换为词性
            self.question_flag[ix]=item+"ed" # 修改词性，表示已替换了
    # 将问题转化字符串
    str_question="".join(self.question_word)
    print("抽象问题为：",str_question)
    # 通过分类器获取问题模板编号
    question_template_num=self.classify_model.predict(str_question)
    print("使用模板编号：",question_template_num)
    question_template=self.question_mode_dict[question_template_num]
    print("问题模板：",question_template)
    question_template_id_str=str(question_template_num)+"\t"+question_template
    return question_template_id_str
```

### 查询部分

根据模板号调用方法：EA_QA_with_KQ/question_template.py，line 24-43

```python
def get_question_answer(self,question,template):
    # 如果问题模板的格式不正确则结束
    assert len(str(template).strip().split("\t"))==2
    template_id,template_str=int(str(template).strip().split("\t")[0]),str(template).strip().split("\t")[1]
    self.template_id=template_id
    self.template_str2list=str(template_str).split()

    # 预处理问题
    question_word,question_flag=[],[]
    for one in question:
        word, flag = one.split("/")
        question_word.append(str(word).strip())
        question_flag.append(str(flag).strip())
    assert len(question_flag)==len(question_word)
    self.question_word=question_word
    self.question_flag=question_flag
    self.raw_question=question
    # 根据问题模板来做对应的处理，获取答案
    answer=self.q_template_dict[template_id]()
    return answer
```

Cypher语句查询（以类型3为例）：EA_QA_with_KQ/question_template.py，line 87-96

```python
def get_company_code(self):
    com_name = self.get_company_name()
    cql1 = f"match(m:公司) where m.name='{com_name}' return m.market"
    cql2 = f"match(m:公司) where m.name='{com_name}' return m.code"
    print(cql1)
    answer_market = self.graph.run(cql1)[0]
    answer_code = self.graph.run(cql2)[0]
    final_answer = com_name + "在" + answer_market + "上市，股票代码是"+answer_code+"。"
    return final_answer
```

访问数据库：EA_QA_with_KQ/query.py，line 3-12

```python
class Query():
    def __init__(self):
        self.graph=Graph("http://localhost:7474", username="neo4j",password="123456")

    def run(self,cql):
        result=[]
        find_rela = self.graph.run(cql)
        for i in find_rela:
            result.append(i.items()[0][1])
        return result
```
