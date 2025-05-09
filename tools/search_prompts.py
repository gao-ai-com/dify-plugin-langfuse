import requests
from collections.abc import Generator
from typing import Any, Dict, Optional
from datetime import datetime
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Tool to search prompts from Langfuse"""

    def _validate_iso8601(self, date_str: Optional[str]) -> bool:
        """Validate ISO8601 datetime string

        Args:
            date_str: Datetime string to validate

        Returns:
            Validation result
        """
        if not date_str:
            return True

        # ISO8601 regex pattern
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$'

        if not re.match(pattern, date_str):
            return False

        try:
            # Convert Z to +00:00 and parse as datetime
            normalized_date = date_str.replace('Z', '+00:00')
            datetime.fromisoformat(normalized_date)
            return True
        except ValueError:
            return False

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Search prompts

        Args:
            tool_parameters: Tool parameters
                - name: Prompt name (optional)
                - label: Label (optional)
                - tag: Tag (optional)
                - page: Page number (optional)
                - limit: Items per page (optional)
                - fromUpdatedAt: Updated at (start) (optional)
                - toUpdatedAt: Updated at (end) (optional)

        Yields:
            ToolInvokeMessage: Tool execution result
        """
        # Set API endpoint and authentication
        url: str = f"{self.runtime.credentials['langfuse_host']}/api/public/v2/prompts"
        secret_key: str = self.runtime.credentials["langfuse_secret_key"]
        public_key: str = self.runtime.credentials["langfuse_public_key"]

        # Validate datetime parameters
        from_updated_at: Optional[str] = tool_parameters.get("fromUpdatedAt")
        to_updated_at: Optional[str] = tool_parameters.get("toUpdatedAt")

        if from_updated_at and not self._validate_iso8601(from_updated_at):
            raise ValueError("fromUpdatedAt must be in ISO8601 format. Example: 2024-03-20T10:30:00Z")

        if to_updated_at and not self._validate_iso8601(to_updated_at):
            raise ValueError("toUpdatedAt must be in ISO8601 format. Example: 2024-03-20T10:30:00Z")

        # Set query parameters
        params: Dict[str, Any] = {}
        for key in ["name", "label", "tag", "page", "limit"]:
            if value := tool_parameters.get(key):
                params[key] = value

        if from_updated_at:
            params["fromUpdatedAt"] = from_updated_at
        if to_updated_at:
            params["toUpdatedAt"] = to_updated_at

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
            for res in valuable_res["data"]:
                yield self.create_json_message(res)

        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Failed to search prompts: {str(e)}")
