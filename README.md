# MongoDB MCP Server

A custom Model Context Protocol (MCP) server for MongoDB operations, providing CRUD functionality and database management tools.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Available Tools

### 1. connect_mongodb
Connect to a MongoDB database.

**Parameters:**
- `connection_string` (str): Full MongoDB connection string (e.g., `mongodb://localhost:27017/`)
- `database` (str): Database name to use
- `username` (str, optional): MongoDB username
- `password` (str, optional): MongoDB password
- `host` (str, optional): MongoDB host (default: localhost)
- `port` (int, optional): MongoDB port (default: 27017)

**Example:**
```json
{
  "connection_string": "mongodb://localhost:27017/",
  "database": "mydb"
}
```

### 2. create_document
Insert a new document into a collection.

**Parameters:**
- `collection` (str): Collection name
- `document` (str): JSON string of the document to insert

**Example:**
```json
{
  "collection": "users",
  "document": "{\"name\": \"John Doe\", \"email\": \"john@example.com\", \"age\": 30}"
}
```

### 3. read_documents
Read documents from a collection.

**Parameters:**
- `collection` (str): Collection name
- `query` (str, optional): JSON string of MongoDB query filter (default: `{}`)
- `limit` (int, optional): Maximum number of documents to return (default: 10)

**Example:**
```json
{
  "collection": "users",
  "query": "{\"age\": {\"$gte\": 25}}",
  "limit": 5
}
```

### 4. update_document
Update document(s) in a collection.

**Parameters:**
- `collection` (str): Collection name
- `query` (str): JSON string of MongoDB query filter
- `update` (str): JSON string of update operations
- `update_many` (bool, optional): Update all matching documents (default: false)

**Example:**
```json
{
  "collection": "users",
  "query": "{\"name\": \"John Doe\"}",
  "update": "{\"$set\": {\"age\": 31}}",
  "update_many": false
}
```

### 5. delete_document
Delete document(s) from a collection.

**Parameters:**
- `collection` (str): Collection name
- `query` (str): JSON string of MongoDB query filter
- `delete_many` (bool, optional): Delete all matching documents (default: false)

**Example:**
```json
{
  "collection": "users",
  "query": "{\"age\": {\"$lt\": 18}}",
  "delete_many": true
}
```

### 6. list_collections
List all collections in the current database.

**Example:**
```json
{}
```

### 7. count_documents
Count documents in a collection matching a query.

**Parameters:**
- `collection` (str): Collection name
- `query` (str, optional): JSON string of MongoDB query filter (default: `{}`)

**Example:**
```json
{
  "collection": "users",
  "query": "{\"age\": {\"$gte\": 18}}"
}
```

## Usage

### Local Development

```bash
python custom-mcp/mongomcp.py
```


Then call `connect_mongodb` with your credentials when needed.

## Architecture: Flexible Configuration

This MCP server supports **two configuration approaches**:

### Approach 1: Environment Variables (Recommended)

Pass MongoDB credentials through the MCP client JSON configuration using the `env` field:

```json
{
  "mcpServers": {
    "mongodb": {
      "url": "https://your-app.up.railway.app",
      "transport": "sse",
      "env": {
        "MONGODB_URI": "mongodb+srv://user:pass@cluster.mongodb.net/",
        "MONGODB_DATABASE": "mydb"
      }
    }
  }
}
```

**Benefits:**
- ✅ Automatic connection on startup
- ✅ No need to call `connect_mongodb` tool
- ✅ Credentials in client config, not on server
- ✅ Simple and straightforward
- ✅ Perfect for single database usage

### Approach 2: Manual Connection via Tool

Configure without credentials and use the `connect_mongodb` tool when needed:

```json
{
  "mcpServers": {
    "mongodb": {
      "url": "https://your-app.up.railway.app",
      "transport": "sse"
    }
  }
}
```

**Benefits:**
- ✅ Flexible for switching between databases
- ✅ Good for multi-database workflows
- ✅ Connect/disconnect as needed

### Multi-Tenancy Architecture

One deployed server can serve multiple users with different databases:

```
User A (env: DB_A) → Railway MCP Server → MongoDB Atlas (DB_A)
User B (env: DB_B) → Railway MCP Server → Local MongoDB (DB_B)
User C (env: DB_C) → Railway MCP Server → Self-hosted MongoDB (DB_C)
```

**Key Points:**
1. Deploy once to Railway (no credentials on server)
2. Each client passes their own MongoDB credentials via `env` in config
3. Credentials never stored on Railway
4. Complete privacy and security

## Future Enhancements

This MCP server is designed to be extensible. You can easily add more tools for:
- Aggregation pipelines
- Index management
- Bulk operations
- Transaction support
- Database administration
- Backup and restore operations

## Error Handling

All tools include comprehensive error handling and will return descriptive error messages for:
- Connection failures
- Invalid JSON format
- MongoDB operation errors
- Missing connection state

## Requirements

- Python 3.7+
- fastmcp
- pymongo
