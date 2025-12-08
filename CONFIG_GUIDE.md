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

The `EnvironmentManager` class automatically detects the environment:

- **Streamlit Cloud**: Uses `st.secrets` for configuration
- **Local Development**: Uses environment variables (loaded from `.env`)

### Priority Order

1. Streamlit secrets (highest priority)
2. Environment variables
3. Default values (if specified)

### Key Benefits

- **Security**: No API keys in your code repository
- **Flexibility**: Same code works in both local and cloud environments
- **Auto-detection**: No manual configuration needed

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

# Get all API keys
all_keys = EnvironmentManager.get_all_api_keys()
```