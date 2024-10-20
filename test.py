from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_mongodb_connection(uri):
    try:
        client = MongoClient(uri)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful")
    except ConnectionFailure:
        print("MongoDB connection failed")

if __name__ == "__main__":
    # Replace 'your_mongodb_uri' with your actual MongoDB URI
    uri = 'mongodb://localhost:27017'
    test_mongodb_connection(uri)