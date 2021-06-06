'''
爬取数据
两类节点：公司，人；关系为职位
数据来源：巨潮网（http://www.cninfo.com.cn/）
'''

import requests
import json
import csv
import time

def get_executives(code):
    get_company_executives = "http://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives?scode=" + code
    try:
        page = requests.Session().get(get_company_executives)
    except:
        time.sleep(20)
        page = requests.Session().get(get_company_executives)
    while page.status_code == 502:
        time.sleep(50)
        page = requests.Session().get(get_company_executives)
    content = json.loads(page.text)
    if content["code"] == "9240002":
        return None
    executives = content['data']['records']
    modified_executives = []
    for executive in executives:
        item = {}
        item["name"] = executive["F002V"]
        item["sex"] = executive["F010V"]
        item["year"] = executive["F012V"]
        item["education"] = executive["F017V"]
        item["profession"] = executive["F009V"]     # 可能有多个值：执行董事,副行长
        modified_executives.append(item)
    return modified_executives


def get_information(code):
    get_company_introduction = "http://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction?scode=" + code
    try:
        page = requests.Session().get(get_company_introduction)
    except:
        time.sleep(20)
        page = requests.Session().get(get_company_introduction)
    while page.status_code == 502:
        time.sleep(60)
        page = requests.Session().get(get_company_introduction)
    content = json.loads(page.text)
    if content["code"] == "9240002":
        return None
    information = content['data']['records']
    while information[0]["basicInformation"] == None:
        time.sleep(30)
        information = json.loads(requests.Session().get(get_company_introduction).text)['data']['records']
    modified_information = {}
    modified_information["code"] = information[0]["basicInformation"][0]["ASECCODE"]
    modified_information["name"] = information[0]["basicInformation"][0]["ASECNAME"]
    modified_information["market"] = information[0]["basicInformation"][0]["MARKET"]
    modified_information["industry"] = information[0]["basicInformation"][0]["F032V"]
    modified_information["establishment_date"] = information[0]["basicInformation"][0]["F010D"]
    modified_information["address"] = information[0]["basicInformation"][0]["F004V"]
    modified_information["telephone"] = information[0]["basicInformation"][0]["F014V"]
    modified_information["business"] = information[0]["basicInformation"][0]["F015V"]
    return modified_information


if __name__ == '__main__':
    code_arr = []
    with open('name_code.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != '':
                code = row[2]
                if code[0:3] in ["000", "002", "300", "600", "601", "603"]:
                    code_arr.append(code)
    print(code_arr)
    print(len(code_arr))

    result = {}
    for code in code_arr:
        company = {}
        company["information"] = get_information(code)
        company["executives"] = get_executives(code)
        if company["information"] == None or company["executives"] == None:
            continue
        result[code] = company
        print(company)
    with open("result.txt", "w+") as file:
        file.write(str(result))