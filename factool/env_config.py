"""Environment configuration for Factool. """
import pydantic


class FactoolEnvConfig(pydantic.BaseSettings, frozen=True):
    """Environment configuration for Factool."""

    openai_api_key: str = pydantic.Field(
        default=None,
        env="OPENAI_API_KEY",
        description="API key for OpenAI",
    )
factool_env_config = FactoolEnvConfig()
