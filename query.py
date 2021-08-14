from pymongo import MongoClient
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["hwr_data"]

# Choose a route and a direction
mycol = mydb["docs"]

cursor = mycol.find({})
for document in cursor:
      print(document)


# query = { "$match": { 'Minutes' : { "$gte" : current_time-60, "$lt" : current_time+60 } } }
# mydoc = mycol.aggregate([ query ])
