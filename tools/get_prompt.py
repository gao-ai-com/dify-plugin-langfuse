import requests
from collections.abc import Generator
from typing import Any, Dict, Optional

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Tool to retrieve prompts from Langfuse"""

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Retrieve a prompt

        Args:
            tool_parameters: Tool parameters
                - name: Prompt name (required)
                - version: Version (optional)
                - label: Label (optional)

        Yields:
            ToolInvokeMessage: Tool execution result
        """
        # Get parameters
        prompt_name: str = tool_parameters["name"]
        version: Optional[int] = tool_parameters.get("version")
        label: Optional[str] = tool_parameters.get("label")

        # Version and label cannot be specified simultaneously
        if version and label:
            raise ValueError("Version and label cannot be specified simultaneously.")

        # Set API endpoint and authentication
        url: str = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts/{prompt_name}"
        secret_key: str = self.runtime.credentials["langfuse_secret_key"]
        public_key: str = self.runtime.credentials["langfuse_public_key"]

        # Set query parameters
        params: Dict[str, Any] = {}
        if version:
            params["version"] = version
        if label:
            params["label"] = label

        try:
            # Send API request
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"},
                params=params,
                auth=(public_key, secret_key)
            )
            response.raise_for_status()
            valuable_res = response.json()

            # Process response
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
