from query import Query
import re
from py2neo import Graph,Node,Relationship,NodeMatcher

class QuestionTemplate():
    def __init__(self):
        self.q_template_dict={
            0:self.get_company_address,
            1:self.get_company_time,
            2:self.get_company_business,
            3:self.get_company_code,
            4:self.get_company_em,
            5:self.get_company_peo,
            6:self.get_company_pro,
            7:self.get_peo_birth,
            8:self.get_peo_edu,
            9:self.get_peo_countcompany,
        }


        self.graph = Query()


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

    # 获取名字
    def get_company_name(self):
        tag_index = self.question_flag.index("nnc")
        com_name = self.question_word[tag_index]
        return com_name

    def get_peo_name(self):
        tag_index = self.question_flag.index("nnr")
        com_name = self.question_word[tag_index]
        return com_name

    def get_pro_name(self):
        tag_index = self.question_flag.index("nnp")
        com_name = self.question_word[tag_index]
        return com_name

    # 0:地址
    def get_company_address(self):
        com_name=self.get_company_name()
        cql = f"match (m:公司) where m.name='{com_name}' return m.address"
        print(cql)
        answer = self.graph.run(cql)[0]
        print(answer)
        final_answer=com_name+"的地址是"+answer+"。"
        return final_answer

    # 1:创办时间
    def get_company_time(self):
        com_name = self.get_company_name()
        cql = f"match(m:公司) where m.name='{com_name}' return m.establishment_date"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = com_name + "成立于" + answer + "。"
        return final_answer
    # 2:业务
    def get_company_business(self):
        com_name = self.get_company_name()
        cql = f"match(m:公司) where m.name='{com_name}' return m.business"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = com_name + "的经营范围是:" + answer
        return final_answer
    # 3:上市所
    def get_company_code(self):
        com_name = self.get_company_name()
        cql1 = f"match(m:公司) where m.name='{com_name}' return m.market"
        cql2 = f"match(m:公司) where m.name='{com_name}' return m.code"
        print(cql1)
        answer_market = self.graph.run(cql1)[0]
        answer_code = self.graph.run(cql2)[0]
        final_answer = com_name + "在" + answer_market + "上市，股票代码是"+answer_code+"。"
        return final_answer
    # 4:公司高管名单
    def get_company_em(self):
        com_name=self.get_company_name()
        cql1 = f"match(n)-[r]->(m:公司) where m.name='{com_name}' return n.name"
        cql2 = f"match(n)-[r]->(m:公司) where m.name='{com_name}' return r.name"
        print(cql1)
        print(cql2)
        answer_peo = self.graph.run(cql1)
        answer_pro = self.graph.run(cql2)
        print("----")
        print(answer_peo)
        print(answer_pro)
        final_answer = com_name + "的管理层结构为：\n"
        for i in range(0,len(answer_peo)):
            final_answer = final_answer+ answer_pro[i]+answer_peo[i]+'；\n'
        final_answer = final_answer[:-2]+'。\n'
        return final_answer
    # 5:职务和公司得到人
    def get_company_peo(self):
        print("------------")
        pro_name = self.get_pro_name()
        com_name = self.get_company_name()
        cql = f"match(n)-[r]->(m:公司) where m.name='{com_name}' and r.name=~ '.*{pro_name}.*' return n.name"
        print(cql)
        answer = self.graph.run(cql)
        print(answer)
        final_answer = com_name+"的"+pro_name+"有：\n"
        for item in answer:
            final_answer = final_answer + item+'，\n'
        final_answer = final_answer[:-2] + '。'
        return final_answer
    # 6:人和公司得到职务
    def get_company_pro(self):
        com_name = self.get_company_name()
        peo_name = self.get_peo_name()
        cql = f"match(n)-[r]->(m:公司) where m.name='{com_name}' and n.name='{peo_name}' return r.name"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = com_name+"的"+peo_name+"担任"+answer+"。"
        return final_answer
    # 7:人员信息
    def get_peo_birth(self):
        peo_name = self.get_peo_name()
        cql = f"match(n:人) where n.name='{peo_name}' return n"
        print(cql)
        answer = self.graph.run(cql)
        length = len(answer)
        final_answer = "一共找到了"+str(length)+"个名为"+peo_name+"的人：\n"
        for item in answer:
            temp = item
            final_answer = final_answer+peo_name+"，性别"+temp['sex']+"，出生于"+temp['year']+"，学历是"+temp['education']+"；\n"
        final_answer = final_answer[:-2]+'。\n'
        return final_answer

    # 8:同上
    def get_peo_edu(self):
        return self.get_peo_birth()

    # 9:同上，但含详细任职信息
    def get_peo_countcompany(self):
        peo_name = self.get_peo_name()
        cql1 = f"match(n:人) where n.name='{peo_name}' return n"
        cql4 = f"match(n:人) where n.name='{peo_name}' return id(n)"
        answer_peo_info = self.graph.run(cql1)
        print(answer_peo_info)
        peo_id = self.graph.run(cql4)
        print(peo_id)
        length = len(answer_peo_info)
        final_answer = "一共找到了" + str(length) + "个名为" + peo_name + "的人：\n"
        for i in range(length):
            item = answer_peo_info[i]
            final_answer = final_answer+peo_name + "，性别" + item['sex'] + "，出生于" + item['year'] + "，学历是" + item['education'] + "，\n"
            get_id = peo_id[i]
            cql2 = f"match(n:人)-[r]-(m) where id(n)={get_id} return r.name"
            cql3 = f"match(n:人)-[r]-(m) where id(n)={get_id} return m.name"
            answer_pro = self.graph.run(cql2)
            print(answer_pro)
            answer_com = self.graph.run(cql3)
            for j in range(len(answer_pro)):
                final_answer = final_answer+"在"+answer_com[j]+"担任"+answer_pro[j]+"，\n"
            final_answer = final_answer[:-2] + '；\n'
        final_answer = final_answer[:-2]+'。\n'
        return final_answer

if __name__ =='__main__':
    graph = Graph("http://localhost:7474", username="neo4j", password="123456")
    com_name = '浦发银行'
    cql = f"match(m:公司) where m.name='{com_name}' return m.establishment_date"
    print(cql)
    answer = graph.run(cql).evaluate()
    final_answer = com_name + "成立于" + answer + "。"
    print(final_answer)
