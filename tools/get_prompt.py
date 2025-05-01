from collections.abc import Generator
from typing import Any, Optional, Union, List
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from langfuse import Langfuse

class DifyLangfusePluginTool(Tool):
    def _parse_response(self, response: dict) -> dict:
        result = {}
        if "knowledge_graph" in response:
            result["title"] = response["knowledge_graph"].get("title", "")
            result["description"] = response["knowledge_graph"].get("description", "")
        if "organic_results" in response:
            result["organic_results"] = [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
                for item in response["organic_results"]
            ]
        return result

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Langfuseクライアントの初期化
        langfuse = Langfuse(
            public_key=self.runtime.credentials["langfuse_public_key"],
            secret_key=self.runtime.credentials["langfuse_secret_key"],
            host=self.runtime.credentials["langfuse_host"]
        )
        
        try:
            # バージョンとラベルは同時に指定できない
            if tool_parameters.get("version") and tool_parameters.get("label"):
                yield self.create_text_message("バージョンとラベルは同時に指定できません。")
                return
            
            # get_promptメソッドを呼び出し
            prompt = langfuse.get_prompt(
                name=tool_parameters["name"],
                version=tool_parameters.get("version"),
                label=tool_parameters.get("label"),
                type=tool_parameters.get("type", "text"),
                cache_ttl_seconds=tool_parameters.get("cache_ttl_seconds"),
                max_retries=tool_parameters.get("max_retries"),
                fetch_timeout_seconds=tool_parameters.get("fetch_timeout_seconds")
            )
            
            # レスポンスを返す
            yield self.create_json_message({
                "prompt": prompt.prompt,
                "config": prompt.config
            })
            
        except Exception as e:
            yield self.create_text_message(f"エラーが発生しました: {str(e)}")
        finally:
            # Langfuseクライアントをシャットダウン
            langfuse.shutdown()
