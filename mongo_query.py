from pymongo import MongoClient
import math
from bson.objectid import ObjectId
mongo_client = MongoClient('192.168.6.218', 27017)
dbname = mongo_client['security']
dbname['performance'].update_many({},{'$rename':{'REPORTDATE':'REPORT_DATE'}})
# col = mongo_client['test']['colname']
#for name in col.find():
    #print(name)
# print(dbname.list_collection_names())
# print(mongo_client.server_info())
# count = dbname.codeinfo.count_documents({})
# print(count)
# n = math.ceil(count/101) + 1
# print(n)
# for result in col.find():
#     print(result)
#for result in dbname.colname.find({'TRADE_MARKET': '深交所中小板'}):