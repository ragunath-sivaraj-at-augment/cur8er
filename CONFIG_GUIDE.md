# Configuration Guide

This application supports two ways to configure API keys and environment variables:

## Local Development (using .env file)

For local development, create a `.env` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

The application will automatically load these variables when running locally.

## Streamlit Cloud Deployment (using Streamlit Secrets)

When deploying to Streamlit Cloud:

1. **Don't** include your `.env` file in the deployment
2. **Do** configure secrets in Streamlit Cloud:
   - Go to your app's settings in Streamlit Cloud
   - Navigate to the "Secrets" tab
   - Add your configuration in TOML format:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
GOOGLE_API_KEY = "your-google-api-key-here"
```

## How It Works

The `EnvironmentManager` class automatically detects the environment and uses the proper API key retrieval method:

**Method 1: `get_config_value()` (Primary)**
```python
# Uses st.secrets.get() with fallback to os.getenv()
api_key = EnvironmentManager.get_config_value("OPENAI_API_KEY")
```

**Method 2: `get_api_keys_explicit()` (Backup/Debug)**
```python
# Explicit pattern for maximum compatibility
keys = EnvironmentManager.get_api_keys_explicit()
```

Both methods use this priority order:
1. **Streamlit secrets** (via `st.secrets.get()`)
2. **Environment variables** (via `os.getenv()`)
3. **Default values** (if specified)

### Key Benefits

- **Robust Fallback**: Uses `st.secrets.get()` with explicit fallback
- **Debug Support**: Includes debugging information in sidebar
- **Auto-detection**: Detects deployment environment automatically
- **Maximum Compatibility**: Works with all Streamlit deployment types

## Files Modified

- `utils/config.py`: Added `EnvironmentManager` class
- `utils/helpers.py`: Updated to use new configuration system
- `utils/ai_generator.py`: Updated API key handling
- `app.py`: Conditional .env loading

## Example Usage

```python
from utils.config import EnvironmentManager

# Get API key from either secrets or env vars
api_key = EnvironmentManager.get_config_value("OPENAI_API_KEY")

# Check if running in Streamlit deployment
is_deployed = EnvironmentManager.is_streamlit_deployment()

# Get all API keys (primary method)
all_keys = EnvironmentManager.get_all_api_keys()

# Get all API keys (explicit method for debugging)
explicit_keys = EnvironmentManager.get_api_keys_explicit()
```

## Troubleshooting

### Issue: "Cannot generate images without API key" 

**For Streamlit Cloud:**
1. Check the "🔍 API Key Debug Info" in the sidebar
2. Verify secrets are configured in Streamlit Cloud settings
3. Ensure secrets use exact format: `GOOGLE_API_KEY = "your-key"`
4. Try redeploying the app after updating secrets

**For Local Development:**
1. Check if `.env` file exists in project root
2. Verify `.env` format: `GOOGLE_API_KEY=your-key` (no quotes)
3. Restart the application after changing `.env`

### Debug Steps:
1. Enable "🔍 API Key Debug Info" expander in sidebar
2. Check both "primary" and "explicit" method results
3. Verify environment detection is correct
4. Compare masked key values to ensure they match your actual keys