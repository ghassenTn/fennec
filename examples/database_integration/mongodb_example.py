"""
MongoDB Integration Example

Demonstrates how to integrate MongoDB with Fennec using motor (async MongoDB driver).
"""

from fennec import Application, Router, JSONResponse, HTTPException, Depends
from fennec.db import DatabaseConnection, Repository
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


class MongoDBConnection(DatabaseConnection):
    """MongoDB database connection using motor"""
    
    def __init__(self, connection_string: str, database_name: str = "fennec_db"):
        super().__init__(connection_string)
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Create MongoDB client"""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]
        # Test connection
        await self.client.admin.command('ping')
        print("✓ Connected to MongoDB")
    
    async def disconnect(self):
        """Close MongoDB client"""
        if self.client:
            self.client.close()
            print("✓ Disconnected from MongoDB")
    
    def get_collection(self, name: str):
        """Get collection"""
        return self.db[name]


class UserRepository(Repository):
    """Repository for user operations"""
    
    def __init__(self, db: MongoDBConnection):
        self.db = db
        self.collection = None
    
    def _ensure_collection(self):
        """Ensure collection is initialized"""
        if self.collection is None:
            self.collection = self.db.get_collection("users")
    
    def _serialize(self, doc: dict) -> dict:
        """Convert MongoDB document to JSON-serializable dict"""
        if doc and "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return doc
    
    async def create_indexes(self):
        """Create indexes"""
        self._ensure_collection()
        await self.collection.create_index("email", unique=True)
        await self.collection.create_index("name")
    
    async def get_all(self) -> List[dict]:
        """Get all users"""
        self._ensure_collection()
        cursor = self.collection.find()
        users = await cursor.to_list(length=None)
        return [self._serialize(user) for user in users]
    
    async def get(self, id: str) -> Optional[dict]:
        """Get user by ID"""
        self._ensure_collection()
        try:
            user = await self.collection.find_one({"_id": ObjectId(id)})
            return self._serialize(user) if user else None
        except:
            return None
    
    async def create(self, name: str, email: str, age: int) -> dict:
        """Create new user"""
        self._ensure_collection()
        user_doc = {
            "name": name,
            "email": email,
            "age": age
        }
        result = await self.collection.insert_one(user_doc)
        user_doc["id"] = str(result.inserted_id)
        return user_doc
    
    async def update(self, id: str, name: Optional[str] = None,
                    email: Optional[str] = None, age: Optional[int] = None) -> Optional[dict]:
        """Update user"""
        self._ensure_collection()
        
        # Build update document
        update_doc = {}
        if name is not None:
            update_doc["name"] = name
        if email is not None:
            update_doc["email"] = email
        if age is not None:
            update_doc["age"] = age
        
        if not update_doc:
            return await self.get(id)
        
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": update_doc},
                return_document=True
            )
            return self._serialize(result) if result else None
        except:
            return None
    
    async def delete(self, id: str) -> bool:
        """Delete user"""
        self._ensure_collection()
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except:
            return False
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        self._ensure_collection()
        user = await self.collection.find_one({"email": email})
        return self._serialize(user) if user else None
    
    async def search(self, query_text: str) -> List[dict]:
        """Search users by name or email"""
        self._ensure_collection()
        cursor = self.collection.find({
            "$or": [
                {"name": {"$regex": query_text, "$options": "i"}},
                {"email": {"$regex": query_text, "$options": "i"}}
            ]
        })
        users = await cursor.to_list(length=None)
        return [self._serialize(user) for user in users]
    
    async def find_by_age_range(self, min_age: int, max_age: int) -> List[dict]:
        """Find users by age range"""
        self._ensure_collection()
        cursor = self.collection.find({
            "age": {"$gte": min_age, "$lte": max_age}
        })
        users = await cursor.to_list(length=None)
        return [self._serialize(user) for user in users]
    
    async def count(self) -> int:
        """Count total users"""
        self._ensure_collection()
        return await self.collection.count_documents({})


# Database connection
db = MongoDBConnection(
    "mongodb://localhost:27017",
    database_name="fennec_db"
)

# Repository
user_repo = UserRepository(db)


# Dependency injection
def get_user_repo():
    return user_repo


# Create application
app = Application(title="MongoDB Example")
router = Router(prefix="/api/users")


@app.middleware("http")
async def db_middleware(request, call_next):
    """Ensure database is connected"""
    if not db.client:
        await db.connect()
        await user_repo.create_indexes()
    
    response = await call_next(request)
    return response


@router.get("/")
async def get_users(repo: UserRepository = Depends(get_user_repo)):
    """Get all users"""
    users = await repo.get_all()
    return JSONResponse(data=users)


@router.get("/count")
async def count_users(repo: UserRepository = Depends(get_user_repo)):
    """Get user count"""
    count = await repo.count()
    return JSONResponse(data={"count": count})


@router.get("/{user_id}")
async def get_user(user_id: str, repo: UserRepository = Depends(get_user_repo)):
    """Get user by ID"""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data=user)


@router.post("/")
async def create_user(name: str, email: str, age: int,
                     repo: UserRepository = Depends(get_user_repo)):
    """Create new user"""
    # Check if email exists
    existing = await repo.find_by_email(email)
    if existing:
        raise HTTPException(400, f"Email {email} already exists")
    
    user = await repo.create(name, email, age)
    return JSONResponse(data=user, status_code=201)


@router.put("/{user_id}")
async def update_user(user_id: str, name: Optional[str] = None,
                     email: Optional[str] = None, age: Optional[int] = None,
                     repo: UserRepository = Depends(get_user_repo)):
    """Update user"""
    user = await repo.update(user_id, name, email, age)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data=user)


@router.delete("/{user_id}")
async def delete_user(user_id: str, repo: UserRepository = Depends(get_user_repo)):
    """Delete user"""
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(404, f"User {user_id} not found")
    return JSONResponse(data={"message": "User deleted"})


@router.get("/search/{query}")
async def search_users(query: str, repo: UserRepository = Depends(get_user_repo)):
    """Search users"""
    users = await repo.search(query)
    return JSONResponse(data=users)


@router.get("/age/{min_age}/{max_age}")
async def find_by_age(min_age: int, max_age: int,
                     repo: UserRepository = Depends(get_user_repo)):
    """Find users by age range"""
    users = await repo.find_by_age_range(min_age, max_age)
    return JSONResponse(data=users)


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Fennec + MongoDB Example")
    print("=" * 50)
    print("Make sure MongoDB is running:")
    print("  docker run -d -p 27017:27017 mongo")
    print("\nOr update connection string in code")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
