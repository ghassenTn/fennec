# How to Publish Fennec to PyPI 🦊

## Quick Start (3 Steps)

### 1. Create PyPI Account
- Register at https://pypi.org/account/register/
- Verify your email

### 2. Install Tools
```bash
pip install --upgrade pip setuptools wheel twine build
```

### 3. Publish
```bash
./publish.sh
```

Choose option 3 (test on TestPyPI first, then publish to PyPI).

---

## Manual Publishing

If you prefer manual control:

```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

---

## Using API Tokens (Recommended)

1. Get token from https://pypi.org/manage/account/token/
2. Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
```

3. Set permissions:
```bash
chmod 600 ~/.pypirc
```

Now you can upload without entering credentials.

---

## After Publishing

1. **Verify**: https://pypi.org/project/fennec/
2. **Test**: `pip install fennec`
3. **Create GitHub Release**: Tag v0.3.0
4. **Announce**: Share on social media

---

## Troubleshooting

**"File already exists"**: Increment version number in `setup.py` and `pyproject.toml`

**"Authentication failed"**: Check your username/password or API token

**"Package name taken"**: The name must be unique on PyPI

---

For detailed information, see [PUBLISHING.md](PUBLISHING.md)

Built with ❤️ in Tunisia 🇹🇳
