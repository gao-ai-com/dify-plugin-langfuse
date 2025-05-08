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
            yield self.create_text_message("Version and label cannot be specified simultaneously.")
            return
            
        # クエリパラメータを設定
        params = {}
        if tool_parameters.get("version"):
            params["version"] = tool_parameters["version"]
        if tool_parameters.get("label"):
            params["label"] = tool_parameters["label"]
            
        # APIリクエストを送信
        response = requests.get(url, headers=headers, params=params, auth=(public_key, secret_key))
        try:
            response.raise_for_status()
            valuable_res = response.json()
            if valuable_res["type"] == "text":
                yield self.create_text_message(valuable_res["prompt"])
                yield self.create_json_message(valuable_res)
            else:
                raise ValueError(f"Unsupported prompt type: {valuable_res['type']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"Prompt not found: name='{prompt_name}'"
                if tool_parameters.get("version"):
                    error_msg += f", version='{tool_parameters['version']}'"
                if tool_parameters.get("label"):
                    error_msg += f", label='{tool_parameters['label']}'"
                raise ValueError(error_msg)
            raise
