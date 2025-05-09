from typing import Any, Dict

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.search_prompts import DifyLangfusePluginTool


class DifyLangfusePluginProvider(ToolProvider):
    """Langfuseプラグインのプロバイダー"""

    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """認証情報を検証する

        Args:
            credentials: 認証情報
                - langfuse_host: Langfuseのホスト
                - langfuse_secret_key: Langfuseの秘密鍵
                - langfuse_public_key: Langfuseの公開鍵

        Raises:
            ToolProviderCredentialValidationError: 認証情報が無効な場合
        """
        try:
            # 認証情報を使用してツールを初期化
            tool = DifyLangfusePluginTool.from_credentials(credentials)
            
            # テスト用のリクエストを実行
            for _ in tool.invoke(tool_parameters={"name": "test"}):
                pass

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
