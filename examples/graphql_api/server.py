"""
GraphQL API Example

A user management API demonstrating GraphQL support in Fennec.
Features queries, mutations, and a complete CRUD interface.
"""

from fennec import Application, GraphQLEngine, query, mutation
from typing import Optional, List
from dataclasses import dataclass, asdict


# Data models
@dataclass
class User:
    id: int
    name: str
    email: str
    age: int
    active: bool = True


# In-memory database
users_db: List[User] = [
    User(id=1, name="Alice Johnson", email="alice@example.com", age=28),
    User(id=2, name="Bob Smith", email="bob@example.com", age=35),
    User(id=3, name="Charlie Brown", email="charlie@example.com", age=42),
]
next_id = 4


# Create application
app = Application(title="GraphQL User API")

# Create GraphQL engine
gql = GraphQLEngine()

# Define GraphQL schema
schema = """
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
"""

gql.set_schema(schema)


# Query resolvers
@query("user")
async def resolve_user(parent, info, id: str):
    """Get a single user by ID"""
    user_id = int(id)
    for user in users_db:
        if user.id == user_id:
            return asdict(user)
    return None


@query("users")
async def resolve_users(parent, info):
    """Get all users"""
    return [asdict(user) for user in users_db]


@query("activeUsers")
async def resolve_active_users(parent, info):
    """Get all active users"""
    return [asdict(user) for user in users_db if user.active]


@query("usersByAge")
async def resolve_users_by_age(parent, info, minAge: Optional[int] = None, maxAge: Optional[int] = None):
    """Get users filtered by age range"""
    filtered_users = users_db
    
    if minAge is not None:
        filtered_users = [u for u in filtered_users if u.age >= minAge]
    
    if maxAge is not None:
        filtered_users = [u for u in filtered_users if u.age <= maxAge]
    
    return [asdict(user) for user in filtered_users]


# Mutation resolvers
@mutation("createUser")
async def resolve_create_user(parent, info, name: str, email: str, age: int):
    """Create a new user"""
    global next_id
    
    # Check if email already exists
    for user in users_db:
        if user.email == email:
            raise Exception(f"User with email {email} already exists")
    
    # Create new user
    new_user = User(
        id=next_id,
        name=name,
        email=email,
        age=age,
        active=True
    )
    
    users_db.append(new_user)
    next_id += 1
    
    return asdict(new_user)


@mutation("updateUser")
async def resolve_update_user(
    parent,
    info,
    id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    age: Optional[int] = None,
    active: Optional[bool] = None
):
    """Update an existing user"""
    user_id = int(id)
    
    # Find user
    user = None
    for u in users_db:
        if u.id == user_id:
            user = u
            break
    
    if not user:
        raise Exception(f"User with id {id} not found")
    
    # Update fields
    if name is not None:
        user.name = name
    if email is not None:
        # Check if email is taken by another user
        for u in users_db:
            if u.id != user_id and u.email == email:
                raise Exception(f"Email {email} is already taken")
        user.email = email
    if age is not None:
        user.age = age
    if active is not None:
        user.active = active
    
    return asdict(user)


@mutation("deleteUser")
async def resolve_delete_user(parent, info, id: str):
    """Delete a user"""
    global users_db
    user_id = int(id)
    
    # Find and remove user
    for i, user in enumerate(users_db):
        if user.id == user_id:
            users_db.pop(i)
            return True
    
    return False


@mutation("deactivateUser")
async def resolve_deactivate_user(parent, info, id: str):
    """Deactivate a user (soft delete)"""
    user_id = int(id)
    
    # Find user
    for user in users_db:
        if user.id == user_id:
            user.active = False
            return asdict(user)
    
    raise Exception(f"User with id {id} not found")


# Add GraphQL endpoint with GraphiQL interface
app.add_graphql("/graphql", gql, graphiql=True)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Fennec GraphQL API")
    print("=" * 50)
    print("GraphQL endpoint: http://localhost:8000/graphql")
    print("GraphiQL interface: http://localhost:8000/graphql/graphiql")
    print("=" * 50)
    print("\nExample queries:")
    print("\n1. Get all users:")
    print("   { users { id name email age } }")
    print("\n2. Get user by ID:")
    print("   { user(id: \"1\") { id name email } }")
    print("\n3. Create user:")
    print("   mutation { createUser(name: \"John\", email: \"john@example.com\", age: 30) { id name } }")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
