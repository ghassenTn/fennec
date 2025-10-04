# Import Changes - Fennec Framework 🦊

## What Changed?

The package name has been changed from `framework` to `fennec` for cleaner, more intuitive imports.

## Before ❌

```python
from framework import Application, Router, JSONResponse
from framework.validation import BaseModel, Field
from framework.dependencies import Depends
from framework.security import CORSMiddleware
```

## After ✅

```python
from fennec import Application, Router, JSONResponse
from fennec.validation import BaseModel, Field
from fennec.dependencies import Depends
from fennec.security import CORSMiddleware
```

## Why This Change?

### Better Branding
- `from fennec import` is more memorable
- Matches the framework name
- Cleaner and more professional

### Clearer Identity
- No confusion with generic "framework" name
- Unique and distinctive
- Better for documentation and tutorials

### Easier to Remember
- Short and simple: `fennec`
- Matches the package name: `fennec-framework`
- Consistent branding throughout

## Migration Guide

### For New Projects ✅

Just use the new imports:

```python
from fennec import Application, Router, JSONResponse

app = Application(title="My API")
router = Router()

@router.get("/")
async def root():
    return JSONResponse(data={"message": "Hello from Fennec! 🦊"})

app.include_router(router)
```

### For Existing Projects 🔄

Simply replace all imports:

**Find and Replace:**
- `from framework` → `from fennec`
- `import framework` → `import fennec`

**Example:**

```bash
# Using sed (Linux/Mac)
find . -name "*.py" -exec sed -i 's/from framework/from fennec/g' {} \;

# Or manually in your editor
# Find: from framework
# Replace: from fennec
```

## All Import Patterns

### Main Imports

```python
# Application and routing
from fennec import Application, Router, JSONResponse, Request, Response

# Validation
from fennec.validation import BaseModel, Field

# Dependencies
from fennec.dependencies import Depends

# Middleware
from fennec.middleware import Middleware

# Background tasks
from fennec.background import BackgroundTasks

# Exceptions
from fennec.exceptions import (
    HTTPException,
    NotFoundException,
    ValidationException,
    UnauthorizedException
)
```

### Security Imports

```python
# Authentication
from fennec.security import (
    JWTHandler,
    requires_auth,
    requires_role,
    has_permission
)

# Middleware
from fennec.security import CORSMiddleware, RateLimitMiddleware
```

### Database Imports

```python
from fennec.db import Repository, DatabaseConnection
```

### Testing Imports

```python
from fennec.testing import TestClient
```

### CLI Imports

```python
from fennec.cli import CLI, cli
```

## CLI Commands

### Before ❌
```bash
python -m framework.cli startproject myproject
```

### After ✅
```bash
python -m fennec.cli startproject myproject
```

## Package Installation

The package name remains `fennec-framework`:

```bash
pip install fennec-framework
```

But you import it as `fennec`:

```python
from fennec import Application
```

## Complete Example

### Before ❌

```python
from framework import Application, Router, JSONResponse
from framework.validation import BaseModel, Field
from framework.dependencies import Depends
from framework.security import CORSMiddleware, RateLimitMiddleware

app = Application(title="My API")
app.middleware_manager.add(CORSMiddleware(allow_origins=["*"]))
app.middleware_manager.add(RateLimitMiddleware())

router = Router()

class User(BaseModel):
    name: str = Field(min_length=2)
    email: str
    age: int

def get_db():
    return {}

@router.post("/users")
async def create_user(request, db=Depends(get_db)):
    data = await request.json()
    user = User(**data)
    return JSONResponse(data=user.dict(), status_code=201)

app.include_router(router)
```

### After ✅

```python
from fennec import Application, Router, JSONResponse
from fennec.validation import BaseModel, Field
from fennec.dependencies import Depends
from fennec.security import CORSMiddleware, RateLimitMiddleware

app = Application(title="My API")
app.middleware_manager.add(CORSMiddleware(allow_origins=["*"]))
app.middleware_manager.add(RateLimitMiddleware())

router = Router()

class User(BaseModel):
    name: str = Field(min_length=2)
    email: str
    age: int

def get_db():
    return {}

@router.post("/users")
async def create_user(request, db=Depends(get_db)):
    data = await request.json()
    user = User(**data)
    return JSONResponse(data=user.dict(), status_code=201)

app.include_router(router)
```

## Benefits

### 1. Cleaner Code ✨
```python
# Before
from framework import Application

# After - cleaner!
from fennec import Application
```

### 2. Better Branding 🦊
```python
# Matches the framework name
from fennec import Application  # Fennec Framework!
```

### 3. Easier to Type ⌨️
```python
# Shorter and simpler
from fennec import ...  # vs from framework import ...
```

### 4. More Professional 💼
```python
# Unique identity
from fennec import Application  # Clear what framework you're using
```

### 5. Better Documentation 📚
```python
# Easier to search and reference
from fennec import Application  # Google "fennec python" = clear results
```

## FAQ

### Q: Do I need to reinstall?
**A:** No! The package name is still `fennec-framework`. Only the import changed.

### Q: Will old code break?
**A:** Yes, you need to update imports from `framework` to `fennec`.

### Q: How long does migration take?
**A:** Usually 1-2 minutes with find & replace.

### Q: Can I use both?
**A:** No, choose one. We recommend `fennec` (new way).

### Q: What about examples?
**A:** All examples and documentation updated to use `fennec`.

## Testing Your Migration

After updating imports, run:

```bash
# Test your application
python test_framework.py

# Or run your app
python main.py
```

You should see:
```
🦊 Fennec Framework is working perfectly!
```

## Summary

**Old Way:**
```python
from framework import Application
```

**New Way:**
```python
from fennec import Application  # 🦊
```

**Why:** Cleaner, more memorable, better branding!

---

<div align="center">
  <strong>🦊 Fennec Framework 🦊</strong><br>
  Small, Swift, and Adaptable<br><br>
  Now with cleaner imports!
</div>
