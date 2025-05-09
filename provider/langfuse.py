from typing import Any, Dict

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.search_prompts import DifyLangfusePluginTool


class DifyLangfusePluginProvider(ToolProvider):
    """Langfuse plugin provider"""

    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """Validate credentials

        Args:
            credentials:
                - langfuse_host: Langfuse host
                - langfuse_secret_key: Langfuse secret key
                - langfuse_public_key: Langfuse public key

        Raises:
            ToolProviderCredentialValidationError: If credentials are invalid
        """
        try:
            # Initialize tool with credentials
            tool = DifyLangfusePluginTool.from_credentials(credentials)
            
            # Execute test request
            for _ in tool.invoke(tool_parameters={"name": "test"}):
                pass

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
