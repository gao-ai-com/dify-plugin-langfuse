from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.search_prompts import DifyLangfusePluginTool
from langfuse.decorators import langfuse_context


class DifyLangfusePluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            DifyLangfusePluginTool.from_credentials(credentials)
            if not langfuse_context.auth_check():
                raise ToolProviderCredentialValidationError("Langfuseの認証に失敗しました")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
