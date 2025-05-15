# Dify Langfuse Integration Plugin

**Author:** Shunsaku Takagi(**Change this to GitHub link!**)
**Version:** 0.0.1
**Type:** tool

## Overview

This repository is a custom plugin for integrating [Langfuse](https://langfuse.com/), an LLM observability & prompt management tool, with [Dify](https://dify.ai/), an LLM application development platform.

By using this plugin, you can directly utilize and search prompts managed in Langfuse from within Dify workflows, supporting efficient prompt management and improving application development quality.

## Main Features

This plugin provides three main features as custom tools for Dify:

* **Get Prompt Tool:** Retrieves specific prompts (text type) managed in Langfuse for use in Dify workflows.
* **Search Prompts Tool:** Searches for prompts in Langfuse under various conditions to discover available prompts.
* **Update Prompt Tool:** Creates a new version of a prompt managed in Langfuse and sets tags and labels.

## Usage

### Get Prompt Tool

Loads the content of a specific prompt managed on Langfuse into a Dify workflow.

**Purpose:**
To retrieve the content of prompts stored and managed on Langfuse in a format usable within Dify workflows.

**Main Features:**
* Retrieves prompt content by specifying the prompt name.
* Allows specification of labels and versions.

**Input Parameters:**
| Parameter | Description | Required | Default Value |
| :-------- | :---------- | :------- | :------------ |
| `name` | Unique name of the prompt managed in Langfuse. | Yes | - |
| `label` | Label assigned to the prompt version to retrieve. Cannot be specified together with `version`. | No | production |
| `version` | Specific version number of the prompt to retrieve. Cannot be specified together with `label`. | No | - |

**Output:**
| Output | Description |
| :----- | :---------- |
| `text` | The text content of the retrieved prompt. Can be directly used as input for Dify's LLM node prompts. |
| `json` | Metadata about the retrieved prompt (in JSON format). Includes prompt name, version, label, creation date, etc. |

**Example Output:**
```json
{
  "text": "Please add 'Hello.' at the very end of your answer",
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
      "name": "call_hello_at_the_end",
      "projectId": "cma4zpa1j0009lc08oe82jnoy",
      "prompt": "Please add Hello. at the very end of your answer",
      "resolutionGraph": null,
      "tags": [
        "joke",
        "test"
      ],
      "type": "text",
      "updatedAt": "2025-05-01T08:28:14.098Z",
      "version": 2
    }
  ]
}
```

**Limitations:**
* The `label` and `version` parameters cannot be specified simultaneously.
* Only supports prompts of type 'text' on Langfuse. Returns a custom error if the requested prompt is of type 'chat'.

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
