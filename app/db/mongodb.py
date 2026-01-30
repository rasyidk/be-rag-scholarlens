from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import get_settings

# Database name
DATABASE_NAME = "scholarlens-db"

# Collection names
USERS_COLLECTION = "users"
PROJECTS_COLLECTION = "projects"
DOCUMENTS_COLLECTION = "documents"
CHATS_COLLECTION = "chats"


def get_mongodb_client() -> MongoClient:
    """Create and return a MongoDB client."""
    settings = get_settings()
    client = MongoClient(settings.MONGODB_URI)
    return client


def get_database() -> Database:
    """Get the rag_db database."""
    client = get_mongodb_client()
    return client[DATABASE_NAME]


def get_users_collection() -> Collection:
    """Get the users collection."""
    db = get_database()
    return db[USERS_COLLECTION]


def get_projects_collection() -> Collection:
    """Get the projects collection."""
    db = get_database()
    return db[PROJECTS_COLLECTION]


def get_documents_collection() -> Collection:
    """Get the documents collection."""
    db = get_database()
    return db[DOCUMENTS_COLLECTION]


def get_chats_collection() -> Collection:
    """Get the chats collection."""
    db = get_database()
    return db[CHATS_COLLECTION]


def test_mongodb_connection() -> dict:
    """Test MongoDB connection and return status."""
    try:
        client = get_mongodb_client()
        # The ping command is cheap and does not require auth
        client.admin.command("ping")
        
        # Get server info
        server_info = client.server_info()
        
        return {
            "status": "success",
            "message": "Successfully connected to MongoDB!",
            "server_version": server_info.get("version", "unknown"),
        }
    except ConnectionFailure as e:
        return {
            "status": "error",
            "message": f"Failed to connect to MongoDB: {str(e)}",
        }
    except ServerSelectionTimeoutError as e:
        return {
            "status": "error",
            "message": f"MongoDB server selection timeout: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
        }


def init_collections() -> dict:
    """Initialize collections with indexes."""
    try:
        db = get_database()
        
        # Create users collection with unique email index
        users = db[USERS_COLLECTION]
        users.create_index([("email", ASCENDING)], unique=True)
        
        # Create projects collection with user_id index
        projects = db[PROJECTS_COLLECTION]
        projects.create_index([("user_id", ASCENDING)])
        
        # Create documents collection with project_id index
        documents = db[DOCUMENTS_COLLECTION]
        documents.create_index([("project_id", ASCENDING)])
        
        # Create chats collection with project_id and created_at index
        chats = db[CHATS_COLLECTION]
        chats.create_index([("project_id", ASCENDING), ("created_at", ASCENDING)])
        
        return {
            "status": "success",
            "message": "Collections initialized successfully!",
            "collections": [USERS_COLLECTION, PROJECTS_COLLECTION, DOCUMENTS_COLLECTION, CHATS_COLLECTION],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize collections: {str(e)}",
        }


if __name__ == "__main__":
    result = test_mongodb_connection()
    print(result)
    
    if result["status"] == "success":
        init_result = init_collections()
        print(init_result)
