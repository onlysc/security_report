import requests
import pandas
import time
import math
from pymongo import MongoClient

table2db_name = {'RPT_DMSK_FN_INCOME': 'income', 'RPT_DMSK_FN_CASHFLOW': 'cash', 'RPT_DMSK_FN_BALANCE': 'balance', 'RPT_LICO_FN_CPD': 'performance'}
table2sheet_name = {'RPT_DMSK_FN_INCOME': '利润表', 'RPT_DMSK_FN_CASHFLOW': '现金流量表', 'RPT_DMSK_FN_BALANCE': '资产负债表', 'RPT_LICO_FN_CPD': '业绩报表'}

sheet_pages = 0
page_number = 1
total_pages = 1
all_data = []
error_security = []
error_pages = []
mongo_client = MongoClient('192.168.6.218', 27017)
dbname = mongo_client['security']
code_info = dbname['codeinfo']
performance_report = dbname['performance']
income_statement_report = dbname['income']
cash_flow_report = dbname['cash']
balance_sheet_report = dbname['balance']

def excel_write(filename, sheetname, all_data_v):
    # if sheet_pages == 0:
    write_mode = "w"
    # else:
    #     write_mode = "a"
    #     sheet_pages += 1
    asset = pandas.DataFrame(all_data_v)
    writer = pandas.ExcelWriter(filename, mode=write_mode, engine='openpyxl')
    asset.to_excel(writer, sheet_name=sheetname, startrow=0, startcol=0)
    writer.save()
    writer.close()

def get_security_info(page_number):
    url = "http://datacenter.eastmoney.com/api/data/get?type=" + table_name[3] + "&sty=ALL&p=1&ps=50&st=UPDATE_DATE,SECURITY_CODE&sr=-1,-1&filter=(SECURITY_TYPE_CODE=%22058001001%22)(REPORTDATE=%272019-12-31%27)"
    api_request = requests.get(url)
    if api_request.status_code == 200:
        print(api_request.status_code)
        json_response = api_request.json()
        if page_number == 1:
            total_pages = json_response['result']['pages']
            print("Total pages:", total_pages)
            #all_data = json_response['result']['data']
    for page_number in range(1, total_pages + 1):
        url = "http://datacenter.eastmoney.com/api/data/get?type=" + table_name[3] + "&sty=ALL&p=" + str(page_number) + "&ps=50&st=UPDATE_DATE,SECURITY_CODE&sr=-1,-1&filter=(SECURITY_TYPE_CODE=%22058001001%22)(REPORTDATE=%272019-12-31%27)"
        api_request = requests.get(url)
        if api_request.status_code == 200:
            json_response = api_request.json()
            #data_list = json_response['result']['data']
            code_info.insert_many(json_response['result']['data'])
            #all_data = all_data + data_list
            time.sleep(5)
            print(page_number)
            print(url)
        else:
            error_pages.append(page_number)
    print("Error Pages:", error_pages)

def data_check(response):
    if type(response['result']) is None:
        return False
    elif type(response['result']) is dict:
        return True
    else:
        print("Unknow Type of return data.")

#get_security_info(page_number)
#该函数从财务简报API中获得所有A股股票基本数据，主要目的得到股票代码
def check_dup(sec_dbpage_nums_v, dbname_v): #TODO make this finished #检查数据库内文档完全重复的条目，并删除重复多余的条目
    collections_list = ['income', 'cash', 'balance', 'performance']
    code_info = dbname_v['codeinfo']
    excel_dupfile_name = 'dup_doc.xlsx'
    all_data = []
    for i in range(0, sec_dbpage_nums_v):
        with code_info.find({'$and':[{'num':{'$exists':True}}, {'num':{'$gte':(i*101), '$lte':((i+1)*101)}}]}, no_cursor_timeout = True) as cursor:
            for result in cursor:
                security_code = result['SECURITY_CODE']
                print(security_code)
                for collection_name in collections_list:
                    dup_info_cursor = dbname_v[collection_name].aggregate([{'$match':{'SECURITY_CODE':security_code}}, {'$group':{'_id':'$REPORT_DATE', 'INDEX':{'$push':'$_id'}, 'count':{'$sum':1}}}])
                    #注意业绩报表的报告日期条目REPORT_DATE、REPORTDATE！！！！！
                    for dup_info in dup_info_cursor:
                        if dup_info['count'] > 1:
                            dup_info['col'] = collection_name
                            print(dup_info)
                            all_data.append(dup_info)
    excel_write(excel_dupfile_name, '重复文档列表', all_data)

def update_db():
    i = 0
    for document in code_info.find():
        document['num'] = i
        print("已添加股票代码的索引:", document['SECURITY_CODE'], i)
        time.sleep(10)
        i += 1

def get_finace_report(sec_dbpage_nums_v, dbname_v, table2db_name_v):
    table_name = ['RPT_DMSK_FN_INCOME', 'RPT_DMSK_FN_CASHFLOW', 'RPT_DMSK_FN_BALANCE', 'RPT_LICO_FN_CPD']
    report_date_form = {'RPT_DMSK_FN_INCOME': 'REPORT_DATE', 'RPT_DMSK_FN_CASHFLOW': 'REPORT_DATE', 'RPT_DMSK_FN_BALANCE': 'REPORT_DATE', 'RPT_LICO_FN_CPD': 'REPORTDATE'}
    code_info = dbname_v['codeinfo']
    for i in range(0, sec_dbpage_nums_v):
        with code_info.find({'$and':[{'num':{'$exists':True}}, {'num':{'$gte':(i*101), '$lte':((i+1)*101)}}]}, no_cursor_timeout = True) as cursor:
            for result in cursor:
                security_code = result['SECURITY_CODE']
                index = int(result['num'])
                print("准备获取的股票代码/索引号/循环号为:", security_code, index, i)
                for report_table in table_name:
                    url = "http://datacenter.eastmoney.com/api/data/get?type=" + report_table + "&sty=ALL&p=1&ps=1&st=" + report_date_form[report_table] + "&sr=1&filter=(SECURITY_CODE=%22" + security_code + "%22)"
                    print("准备获取股票的", table2sheet_name[report_table])
                    print("获取股票财报链接总页数,链接:", url)
                    items_num_request = requests.get(url)
                    time.sleep(5)
                    if items_num_request.status_code == 200:
                        items_num_response = items_num_request.json()
                        if data_check(items_num_response):
                            print('已成功获取报表数据:', table2sheet_name[report_table])
                        else:
                            continue
                        total_pages = items_num_response['result']['pages']
                        print("已经获取到的股票财报条目数:", total_pages)
                        url = "http://datacenter.eastmoney.com/api/data/get?type=" + report_table + "&sty=ALL&p=1&ps=" + str(total_pages) + "&st=" + report_date_form[report_table] + "&sr=1&filter=(SECURITY_CODE=%22" + security_code + "%22)"
                        print("获取财报信息,链接:", url)
                        api_request = requests.get(url)
                        time.sleep(5)
                        if api_request.status_code == 200:
                            json_response = api_request.json()
                            data_list = json_response['result']['data']
                            dbname_v[table2db_name_v[report_table]].insert_many(data_list)
                            print("数据库写入完成，股票代码&报表类别为：", security_code, [table2db_name_v[report_table]])
                        else:
                            error_security.append(security_code)
                            # excel_write()
                    else:
                        error_pages.append(security_code)
                print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Error Security Code's ", table2sheet_name[report_table], error_security)
    print("Error! When Getting Security Code's Total Pages, Code Numbers Are:", error_pages)

sec_db_nums = code_info.count_documents({})
print(sec_db_nums)
sec_dbpage_nums = math.ceil(sec_db_nums/101) + 1
check_dup(sec_dbpage_nums, dbname)
#取得股票数量后向上取整，mongodb的游标101限制，需要分页取回数据
#update_db()
#get_finace_report(sec_dbpage_nums, dbname, table2db_name)