import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DifyLangfusePluginTool(Tool):
    def _parse_response(self, response: dict) -> str:
        result = {
            "type": response.get("type"),
            "prompt": response.get("prompt"),
        }
        return result

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # APIエンドポイントと認証情報を設定
        prompt_name = tool_parameters["name"]
        url = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts/{prompt_name}"
        secret_key = self.runtime.credentials["langfuse_secret_key"]
        public_key = self.runtime.credentials["langfuse_public_key"]

        # ヘッダーを設定
        headers = {
            "Content-Type": "application/json",
        }
        
        # バージョンとラベルは同時に指定できない
        if tool_parameters.get("version") and tool_parameters.get("label"):
            yield self.create_text_message("バージョンとラベルは同時に指定できません。")
            return
            
        # クエリパラメータを設定
        params = {}
        if tool_parameters.get("version"):
            params["version"] = tool_parameters["version"]
        if tool_parameters.get("label"):
            params["label"] = tool_parameters["label"]
            
        # APIリクエストを送信
        response = requests.get(url, headers=headers, params=params, auth=(public_key, secret_key))
        response.raise_for_status()
        valuable_res = response.json()
        if valuable_res["type"] == "text":
            yield self.create_text_message(valuable_res["prompt"])
            yield self.create_json_message(valuable_res)
        else:
            raise ValueError(f"未対応のプロンプトタイプです: {valuable_res['type']}")
