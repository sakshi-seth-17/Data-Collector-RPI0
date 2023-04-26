import json
import sqlite3


def readJson(filename):
    try:
        data = open(filename,"r")
        data = json.loads(data.read())
        return data
    except Exception as e:
        print("Error: ", e)
        return ""

def writeJson(path, newdata):
    try:
        with open(path,"w") as config:
            json.dump(newdata,config)
        return 1
    except :
        return 0
        

def saveSqlite(query):
    try:
        conn = sqlite3.connect("/home/sonya-cummings/DataCollector/data.db")
        conn.execute(query)
        conn.commit()
        conn.close()
        return 1
    except:
        return 0