import json
import re
import requests
from collections.abc import Generator
from typing import Any, Dict, Optional

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DifyLangfusePluginTool(Tool):
    """Tool to retrieve prompts from Langfuse"""

    def _replace_variables(self, prompt_text: str, variables: Optional[str]) -> str:
        """Replace variables in prompt text with provided values
        
        Args:
            prompt_text: The original prompt text containing {{variable}} patterns
            variables: JSON string containing variable names and values
            
        Returns:
            str: Prompt text with variables replaced
            
        Raises:
            ValueError: If variables JSON is invalid or variable not found
        """
        if not variables:
            return prompt_text
            
        try:
            # Parse JSON string to dictionary
            var_dict = json.loads(variables)
            if not isinstance(var_dict, dict):
                raise ValueError("Variables must be a JSON object (dictionary)")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in variables parameter: {str(e)}")
        
        # Find all {{variable}} patterns in the prompt
        pattern = r'\{\{(\w+)\}\}'
        
        def replace_match(match):
            var_name = match.group(1)
            if var_name in var_dict:
                return str(var_dict[var_name])
            else:
                # Keep the original {{variable}} if not found in provided variables
                return match.group(0)
        
        # Replace all matches
        return re.sub(pattern, replace_match, prompt_text)

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Retrieve a prompt

        Args:
            tool_parameters: Tool parameters
                - name: Prompt name (required)
                - version: Version (optional)
                - label: Label (optional)
                - variables: JSON string containing variable replacements (optional)

        Yields:
            ToolInvokeMessage: Tool execution result
        """
        # Get parameters
        prompt_name: str = tool_parameters["name"]
        version: Optional[int] = tool_parameters.get("version")
        label: Optional[str] = tool_parameters.get("label")
        variables: Optional[str] = tool_parameters.get("variables")

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
                # Apply variable replacement if variables are provided
                original_prompt = valuable_res["prompt"]
                processed_prompt = self._replace_variables(original_prompt, variables)
                
                # Update the JSON response to include the processed prompt
                response_data = valuable_res.copy()
                response_data["processed_prompt"] = processed_prompt
                response_data["variables_applied"] = variables is not None
                
                yield self.create_text_message(processed_prompt)
                yield self.create_json_message(response_data)
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
