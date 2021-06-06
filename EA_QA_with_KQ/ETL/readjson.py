'''
将数据装载进neo4j图数据库
'''

#coding:utf-8
from py2neo import Node, Graph, Relationship
import json
graph = Graph("http://localhost:7474",auth = ("neo4j","123456")) # 本地的neo4j数据库

class Company(object):
    def __init__(self,code,name,market,industry,establishment_date,address,telephone,business):
        self.code = code
        self.name = name
        self.market = market
        self.industry = industry
        self.establishment_date = establishment_date
        self.address = address
        self.telephone = telephone
        self.business = business

    def makeToNode(self):
        companyNode = Node('公司',name = self.name,code = self.code,market = self.market, industry = self.industry,establishment_date = self.establishment_date,
                           address = self.address,telephone = self.telephone,business = self.business)
        graph.create(companyNode)
        return companyNode

class People(object):
    def __init__(self,name,sex,year,education):
        self.name = name
        self.sex = sex
        self.year = year
        self.education = education

    def makeToNode(self):
        peopleNode = Node('人',name = self.name,sex = self.sex, year = self.year,education=self.education)
        graph.create(peopleNode)
        return peopleNode

    def hasPerson(self,name,sex,year,education):
        person = graph.run('MATCH(n:人) where n.name = \''+name+'\'and n.sex = \''+sex+
                           '\'and n.year = \''+year+'\'and n.education = \''+education+'\' RETURN n').data()
        if(len(person)==0):
            return None
        else:
            return person

    def linkToCompany(self,profession,companyNode,peopleNode):
        relation = Relationship(peopleNode,profession,companyNode)
        relation['name']=profession
        graph.create(relation)


def read_file(filepath):
    with open(filepath,encoding="utf-8") as fp:
        content=fp.read()
    return content

def readJson(x):
    content = read_file(x)
    content = content.replace("\"", "”")
    content = content.replace("\\x7f", "")
    content = content.replace("None","\'None\'")
    content = content.replace("\'", "\"")
    list_json = json.loads(content)
    dealJson(list_json,0)
    return

def dealJson(list_json,start):
    for messages in list_json:
        print("进行到:"+messages) # 回显，跑的时候记一下跑到哪了，这样崩溃的时候好处理
        # if(messages=='002584'): # 如果真的崩溃了，比如跑到002584崩溃了，那就把这些注释回来，然后把数字改成你崩溃的地方
        #     start=1
        # if(start==0):
        #     print("跳过:" + messages)
        #     continue
        # else:
        #     print("正式开始")
        information = list_json[messages]['information']
        code = information['code']
        name = information['name']
        market = information['market']
        industry = information['industry']
        establishment_date = information['establishment_date']
        address = information['address']
        telephone = information['telephone']
        business = information['business']
        company = Company(code,name,market,industry,establishment_date,address,telephone,business)
        companyNode = company.makeToNode()
        peoples = list_json[messages]['executives']
        for people in peoples:
            name = people['name']
            sex = people['sex']
            year = people['year']
            education = people['education']
            profession = people['profession']
            # cyper="MATCH p=()-[r:`"+profession+"`]-() SET r={name:'"+profession+"'} ;"
            # print(cyper)
            # graph.run(cyper)
            person = People(name,sex,year,education)
            if(person.hasPerson(name,sex,year,education) is None):
                personNode = person.makeToNode()
                person.linkToCompany(profession,companyNode,personNode)
            else:
                personNode = person.hasPerson(name,sex,year,education)[0]['n']
                person.linkToCompany(profession, companyNode, personNode)



if __name__ == '__main__':
    x = "result.txt" # 该文件下载下来什么都没改过
    graph.delete_all() # 这个是删除数据库内原有图谱，建议万不得已不要点
    readJson(x)