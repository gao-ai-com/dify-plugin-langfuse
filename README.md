# Dify Plugin Langfuse

**Author** [gao-ai-com](https://github.com/gao-ai-com)
**Version:** 0.0.3
**Type:** tool

## Overview

This repository is a custom plugin for integrating [Langfuse](https://langfuse.com/), an LLM observability & prompt management tool, with [Dify](https://dify.ai/), an LLM application development platform.

By using this plugin, you can directly utilize and search prompts managed in Langfuse from within Dify workflows, supporting efficient prompt management and improving application development quality.

## Main Features

This plugin provides three main features as custom tools for Dify:

* **Get Prompt Tool:** Retrieves specific prompts (text type) managed in Langfuse for use in Dify workflows.
* **Search Prompts Tool:** Searches for prompts in Langfuse under various conditions to discover available prompts.
* **Update Prompt Tool:** Creates a new version of a prompt managed in Langfuse and sets tags and labels.

## Installation
1. **Navigate to Dify's Plugin Management Page**: After logging into Dify, click on [Plugins] in the top right corner to open the plugin management page, then click [Install Plugin] followed by [GitHub].
2. **Enter Repository Address**: In the field that appears for entering the GitHub repository address of the plugin to install, enter: https://github.com/gao-ai-com/dify-plugin-langfuse
3. **Select Version and Package File**: Once the repository is recognized, you'll proceed to a screen where you can select the available version number and package. Select the appropriate one and follow the instructions to complete the installation.

## Usage

### Get Prompt Tool

Loads the content of a specific prompt managed on Langfuse into a Dify workflow.

**Purpose:**
To retrieve the content of prompts stored and managed on Langfuse in a format usable within Dify workflows.

**Main Features:**
* Retrieves prompt content by specifying the prompt name.
* Allows specification of labels and versions.
* Supports variable replacement in prompts using JSON-formatted variable definitions.

**Input Parameters:**
| Parameter | Description | Required | Default Value |
| :-------- | :---------- | :------- | :------------ |
| `name` | Unique name of the prompt managed in Langfuse. | Yes | - |
| `label` | Label assigned to the prompt version to retrieve. Cannot be specified together with `version`. | No | production |
| `version` | Specific version number of the prompt to retrieve. Cannot be specified together with `label`. | No | - |
| `variables` | JSON string containing variable replacements for the prompt. Format: `{"variable_name": "value"}`. Variables in the format `{{variable_name}}` will be replaced with corresponding values. | No | - |

**Output:**
| Output | Description |
| :----- | :---------- |
| `text` | The text content of the retrieved prompt with variables replaced (if variables were provided). Can be directly used as input for Dify's LLM node prompts. |
| `json` | Metadata about the retrieved prompt (in JSON format). Includes prompt name, version, label, creation date, etc. When variables are applied, also includes `processed_prompt`, and `variables_applied` fields. |

**Example Output (with variable replacement):**
```json
{
  "text": "Hello world! Please respond in English style.",
  "files": [],
  "json": [
    {
      "commitMessage": null,
      "config": {},
      "createdAt": "2025-05-01T08:28:14.098Z",
      "createdBy": "cma4qy3fh0003lc084jrek7gk",
      "id": "2d9adb37-f6f0-4ae0-9bd8-4685e35524c8",
      "isActive": null,
      "labels": [
        "production",
        "latest"
      ],
      "name": "greeting_prompt",
      "projectId": "cma4zpa1j0009lc08oe82jnoy",
      "prompt": "{{greeting}} world! Please respond in {{language}} style.",
      "processed_prompt": "Hello world! Please respond in English style.",
      "original_prompt": "{{greeting}} world! Please respond in {{language}} style.",
      "variables_applied": true,
      "resolutionGraph": null,
      "tags": [
        "greeting",
        "test"
      ],
      "type": "text",
      "updatedAt": "2025-05-01T08:28:14.098Z",
      "version": 2
    }
  ]
}
```

**Variable Replacement Example:**
If your Langfuse prompt contains: `"Hello {{name}}, welcome to {{country}}!"`
And you provide variables: `{"name": "John", "country": "Japan"}`
The output will be: `"Hello John, welcome to Japan!"`

**Folder Hierarchy Support:**
Prompt names with slashes like `folder/prompt-name` work seamlessly.

**Limitations:**
* The `label` and `version` parameters cannot be specified simultaneously.
* Only supports prompts of type 'text' on Langfuse. Returns a custom error if the requested prompt is of type 'chat'.
* Variables must be provided in JSON format as a string. Invalid JSON will result in an error.
* Variables not found in the provided JSON will remain unchanged in the format `{{variable_name}}`.

### Search Prompts Tool

Searches for prompts managed in Langfuse under various conditions and retrieves them as a list.

**Purpose:**
To search for prompts registered in Langfuse from within Dify workflows and discover available prompts.

**Main Features:**
* Filtering search by labels and tags.
* Filtering by last update date.
* Pagination support.

**Input Parameters:**
| Parameter | Description | Type |
| :-------- | :---------- | :--- |
| `name` | Name of the prompt to search for. | String |
| `label` | Label to use as search criteria. | String |
| `tag` | Tag to use as search criteria. | String |
| `page` | Page number of search results to retrieve (for pagination, starts from 1) | Number |
| `limit` | Maximum number of prompts to retrieve per page. | Number |
| `fromUpdatedAt` | Search for prompts created or updated after this date (ISO 8601 format, e.g., 2023-01-01T00:00:00Z). | String (ISO 8601) |
| `toUpdatedAt` | Search for prompts created or updated before this date (ISO 8601 format, e.g., 2023-12-31T23:59:59Z). | String (ISO 8601) |

**Output:**
| Output | Description |
| :----- | :---------- |
| `json` | List of JSON objects containing metadata of prompts matching the search criteria (name, version information, labels, tags, creation date, update date, etc.). |

**Example Output:**
```json
{
  "text": "",
  "files": [],
  "json": [
    {
      "labels": [
        "noperiod"
      ],
      "lastConfig": {},
      "lastUpdatedAt": "2025-05-07T00:06:55.081Z",
      "name": "call_hello_at_the_end",
      "tags": [
        "joke",
        "test"
      ],
      "versions": [
        1
      ]
    },
    {
      "labels": [
        "latest",
        "production"
      ],
      "lastConfig": {},
      "lastUpdatedAt": "2025-05-02T00:10:27.220Z",
      "name": "good_engineer_test",
      "tags": [
        "test"
      ],
      "versions": [
        1
      ]
    }
  ]
}
```

**Limitations:**
* This tool is for discovering and identifying prompts only, and the metadata list in search results does not include the actual prompt text content. Use the Get Prompt tool to retrieve prompt content.

### Update Prompt Tool

Creates a new version of a prompt managed in Langfuse and sets tags and labels.

**Purpose:**
To create a new version of a prompt stored and managed on Langfuse and set metadata (tags and labels).

**Main Features:**
* Creates a new version of an existing prompt.
* Sets tags for the prompt and labels for the new version.
* Manages change history with commit messages.

**Input Parameters:**
| Parameter | Description | Required |
| :-------- | :---------- | :------- |
| `name` | Name of the prompt to update. Only supports prompts of type 'text'. | Yes |
| `prompt` | Content of the prompt to update. | Yes |
| `labels` | Comma-separated list of labels for this prompt version. | No |
| `tag` | A single tag to apply to all versions of this prompt. | No |
| `commitMessage` | Commit message for this prompt version. | No |

**Output:**
| Output | Description |
| :----- | :---------- |
| `text` | Version number of the created prompt. |
| `json` | Metadata of the created prompt version (in JSON format). Includes prompt name, version, labels, tags, creation date, etc. |

**Example Output:**
```json
{
  "text": "3",
  "files": [],
  "json": [
    {
      "commitMessage": null,
      "config": {},
      "createdAt": "2025-05-14T07:01:34.828Z",
      "createdBy": "API",
      "id": "d1f66313-9960-4e3c-8a88-8e2c19ad31e6",
      "isActive": null,
      "labels": [
        "production",
        "latest"
      ],
      "name": "say_hello_at_the_end",
      "projectId": "cma4zpa1j0009lc08oe82jnoy",
      "prompt": "Please add \"Hello.\" at the end of your answer.",
      "tags": [
        "joke",
        "test"
      ],
      "type": "text",
      "updatedAt": "2025-05-14T07:01:34.828Z",
      "version": 3
    }
  ]
}
```

**Limitations:**
* Only supports prompts of type 'text' on Langfuse.
* When setting multiple labels, they must be comma-separated (e.g., `production,latest`).
* Only one tag can be set per prompt.

## License

This project is released under the MIT License.
For details, please see the `LICENSE` file in the repository.
