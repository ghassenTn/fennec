# Publishing Fennec Framework to PyPI 🦊

This guide will help you publish Fennec Framework to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**
   - Create an account at https://pypi.org/account/register/
   - Verify your email address

2. **TestPyPI Account** (for testing)
   - Create an account at https://test.pypi.org/account/register/
   - Verify your email address

3. **Install Required Tools**
   ```bash
   pip install --upgrade pip setuptools wheel twine build
   ```

## Step 1: Update Package Information

Before publishing, update these files with your information:

### setup.py
```python
author_email="your.email@example.com",  # Your email
url="https://github.com/yourusername/fennec-framework",  # Your GitHub URL
```

### pyproject.toml
```toml
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
```

## Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info
```

## Step 3: Build the Package

```bash
# Build source distribution and wheel
python -m build

# Or using setup.py
python setup.py sdist bdist_wheel
```

This creates:
- `dist/fennec-framework-0.3.0.tar.gz` (source distribution)
- `dist/fennec_framework-0.3.0-py3-none-any.whl` (wheel)

## Step 4: Test on TestPyPI (Recommended)

### Upload to TestPyPI
```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: Your TestPyPI username
- Password: Your TestPyPI password (or API token)

### Test Installation from TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps fennec-framework
```

### Test the Package
```python
from fennec import Application

app = Application(title="Test API")
print("✅ Fennec Framework installed successfully!")
```

## Step 5: Publish to PyPI

Once you've tested on TestPyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username: Your PyPI username
- Password: Your PyPI password (or API token)

## Step 6: Verify Publication

1. Visit https://pypi.org/project/fennec-framework/
2. Check that all information is correct
3. Test installation:
   ```bash
   pip install fennec-framework
   ```

## Using API Tokens (Recommended)

API tokens are more secure than passwords.

### Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Give it a name (e.g., "fennec-framework-upload")
4. Set scope to "Entire account" or specific project
5. Copy the token (starts with `pypi-`)

### Configure .pypirc

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Set permissions:
```bash
chmod 600 ~/.pypirc
```

Now you can upload without entering credentials:
```bash
python -m twine upload dist/*
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI API token to GitHub Secrets:
1. Go to your repo → Settings → Secrets → Actions
2. Add new secret: `PYPI_API_TOKEN`
3. Paste your PyPI API token

## Version Management

### Updating Version

Update version in these files:
- `setup.py`: `version="0.3.1"`
- `pyproject.toml`: `version = "0.3.1"`
- `fennec/__init__.py`: `__version__ = "0.3.1"`

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.3.0): New features, backwards compatible
- **PATCH** (0.3.1): Bug fixes, backwards compatible

## Checklist Before Publishing

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are updated
- [ ] README.md is complete
- [ ] LICENSE file exists
- [ ] Examples work correctly
- [ ] Package builds without errors
- [ ] Tested on TestPyPI
- [ ] GitHub repository is public (if linking)

## Common Issues

### Issue: "File already exists"
**Solution**: You can't re-upload the same version. Increment the version number.

### Issue: "Invalid distribution"
**Solution**: Make sure all required files exist (README.md, LICENSE, etc.)

### Issue: "Authentication failed"
**Solution**: Check your username/password or API token. Make sure .pypirc is configured correctly.

### Issue: "Package name already taken"
**Solution**: The name "fennec-framework" must be available. Check https://pypi.org/project/fennec-framework/

## Post-Publication

1. **Create a GitHub Release**
   - Tag: `v0.3.0`
   - Title: "Fennec Framework v0.3.0 - Production Ready"
   - Description: Copy from CHANGELOG.md

2. **Announce**
   - Tweet about the release
   - Post on Reddit (r/Python)
   - Share on LinkedIn
   - Update documentation site

3. **Monitor**
   - Watch for issues on GitHub
   - Respond to PyPI comments
   - Track download statistics

## Resources

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/
- Semantic Versioning: https://semver.org/

---

Built with ❤️ in Tunisia 🇹🇳
