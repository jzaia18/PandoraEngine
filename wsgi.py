from pandorasengine import app
import pymongo

app.client = pymongo.MongoClient("mongodb+srv://admin:pass@cluster0.idxdfmn.mongodb.net/?retryWrites=true&w=majority")
app.rooms = dict()
if __name__ == "__main__":
    app.run()
