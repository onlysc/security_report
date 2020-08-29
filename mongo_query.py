from pymongo import MongoClient
from bson.objectid import ObjectId
mongo_client = MongoClient('192.168.6.218', 27017)
dbname = mongo_client['test']
col = mongo_client['test']['colname']
#for name in col.find():
    #print(name)
print(dbname.list_collection_names())
for result in col.find():
    print(result)
#for result in dbname.colname.find({'TRADE_MARKET': '深交所中小板'}):