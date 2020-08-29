import requests
import pandas
import time
from pymongo import MongoClient

table_name = ['RPT_DMSK_FN_INCOME', 'RPT_DMSK_FN_CASHFLOW', 'RPT_DMSK_FN_BALANCE', 'RPT_LICO_FN_CPD']
table2db_name = {'RPT_DMSK_FN_INCOME': 'income', 'RPT_DMSK_FN_CASHFLOW': 'cash', 'RPT_DMSK_FN_BALANCE': 'balance', 'RPT_LICO_FN_CPD': 'performance'}
table2sheet_name = {'RPT_DMSK_FN_INCOME': '利润表', 'RPT_DMSK_FN_CASHFLOW': '现金流量表', 'RPT_DMSK_FN_BALANCE': '资产负债表', 'RPT_LICO_FN_CPD': '业绩报表'}
report_date_form = {'RPT_DMSK_FN_INCOME': 'REPORT_DATE', 'RPT_DMSK_FN_CASHFLOW': 'REPORT_DATE', 'RPT_DMSK_FN_BALANCE': 'REPORT_DATE', 'RPT_LICO_FN_CPD': 'REPORTDATE'}

sheet_pages = 0
page_number = 1
total_pages = 1
all_data = []
error_security = []
error_pages = []
mongo_client = MongoClient('192.168.6.218', 27017)
dbname = mongo_client['security']
code_info = mongo_client['security']['codeinfo']
performance_report = mongo_client['security']['performance']
income_statement_report = mongo_client['security']['income']
cash_flow_report = mongo_client['security']['cash']
balance_sheet_report = mongo_client['security']['balance']

def excel_write():
    if sheet_pages == 0:
        write_mode = "w"
    else:
        write_mode = "a"
        sheet_pages += 1
    asset = pandas.DataFrame(all_data)
    writer = pandas.ExcelWriter('股票名称和代码.xlsx', mode=write_mode, engine='openpyxl')
    asset.to_excel(writer, sheet_name='股票代码', startrow=0, startcol=0)
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

for result in code_info.find():
    security_code = result['SECURITY_CODE']
    print("准备获取的股票代码为:", security_code)
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
            print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            if api_request.status_code == 200:
                json_response = api_request.json()
                data_list = json_response['result']['data']
                mongo_client['security'][table2db_name[report_table]].insert_many(data_list)
            else:
                error_security.append(security_code)
                # excel_write()
        else:
            error_pages.append(security_code)
print("Error Security Code's ", table2sheet_name[report_table], error_security)
print("Error! When Getting Security Code's Total Pages, Code Numbers Are:", error_pages)