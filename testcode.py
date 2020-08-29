import requests
#obj={"result": null, "success": false, "message": "返回数据为空", "code": 9201}
url = 'http://datacenter.eastmoney.com/api/data/get?type=RPT_DMSK_FN_CASHFLOW&sty=ALL&p=1&ps=6&st=REPORT_DATE&sr=1&filter=(SECURITY_CODE=%22605009%22)'
response = requests.get(url)
date = response.json()
print(type(date["result"]))
if type(date) is dict:
    print(date["result"])
