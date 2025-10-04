# Fennec Framework 🦊 - GUI Client Guide

## Overview

A complete **Tkinter GUI client** for the Fennec API Demo. Beautiful, functional, and easy to use!

## Features

### ✅ User Management
- View all users in a table
- Create new users
- Edit existing users
- Delete users
- Real-time updates

### ✅ Authentication
- Login with email/password
- JWT token management
- Logout functionality
- User info display

### ✅ Admin Panel
- Admin-only user list
- Admin delete functionality
- Role-based access control

### ✅ Beautiful UI
- Fennec branding colors
- Clean, modern design
- Tabbed interface
- Status bar with feedback
- Responsive layout

## Installation

### 1. Install Dependencies

```bash
# Tkinter is usually included with Python
# Install requests library
pip install requests
```

### 2. Make Sure API is Running

```bash
# In one terminal, start the API
python main.py
```

### 3. Run the GUI Client

```bash
# In another terminal, start the GUI
python gui_client.py
```

## Usage

### Login

1. **Default Credentials:**
   - Email: `admin@fennec.dev`
   - Password: `admin123`

2. Click **"Login"** button

3. You'll see your user info displayed

### View Users

1. Go to **"👥 Users"** tab
2. Click **"🔄 Refresh"** to load users
3. Users are displayed in a table

### Create User

1. Go to **"➕ Add User"** tab
2. Fill in the form:
   - Name (2-50 characters)
   - Email
   - Age (0-150)
3. Click **"💾 Save User"**
4. User is created and welcome email is sent (simulated)

### Edit User

1. Go to **"👥 Users"** tab
2. Select a user from the table
3. Click **"✏️ Edit"**
4. Form is filled with user data
5. Modify and click **"💾 Update User"**

### Delete User

1. Go to **"👥 Users"** tab
2. Select a user from the table
3. Click **"🗑️ Delete"**
4. Confirm deletion

### Admin Panel

1. Login as admin
2. Go to **"🔒 Admin"** tab
3. Click **"🔄 Refresh"** to load all users
4. Select and delete users with admin privileges

### Logout

1. Click **"Logout"** button in the left panel
2. You'll be returned to the login screen

## Screenshots

### Main Window
```
┌─────────────────────────────────────────────────────────┐
│  🦊 Fennec Framework - API Client                       │
├──────────────┬──────────────────────────────────────────┤
│ Authentication│  👥 Users  │ ➕ Add User │ 🔒 Admin    │
│              ├──────────────────────────────────────────┤
│ Email:       │  ID │ Name      │ Email        │ Age     │
│ [________]   │  1  │ Admin     │ admin@...    │ 30      │
│              │  2  │ John Doe  │ john@...     │ 25      │
│ Password:    │  3  │ Jane      │ jane@...     │ 28      │
│ [________]   │                                          │
│              │  [🔄 Refresh] [✏️ Edit] [🗑️ Delete]     │
│ [Login]      │                                          │
│              │                                          │
│ API: localhost│                                         │
└──────────────┴──────────────────────────────────────────┘
│ Status: ✓ Connected to API                              │
└─────────────────────────────────────────────────────────┘
```

## Features Breakdown

### Tab 1: Users List
- **Table View**: Shows all users with ID, Name, Email, Age, Role
- **Refresh Button**: Reload users from API
- **Edit Button**: Edit selected user
- **Delete Button**: Delete selected user
- **Double-click**: Quick view user details

### Tab 2: Add/Edit User
- **Form Fields**: Name, Email, Age
- **Validation**: Client-side and server-side
- **Save Button**: Create or update user
- **Clear Button**: Reset form
- **Auto-switch**: Returns to users list after save

### Tab 3: Admin Panel
- **Admin-only**: Requires admin role
- **Full User List**: See all users including passwords (hidden)
- **Admin Delete**: Delete any user (except yourself)
- **Access Control**: Shows error if not admin

## API Integration

### Endpoints Used

```python
# Public
GET  /health              # Check API status
GET  /users               # List users
GET  /users/{id}          # Get user
POST /users               # Create user
PUT  /users/{id}          # Update user
DELETE /users/{id}        # Delete user

# Authentication
POST /auth/login          # Login
GET  /auth/me             # Get current user

# Admin
GET  /admin/users         # List all users (admin)
DELETE /admin/users/{id}  # Delete user (admin)
```

### Authentication Flow

1. User enters credentials
2. GUI sends POST to `/auth/login`
3. API returns JWT token
4. GUI stores token in memory
5. All subsequent requests include token in header:
   ```
   Authorization: Bearer <token>
   ```

## Error Handling

### API Not Running
- Shows warning dialog on startup
- Status bar shows error message
- Suggests running `python main.py`

### Authentication Errors
- Invalid credentials: Shows error dialog
- Token expired: Prompts to login again
- No token: Redirects to login

### Validation Errors
- Empty fields: Shows error before sending
- Invalid age: Caught by API validation
- Invalid email: Caught by API validation

### Network Errors
- Connection refused: Shows error dialog
- Timeout: Shows timeout message
- Server error: Shows server response

## Customization

### Change API URL

Edit `gui_client.py`:
```python
self.api = FennecAPIClient(base_url="http://your-api-url:port")
```

### Change Colors

Edit the `colors` dictionary:
```python
self.colors = {
    "primary": "#D4A574",    # Your primary color
    "secondary": "#E8D5B7",  # Your secondary color
    # ... etc
}
```

### Add New Features

1. Add method to `FennecAPIClient` class
2. Add UI elements to appropriate tab
3. Add event handler
4. Connect to API method

## Troubleshooting

### Problem: GUI doesn't start

**Solution:**
```bash
# Check if tkinter is installed
python -c "import tkinter; print('OK')"

# If not, install it (Ubuntu/Debian)
sudo apt-get install python3-tk

# Or (Fedora)
sudo dnf install python3-tkinter
```

### Problem: "API not running" error

**Solution:**
```bash
# Start the API first
python main.py

# Then start the GUI
python gui_client.py
```

### Problem: Login fails

**Solution:**
- Check credentials (default: admin@fennec.dev / admin123)
- Make sure API is running
- Check API logs for errors

### Problem: "Access denied" in admin panel

**Solution:**
- Login with admin account
- Regular users can't access admin panel
- Check user role in database

## Development

### Project Structure

```python
gui_client.py
├── FennecAPIClient      # API client class
│   ├── login()
│   ├── logout()
│   ├── get_users()
│   ├── create_user()
│   ├── update_user()
│   ├── delete_user()
│   └── admin_*()
│
└── FennecGUI            # Main GUI class
    ├── setup_ui()
    ├── setup_left_panel()    # Login/User info
    ├── setup_right_panel()   # Tabs
    ├── setup_users_tab()     # Users list
    ├── setup_user_form_tab() # Add/Edit form
    ├── setup_admin_tab()     # Admin panel
    └── Event handlers...
```

### Adding a New Tab

```python
# 1. Create tab frame
new_tab = tk.Frame(self.notebook, bg="white")
self.notebook.add(new_tab, text="📊 New Tab")

# 2. Setup tab content
def setup_new_tab(self):
    # Add your widgets here
    pass

# 3. Call setup in __init__
self.setup_new_tab()
```

### Adding a New API Method

```python
# 1. Add to FennecAPIClient
def new_method(self, param):
    response = requests.get(
        f"{self.base_url}/new-endpoint",
        headers=self._headers()
    )
    return response.json()

# 2. Add event handler in FennecGUI
def handle_new_action(self):
    try:
        result = self.api.new_method(param)
        # Update UI
    except Exception as e:
        messagebox.showerror("Error", str(e))
```

## Tips & Tricks

### Keyboard Shortcuts
- **Enter** in login form: Submit login
- **Escape**: Close dialogs
- **F5**: Refresh (if implemented)

### Best Practices
1. Always check if API is running first
2. Login before accessing protected features
3. Refresh users list after modifications
4. Logout when done for security

### Performance
- Users list loads on demand
- Token stored in memory (not persistent)
- Minimal API calls
- Efficient UI updates

## Future Enhancements

Possible additions:
- [ ] Search/filter users
- [ ] Pagination for large user lists
- [ ] User profile pictures
- [ ] Export users to CSV
- [ ] Dark mode
- [ ] Settings panel
- [ ] Remember login (with security)
- [ ] Real-time updates (WebSocket)
- [ ] Statistics dashboard
- [ ] Bulk operations

## Security Notes

⚠️ **Important:**
- Token stored in memory only (cleared on exit)
- No password caching
- HTTPS recommended for production
- Don't expose admin credentials
- Use environment variables for sensitive data

## Support

Having issues? Check:
1. [Main Documentation](README.md)
2. [API Example Guide](EXAMPLE_GUIDE.md)
3. [Fennec Documentation](FENNEC_INTRO.md)

---

<div align="center">
  <strong>🦊 Fennec Framework 🦊</strong><br>
  Small, Swift, and Adaptable<br><br>
  Now with a beautiful GUI client!<br>
  Built with ❤️ in Tunisia 🇹🇳
</div>
