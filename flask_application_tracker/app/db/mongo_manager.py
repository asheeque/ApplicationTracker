from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
import os


uri= os.getenv("DATABASE_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['mydatabase']
users_collection = db['users']
users_collection.create_index("user_id", unique=True)

def test_connection():
    """Function to test MongoDB connection."""
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

# Initialize the connection upon import
test_connection()


def add_or_update_user_token(data):
    """Function to add a user to the database or update the googleToken if the user exists."""
    try:
        # Attempt to insert the user
        users_collection.insert_one(data)
    except DuplicateKeyError:
        # The user already exists, so update the googleToken
        users_collection.update_one({"user_id": data["user_id"]}, {"$set": {"googleToken": data["googleToken"]}})

def fetch_google_token(user_id):
    """Function to fetch the googleToken for a given user_id."""
    user = users_collection.find_one({"user_id": user_id})
    
    if user and "googleToken" in user:
        return user["googleToken"]
    else:
        return None