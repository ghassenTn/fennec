# GraphQL API Example 🦊

A user management API demonstrating GraphQL support in Fennec Framework.

## Features

- ✅ GraphQL queries and mutations
- ✅ Complete CRUD operations
- ✅ Field filtering and selection
- ✅ Input validation
- ✅ Error handling
- ✅ GraphiQL interactive interface
- ✅ Type-safe schema

## Project Structure

```
graphql_api/
├── server.py          # Fennec GraphQL server
└── README.md          # This file
```

## Installation

1. Make sure you have Fennec installed:
```bash
pip install fennec
```

2. Install uvicorn (ASGI server):
```bash
pip install uvicorn
```

## Running the Server

Start the GraphQL API server:

```bash
python server.py
```

The server will start on `http://localhost:8000`

## Accessing the API

### GraphQL Endpoint
- **URL**: `http://localhost:8000/graphql`
- **Methods**: GET, POST
- **Content-Type**: application/json

### GraphiQL Interface
- **URL**: `http://localhost:8000/graphql/graphiql`
- Interactive GraphQL playground
- Auto-completion and documentation
- Query history

## Schema

```graphql
type User {
    id: ID!
    name: String!
    email: String!
    age: Int!
    active: Boolean!
}

type Query {
    user(id: ID!): User
    users: [User!]!
    activeUsers: [User!]!
    usersByAge(minAge: Int, maxAge: Int): [User!]!
}

type Mutation {
    createUser(name: String!, email: String!, age: Int!): User!
    updateUser(id: ID!, name: String, email: String, age: Int, active: Boolean): User!
    deleteUser(id: ID!): Boolean!
    deactivateUser(id: ID!): User!
}
```

## Example Queries

### Get All Users

```graphql
{
  users {
    id
    name
    email
    age
    active
  }
}
```

**Response:**
```json
{
  "data": {
    "users": [
      {
        "id": "1",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 28,
        "active": true
      },
      {
        "id": "2",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "age": 35,
        "active": true
      }
    ]
  }
}
```

### Get Single User

```graphql
{
  user(id: "1") {
    id
    name
    email
  }
}
```

### Get Active Users Only

```graphql
{
  activeUsers {
    id
    name
    email
  }
}
```

### Filter Users by Age

```graphql
{
  usersByAge(minAge: 25, maxAge: 40) {
    id
    name
    age
  }
}
```

## Example Mutations

### Create User

```graphql
mutation {
  createUser(
    name: "John Doe"
    email: "john@example.com"
    age: 30
  ) {
    id
    name
    email
    age
    active
  }
}
```

**Response:**
```json
{
  "data": {
    "createUser": {
      "id": "4",
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30,
      "active": true
    }
  }
}
```

### Update User

```graphql
mutation {
  updateUser(
    id: "1"
    name: "Alice Williams"
    age: 29
  ) {
    id
    name
    email
    age
  }
}
```

### Delete User

```graphql
mutation {
  deleteUser(id: "3")
}
```

**Response:**
```json
{
  "data": {
    "deleteUser": true
  }
}
```

### Deactivate User (Soft Delete)

```graphql
mutation {
  deactivateUser(id: "2") {
    id
    name
    active
  }
}
```

## Using Variables

GraphQL supports variables for dynamic queries:

**Query:**
```graphql
query GetUser($userId: ID!) {
  user(id: $userId) {
    id
    name
    email
  }
}
```

**Variables:**
```json
{
  "userId": "1"
}
```

## Using with cURL

### Query Example

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ users { id name email } }"
  }'
```

### Mutation Example

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createUser(name: \"Jane\", email: \"jane@example.com\", age: 25) { id name } }"
  }'
```

### With Variables

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetUser($id: ID!) { user(id: $id) { name email } }",
    "variables": {"id": "1"}
  }'
```

## Code Walkthrough

### Defining the Schema

```python
from fennec import GraphQLEngine

gql = GraphQLEngine()

schema = """
type User {
    id: ID!
    name: String!
    email: String!
}

type Query {
    users: [User!]!
}
"""

gql.set_schema(schema)
```

### Creating Resolvers

```python
from fennec import query, mutation

@query("users")
async def resolve_users(parent, info):
    return get_all_users()

@mutation("createUser")
async def resolve_create_user(parent, info, name: str, email: str):
    return create_user(name, email)
```

### Adding to Application

```python
from fennec import Application

app = Application(title="My API")
app.add_graphql("/graphql", gql, graphiql=True)
```

## Error Handling

GraphQL errors are returned in a structured format:

```json
{
  "errors": [
    {
      "message": "User with email alice@example.com already exists",
      "path": ["createUser"]
    }
  ]
}
```

## Best Practices

1. **Field Selection**: Only request fields you need
   ```graphql
   { users { id name } }  # Good
   { users { id name email age active } }  # Unnecessary if you don't need all fields
   ```

2. **Use Variables**: Don't hardcode values in queries
   ```graphql
   # Good
   query GetUser($id: ID!) { user(id: $id) { name } }
   
   # Avoid
   query { user(id: "1") { name } }
   ```

3. **Batch Queries**: Fetch related data in one request
   ```graphql
   {
     user(id: "1") { name }
     activeUsers { id name }
   }
   ```

4. **Error Handling**: Always check for errors in response
   ```python
   response = await client.post("/graphql", json={"query": query})
   data = response.json()
   if "errors" in data:
       handle_errors(data["errors"])
   ```

## Advanced Features

### Adding Authentication

```python
from fennec.security import JWTHandler, requires_auth

@query("me")
@requires_auth
async def resolve_me(parent, info):
    # Access authenticated user from context
    user_id = info.request.user_id
    return get_user(user_id)
```

### Database Integration

```python
from fennec.db import DatabaseConnection

@query("users")
async def resolve_users(parent, info):
    db = info.db  # Access from context
    result = await db.execute("SELECT * FROM users")
    return result
```

### Pagination

```python
@query("users")
async def resolve_users(parent, info, limit: int = 10, offset: int = 0):
    return users_db[offset:offset + limit]
```

## Testing

### Using Python

```python
import requests

# Query
response = requests.post(
    "http://localhost:8000/graphql",
    json={"query": "{ users { id name } }"}
)
print(response.json())

# Mutation
response = requests.post(
    "http://localhost:8000/graphql",
    json={
        "query": "mutation { createUser(name: \"Test\", email: \"test@example.com\", age: 25) { id } }"
    }
)
print(response.json())
```

### Using JavaScript

```javascript
async function queryUsers() {
  const response = await fetch('http://localhost:8000/graphql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '{ users { id name email } }'
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

## Production Considerations

1. **Query Complexity Limits**: Prevent expensive queries
2. **Rate Limiting**: Limit requests per user
3. **Caching**: Use DataLoader pattern for N+1 queries
4. **Monitoring**: Log slow queries
5. **Security**: Validate and sanitize all inputs
6. **Database**: Use connection pooling
7. **Pagination**: Always paginate large result sets

## Learn More

- [GraphQL Specification](https://spec.graphql.org/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Fennec Documentation](https://github.com/your-repo/fennec)
