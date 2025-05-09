import requests
from collections.abc import Generator
from typing import Any, Dict, Optional
from datetime import datetime
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Langfuseからプロンプトを検索するツール"""

    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """APIレスポンスをパースする

        Args:
            response: APIレスポンス

        Returns:
            パースされたレスポンス
        """
        result: Dict[str, Any] = {}
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

    def _validate_iso8601(self, date_str: Optional[str]) -> bool:
        """ISO8601形式の日時文字列を検証する

        Args:
            date_str: 検証する日時文字列

        Returns:
            検証結果
        """
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

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """プロンプトを検索する

        Args:
            tool_parameters: ツールパラメータ
                - name: プロンプト名（オプション）
                - label: ラベル（オプション）
                - tag: タグ（オプション）
                - page: ページ番号（オプション）
                - limit: 1ページあたりの件数（オプション）
                - fromUpdatedAt: 更新日時（開始）（オプション）
                - toUpdatedAt: 更新日時（終了）（オプション）

        Yields:
            ToolInvokeMessage: ツール実行結果
        """
        # APIエンドポイントと認証情報を設定
        url: str = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts"
        secret_key: str = self.runtime.credentials["langfuse_secret_key"]
        public_key: str = self.runtime.credentials["langfuse_public_key"]

        # 日時パラメータのバリデーション
        from_updated_at: Optional[str] = tool_parameters.get("fromUpdatedAt")
        to_updated_at: Optional[str] = tool_parameters.get("toUpdatedAt")

        if from_updated_at and not self._validate_iso8601(from_updated_at):
            raise ValueError("fromUpdatedAt must be in ISO8601 format. Example: 2024-03-20T10:30:00Z")

        if to_updated_at and not self._validate_iso8601(to_updated_at):
            raise ValueError("toUpdatedAt must be in ISO8601 format. Example: 2024-03-20T10:30:00Z")

        # クエリパラメータを設定
        params: Dict[str, Any] = {}
        for key in ["name", "label", "tag", "page", "limit"]:
            if value := tool_parameters.get(key):
                params[key] = value

        if from_updated_at:
            params["fromUpdatedAt"] = from_updated_at
        if to_updated_at:
            params["toUpdatedAt"] = to_updated_at

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
            for res in valuable_res["data"]:
                yield self.create_json_message(res)

        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Failed to search prompts: {str(e)}")
