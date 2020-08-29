import json
import requests
import pandas

table_name = ['RPT_DMSK_FN_INCOME', 'RPT_DMSK_FN_CASHFLOW', 'RPT_DMSK_FN_BALANCE', 'RPT_LICO_FN_CPD']
table2sheet_name = {'RPT_DMSK_FN_INCOME': '利润表', 'RPT_DMSK_FN_CASHFLOW': '现金流量表', 'RPT_DMSK_FN_BALANCE': '资产负债表', 'RPT_LICO_FN_CPD': '业绩报表'}
report_date_form = {'RPT_DMSK_FN_INCOME': 'REPORT_DATE', 'RPT_DMSK_FN_CASHFLOW': 'REPORT_DATE', 'RPT_DMSK_FN_BALANCE': 'REPORT_DATE', 'RPT_LICO_FN_CPD': 'REPORTDATE'}
sheet_pages = 0

for report_table in table_name:
    url = "http://datacenter.eastmoney.com/api/data/get?type=" + str(report_table) + "&sty=ALL&p=1&ps=1&st=" + report_date_form[report_table] + "&sr=1&filter=(SECURITY_CODE=%22600855%22)"
    #print(url)
    items_num_request = requests.get(url)
    if items_num_request.status_code == 200:
        items_num_response = items_num_request.json()
        total_pages = items_num_response['result']['pages']
        #print(total_pages)
        url = "http://datacenter.eastmoney.com/api/data/get?type=" + report_table + "&sty=ALL&p=1&ps=" + str(total_pages) + "&st=" + report_date_form[report_table] + "&sr=1&filter=(SECURITY_CODE=%22" + str(600855) + "%22)"
        #print(url)
        api_request = requests.get(url)
        if api_request.status_code == 200:
            json_response = api_request.json()
            data_list = json_response['result']['data']
            asset = pandas.DataFrame(data_list)
            if sheet_pages == 0:
                write_mode = "w"
            else:
                write_mode = "a"
            sheet_pages += 1
            #print(sheet_pages)
            writer = pandas.ExcelWriter('600855.xlsx', mode = write_mode, engine = 'openpyxl')
            asset.to_excel(writer, sheet_name=table2sheet_name[report_table], startrow = 0, startcol = 0)
            writer.save()
writer.close()