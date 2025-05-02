import requests
from collections.abc import Generator
from typing import Any
from datetime import datetime
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DifyLangfusePluginTool(Tool):
    def _parse_response(self, response: dict) -> dict:
        result = {}
        if "data" in response:
            result["prompts"] = [
                {
                    "name": item.get("name", ""),
                    "versions": item.get("versions", []),
                    "labels": item.get("labels", [])
                }
                for item in response["data"]
            ]
        if "meta" in response:
            result["meta"] = response["meta"]
        return result
    
    def _validate_iso8601(self, date_str: str) -> bool:
        """ISO8601形式の日時文字列を検証する"""
        if not date_str:
            return True
        
        # ISO8601形式の正規表現パターン
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$'
        
        if not re.match(pattern, date_str):
            return False
            
        try:
            # Zを+00:00に変換してdatetimeとして解釈
            normalized_date = date_str.replace('Z', '+00:00')
            datetime.fromisoformat(normalized_date)
            return True
        except ValueError:
            return False

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # APIエンドポイントと認証情報を設定
        url = f"{self.runtime.credentials["langfuse_host"]}/api/public/v2/prompts"
        secret_key = self.runtime.credentials["langfuse_secret_key"]
        public_key = self.runtime.credentials["langfuse_public_key"]

        # ヘッダーを設定
        headers = {
            "Content-Type": "application/json",
        }
        
        # 日時パラメータのバリデーション
        from_updated_at = tool_parameters.get("fromUpdatedAt")
        to_updated_at = tool_parameters.get("toUpdatedAt")
        
        if from_updated_at and not self._validate_iso8601(from_updated_at):
            yield self.create_text_message("fromUpdatedAtはISO8601形式の日時である必要があります。例: 2024-03-20T10:30:00Z")
            return
            
        if to_updated_at and not self._validate_iso8601(to_updated_at):
            yield self.create_text_message("toUpdatedAtはISO8601形式の日時である必要があります。例: 2024-03-20T10:30:00Z")
            return
        
        # クエリパラメータを設定し、デフォルト値を適用
        params = {}
        
        # 値が存在する場合のみパラメータに追加
        if tool_parameters.get("name"):
            params["name"] = tool_parameters["name"]
        if tool_parameters.get("label"):
            params["label"] = tool_parameters["label"]
        if tool_parameters.get("tag"):
            params["tag"] = tool_parameters["tag"]
        if tool_parameters.get("page"):
            params["page"] = tool_parameters["page"]
        if tool_parameters.get("limit"):
            params["limit"] = tool_parameters["limit"]
        if from_updated_at:
            params["fromUpdatedAt"] = from_updated_at
        if to_updated_at:
            params["toUpdatedAt"] = to_updated_at
        
        # APIリクエストを送信
        response = requests.get(url, headers=headers, params=params, auth=(public_key, secret_key))
        response.raise_for_status()
        valuable_res = response.json()
        for res in valuable_res["data"]:
            yield self.create_json_message(res)
