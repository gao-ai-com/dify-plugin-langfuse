import requests
from collections.abc import Generator
from typing import Any, Dict, Optional

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Langfuseからプロンプトを取得するツール"""

    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """APIレスポンスをパースする

        Args:
            response: APIレスポンス

        Returns:
            パースされたレスポンス
        """
        return {
            "type": response.get("type"),
            "prompt": response.get("prompt"),
        }

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """プロンプトを取得する

        Args:
            tool_parameters: ツールパラメータ
                - name: プロンプト名（必須）
                - version: バージョン（オプション）
                - label: ラベル（オプション）

        Yields:
            ToolInvokeMessage: ツール実行結果
        """
        # パラメータの取得
        prompt_name: str = tool_parameters["name"]
        version: Optional[int] = tool_parameters.get("version")
        label: Optional[str] = tool_parameters.get("label")

        # バージョンとラベルは同時に指定できない
        if version and label:
            raise ValueError("Version and label cannot be specified simultaneously.")

        # APIエンドポイントと認証情報を設定
        url: str = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts/{prompt_name}"
        secret_key: str = self.runtime.credentials["langfuse_secret_key"]
        public_key: str = self.runtime.credentials["langfuse_public_key"]

        # クエリパラメータを設定
        params: Dict[str, Any] = {}
        if version:
            params["version"] = version
        if label:
            params["label"] = label

        try:
            # APIリクエストを送信
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"},
                params=params,
                auth=(public_key, secret_key)
            )
            response.raise_for_status()
            valuable_res = response.json()

            # レスポンスの処理
            if valuable_res["type"] == "text":
                yield self.create_text_message(valuable_res["prompt"])
                yield self.create_json_message(valuable_res)
            else:
                raise ValueError(f"Unsupported prompt type: {valuable_res['type']}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"Prompt not found: name='{prompt_name}'"
                if version:
                    error_msg += f", version='{version}'"
                if label:
                    error_msg += f", label='{label}'"
                raise ValueError(error_msg)
            raise
