from fastmcp import FastMCP
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Any, Dict, List, Optional
import json
import os
import sys

# Initialize FastMCP server
mcp = FastMCP("MongoDB MCP Server")

# Global MongoDB client
mongo_client: Optional[MongoClient] = None
current_db: Optional[str] = None


def auto_connect_from_env():
    """
    Automatically connect to MongoDB if connection details are provided via environment variables or headers.
    Checks both environment variables and special header-like env vars (X_MONGODB_URI, X_MONGODB_DATABASE).
    """
    global mongo_client, current_db
    
    # Try standard environment variables first
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_database = os.getenv("MONGODB_DATABASE")
    
    # If not found, try header-style environment variables (headers are often passed as env vars in MCP)
    if not mongodb_uri:
        mongodb_uri = os.getenv("X_MONGODB_URI") or os.getenv("X-MONGODB-URI")
    if not mongodb_database:
        mongodb_database = os.getenv("X_MONGODB_DATABASE") or os.getenv("X-MONGODB-DATABASE")
    
    if mongodb_uri and mongodb_database:
        try:
            mongo_client = MongoClient(mongodb_uri)
            current_db = mongodb_database
            # Test connection
            mongo_client.admin.command('ping')
            print(f"Auto-connected to MongoDB database: {mongodb_database}", file=sys.stderr)
        except PyMongoError as e:
            print(f"Auto-connect failed: {str(e)}", file=sys.stderr)
            mongo_client = None
            current_db = None


# Auto-connect on startup
auto_connect_from_env()


@mcp.tool()
def connect_mongodb(
    connection_string: str,
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: str = "localhost",
    port: int = 27017
) -> str:
    """
    Connect to MongoDB database.
    
    Args:
        connection_string: Full MongoDB connection string (e.g., mongodb://localhost:27017/)
                          If provided, other connection params are ignored
        database: Database name to use
        username: MongoDB username (optional)
        password: MongoDB password (optional)
        host: MongoDB host (default: localhost)
        port: MongoDB port (default: 27017)
    
    Returns:
        Connection status message
    """
    global mongo_client, current_db
    
    try:
        # Close existing connection if any
        if mongo_client:
            mongo_client.close()
        
        # Build connection string if not provided
        if not connection_string:
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
            else:
                connection_string = f"mongodb://{host}:{port}/"
        
        # Connect to MongoDB
        mongo_client = MongoClient(connection_string)
        current_db = database
        
        # Test connection
        mongo_client.admin.command('ping')
        
        return f"Successfully connected to MongoDB database: {database}"
    
    except PyMongoError as e:
        return f"Failed to connect to MongoDB: {str(e)}"


@mcp.tool()
def create_document(
    collection: str,
    document: str
) -> str:
    """
    Insert a new document into a collection.
    
    Args:
        collection: Collection name
        document: JSON string of the document to insert
    
    Returns:
        Inserted document ID or error message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        # Parse JSON document
        doc = json.loads(document)
        
        # Insert document
        db = mongo_client[current_db]
        result = db[collection].insert_one(doc)
        
        return f"Document inserted successfully with ID: {str(result.inserted_id)}"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for document"
    except PyMongoError as e:
        return f"Error inserting document: {str(e)}"


@mcp.tool()
def read_documents(
    collection: str,
    query: str = "{}",
    limit: int = 10
) -> str:
    """
    Read documents from a collection.
    
    Args:
        collection: Collection name
        query: JSON string of MongoDB query filter (default: {} for all documents)
        limit: Maximum number of documents to return (default: 10)
    
    Returns:
        JSON string of matching documents or error message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        # Parse query
        query_filter = json.loads(query)
        
        # Find documents
        db = mongo_client[current_db]
        cursor = db[collection].find(query_filter).limit(limit)
        
        # Convert to list and handle ObjectId
        documents = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            documents.append(doc)
        
        return json.dumps(documents, indent=2)
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for query"
    except PyMongoError as e:
        return f"Error reading documents: {str(e)}"


@mcp.tool()
def update_document(
    collection: str,
    query: str,
    update: str,
    update_many: bool = False
) -> str:
    """
    Update document(s) in a collection.
    
    Args:
        collection: Collection name
        query: JSON string of MongoDB query filter to find documents
        update: JSON string of update operations (e.g., {"$set": {"field": "value"}})
        update_many: If True, update all matching documents; if False, update only first match
    
    Returns:
        Update result message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        # Parse query and update
        query_filter = json.loads(query)
        update_doc = json.loads(update)
        
        # Update document(s)
        db = mongo_client[current_db]
        
        if update_many:
            result = db[collection].update_many(query_filter, update_doc)
            return f"Updated {result.modified_count} document(s) successfully"
        else:
            result = db[collection].update_one(query_filter, update_doc)
            return f"Updated {result.modified_count} document successfully"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for query or update"
    except PyMongoError as e:
        return f"Error updating document: {str(e)}"


@mcp.tool()
def delete_document(
    collection: str,
    query: str,
    delete_many: bool = False
) -> str:
    """
    Delete document(s) from a collection.
    
    Args:
        collection: Collection name
        query: JSON string of MongoDB query filter to find documents
        delete_many: If True, delete all matching documents; if False, delete only first match
    
    Returns:
        Delete result message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        # Parse query
        query_filter = json.loads(query)
        
        # Delete document(s)
        db = mongo_client[current_db]
        
        if delete_many:
            result = db[collection].delete_many(query_filter)
            return f"Deleted {result.deleted_count} document(s) successfully"
        else:
            result = db[collection].delete_one(query_filter)
            return f"Deleted {result.deleted_count} document successfully"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for query"
    except PyMongoError as e:
        return f"Error deleting document: {str(e)}"


@mcp.tool()
def list_collections() -> str:
    """
    List all collections in the current database.
    
    Returns:
        JSON string of collection names or error message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        db = mongo_client[current_db]
        collections = db.list_collection_names()
        
        return json.dumps({"collections": collections}, indent=2)
    
    except PyMongoError as e:
        return f"Error listing collections: {str(e)}"


@mcp.tool()
def count_documents(
    collection: str,
    query: str = "{}"
) -> str:
    """
    Count documents in a collection matching a query.
    
    Args:
        collection: Collection name
        query: JSON string of MongoDB query filter (default: {} for all documents)
    
    Returns:
        Document count or error message
    """
    global mongo_client, current_db
    
    if not mongo_client or not current_db:
        return "Error: Not connected to MongoDB. Use connect_mongodb first."
    
    try:
        # Parse query
        query_filter = json.loads(query)
        
        # Count documents
        db = mongo_client[current_db]
        count = db[collection].count_documents(query_filter)
        
        return f"Document count: {count}"
    
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for query"
    except PyMongoError as e:
        return f"Error counting documents: {str(e)}"


# Get port from environment variable for Railway deployment
PORT = int(os.getenv("PORT", 8000))


if __name__ == "__main__":
    # Run the MCP server with Railway port support
    # Bind to 0.0.0.0 to accept external connections on Railway
    mcp.run(transport="sse", host="0.0.0.0", port=PORT)
