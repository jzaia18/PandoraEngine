from pandorasengine import app
import pymongo

if __name__ == "__main__":
    app.client = pymongo.MongoClient("mongodb+srv://admin:pass@cluster0.idxdfmn.mongodb.net/?retryWrites=true&w=majority")
    app.run()
