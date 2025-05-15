import requests
from collections.abc import Generator
from typing import Any, Dict

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Tool to update prompts in Langfuse"""

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Update a prompt

        Args:
            tool_parameters: Tool parameters
                - name: Prompt name (required)
                - prompt: Prompt content (required)
                - labels: Comma-separated labels (optional)
                - tag: tag (optional)
                - commitMessage: Commit message (optional)

        Yields:
            ToolInvokeMessage: Tool execution result
        """
        # Set API endpoint and authentication
        url: str = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts"
        secret_key: str = self.runtime.credentials["langfuse_secret_key"]
        public_key: str = self.runtime.credentials["langfuse_public_key"]

        # Prepare request body
        body: Dict[str, Any] = {}
        for key in ["type", "name", "prompt", "commitMessage"]:
            if value := tool_parameters.get(key):
                body[key] = value

        # Convert comma-separated strings to lists for labels and tags
        if labels := tool_parameters.get("labels"):
            body["labels"] = [label.strip() for label in labels.split(",")]
        if tag := tool_parameters.get("tag"):
            body["tags"] = [tag.strip()]

        try:
            # Send API request
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=body,
                auth=(public_key, secret_key)
            )
            response.raise_for_status()
            valuable_res = response.json()

            # Process response
            yield self.create_json_message(valuable_res)
            yield self.create_text_message(str(valuable_res["version"]))

        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Failed to update prompt: {str(e)}")
