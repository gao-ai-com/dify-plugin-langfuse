from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.search_prompts import DifyLangfusePluginTool


class DifyLangfusePluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in DifyLangfusePluginTool.from_credentials(credentials).invoke(
                tool_parameters={"name": "test"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
