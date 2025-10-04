# Fennec Framework 🦊 - GUI Client Summary

## What's New?

A complete **Tkinter GUI client** has been added to interact with the Fennec API!

## Features

### ✅ Complete User Management
- View all users in a beautiful table
- Create new users with validation
- Edit existing users
- Delete users
- Real-time updates

### ✅ Authentication System
- Login with email/password
- JWT token management
- Secure logout
- User info display with role

### ✅ Admin Panel
- Admin-only features
- View all users (including hidden data)
- Admin delete functionality
- Role-based access control

### ✅ Beautiful UI
- Fennec branding colors (Gold, Desert Sand)
- Clean, modern design
- Tabbed interface (Users, Add User, Admin)
- Status bar with real-time feedback
- Responsive layout

## Quick Start

### Method 1: Run Together (Recommended)

```bash
./run_with_gui.sh
```

This script:
1. Starts the API server in background
2. Waits for API to be ready
3. Launches the GUI client
4. Stops API when GUI closes

### Method 2: Run Separately

```bash
# Terminal 1: Start API
python main.py

# Terminal 2: Start GUI
python gui_client.py
```

## Default Login

```
Email: admin@fennec.dev
Password: admin123
```

## GUI Structure

```
┌─────────────────────────────────────────────────────────┐
│           🦊 Fennec Framework - API Client              │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│ Login Panel  │  Tab 1: 👥 Users List                   │
│              │  - View all users in table              │
│ Email:       │  - Refresh, Edit, Delete buttons        │
│ [________]   │                                          │
│              │  Tab 2: ➕ Add User                      │
│ Password:    │  - Form: Name, Email, Age               │
│ [________]   │  - Save/Clear buttons                   │
│              │                                          │
│ [Login]      │  Tab 3: 🔒 Admin Panel                  │
│              │  - Admin-only user list                 │
│              │  - Admin delete functionality           │
│              │                                          │
│ API Status   │                                          │
└──────────────┴──────────────────────────────────────────┘
│ Status: ✓ Connected to API                              │
└─────────────────────────────────────────────────────────┘
```

## Files Created

### 1. `gui_client.py` (Main GUI Application)
- **FennecAPIClient**: API client class with all endpoints
- **FennecGUI**: Main GUI application with Tkinter
- ~600 lines of well-documented code

### 2. `GUI_CLIENT_GUIDE.md`
- Complete usage guide
- Screenshots and examples
- Troubleshooting section
- Development guide

### 3. `run_with_gui.sh`
- Convenience script to run API + GUI together
- Automatic startup and cleanup

### 4. `GUI_SUMMARY.md`
- This file - quick overview

## API Endpoints Used

The GUI connects to all major API endpoints:

### Public
- `GET /health` - Check API status
- `GET /users` - List users
- `GET /users/{id}` - Get user
- `POST /users` - Create user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Authentication
- `POST /auth/login` - Login and get JWT
- `GET /auth/me` - Get current user info

### Admin
- `GET /admin/users` - List all users (admin only)
- `DELETE /admin/users/{id}` - Delete user (admin only)

## Features Demonstrated

### 1. API Integration
- RESTful API calls with `requests`
- JWT token management
- Error handling
- Status feedback

### 2. Authentication Flow
- Login form
- Token storage
- Authenticated requests
- Logout functionality

### 3. CRUD Operations
- **Create**: Add new users
- **Read**: View users list
- **Update**: Edit user details
- **Delete**: Remove users

### 4. Role-Based Access
- Public endpoints (no auth)
- Protected endpoints (requires auth)
- Admin endpoints (requires admin role)

### 5. User Experience
- Real-time status updates
- Error messages
- Success confirmations
- Loading indicators

## Code Highlights

### Clean API Client

```python
class FennecAPIClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
    
    def login(self, email, password):
        response = requests.post(f"{self.base_url}/auth/login", ...)
        self.token = response.json()["data"]["access_token"]
    
    def get_users(self):
        response = requests.get(
            f"{self.base_url}/users",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()["data"]["users"]
```

### Beautiful UI

```python
# Fennec branding colors
self.colors = {
    "primary": "#D4A574",    # Fennec Gold
    "secondary": "#E8D5B7",  # Desert Sand
    "accent": "#E89B5A",     # Sahara Orange
    "success": "#27AE60",    # Success Green
    "error": "#E74C3C"       # Error Red
}
```

### Event Handling

```python
def login(self):
    try:
        data = self.api.login(email, password)
        self.update_ui_after_login(data)
        messagebox.showinfo("Success", "Welcome!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
```

## Testing the GUI

### 1. Start Everything

```bash
./run_with_gui.sh
```

### 2. Login
- Use default credentials
- Click "Login"

### 3. View Users
- Go to "Users" tab
- Click "Refresh"
- See all users

### 4. Create User
- Go to "Add User" tab
- Fill form:
  - Name: "Test User"
  - Email: "test@example.com"
  - Age: 25
- Click "Save User"
- Check console for "Welcome email sent" message

### 5. Edit User
- Select user from table
- Click "Edit"
- Modify details
- Click "Update User"

### 6. Delete User
- Select user
- Click "Delete"
- Confirm

### 7. Admin Panel
- Go to "Admin" tab
- Click "Refresh"
- See all users (admin view)
- Try admin delete

## Dependencies

```bash
# Built-in (no installation needed)
- tkinter (usually included with Python)

# External (install with pip)
pip install requests
```

## Platform Support

- ✅ **Linux**: Full support
- ✅ **macOS**: Full support
- ✅ **Windows**: Full support

Tkinter is cross-platform and works everywhere!

## Advantages

### 1. No Browser Needed
- Desktop application
- Native look and feel
- Faster than web UI

### 2. Easy to Use
- Familiar desktop interface
- Clear navigation
- Intuitive controls

### 3. Complete Integration
- All API features accessible
- Real-time updates
- Error handling

### 4. Educational
- Shows how to build API clients
- Demonstrates authentication
- Good example of Tkinter usage

## Comparison

### Swagger UI (Web)
- ✅ Auto-generated
- ✅ Interactive
- ❌ Requires browser
- ❌ Less user-friendly

### GUI Client (Desktop)
- ✅ Native application
- ✅ User-friendly interface
- ✅ Better UX
- ✅ Custom features
- ❌ Requires separate development

## Use Cases

### 1. Development
- Test API during development
- Quick user management
- Debug authentication

### 2. Administration
- Manage users
- Monitor system
- Admin operations

### 3. Demo
- Show API capabilities
- Interactive presentation
- Client example

### 4. Learning
- Learn API integration
- Study Tkinter
- Understand authentication

## Next Steps

### For Users
1. Run the GUI: `./run_with_gui.sh`
2. Login and explore
3. Try all features
4. Provide feedback

### For Developers
1. Study the code
2. Add new features
3. Customize UI
4. Integrate with your API

## Possible Enhancements

Future additions:
- [ ] Search/filter users
- [ ] Pagination
- [ ] User avatars
- [ ] Export to CSV
- [ ] Dark mode
- [ ] Settings panel
- [ ] Statistics dashboard
- [ ] Real-time updates (WebSocket)
- [ ] Multi-language support
- [ ] Keyboard shortcuts

## Troubleshooting

### GUI doesn't start
```bash
# Install tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk
```

### API connection error
```bash
# Make sure API is running
python main.py
```

### Login fails
- Check credentials
- Verify API is running
- Check API logs

## Resources

- [GUI Client Guide](GUI_CLIENT_GUIDE.md) - Complete guide
- [Example Guide](EXAMPLE_GUIDE.md) - API documentation
- [Main README](README.md) - Framework documentation

---

<div align="center">
  <h2>🦊 Fennec Framework 🦊</h2>
  <p><strong>Small, Swift, and Adaptable</strong></p>
  <p>Now with a complete GUI client!</p>
  <br>
  <p>Built with ❤️ in Tunisia 🇹🇳</p>
</div>

---

**What's Included:**
- ✅ Complete Tkinter GUI (~600 lines)
- ✅ Full API integration
- ✅ Authentication system
- ✅ Admin panel
- ✅ Beautiful UI with Fennec branding
- ✅ Comprehensive documentation
- ✅ Easy to run script
- ✅ Cross-platform support

**Ready to use, easy to customize!** 🚀
