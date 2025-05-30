# Dify Langfuse 連携プラグイン

**Author** [gao-ai-com](https://github.com/gao-ai-com)
**Version:** 0.0.1
**Type:** tool

## 概要

このリポジトリは、LLM アプリケーション開発プラットフォームである [Dify](https://dify.ai/) 上で、LLM オブザーバビリティ＆プロンプト管理ツール [Langfuse](https://langfuse.com/) と連携するためのカスタムプラグインです。

このプラグインを利用することで、Dify のワークフロー内から Langfuse で管理されているプロンプトを直接利用したり、検索したりすることが可能になり、プロンプト管理の効率化とアプリケーション開発の品質向上を支援します。

## 主な機能

本プラグインは、Dify のカスタムツールとして以下の3つの主要な機能を提供します。

* **Get Prompt ツール:** Langfuse で管理されている特定のプロンプト（テキストタイプ）を取得し、Dify のワークフローで使用します。
* **Search Prompts ツール:** Langfuse 内のプロンプトを様々な条件で検索し、利用可能なプロンプトを発見します。
* **Update Prompt ツール:** Langfuse で管理されているプロンプトの新しいバージョンを作成し、タグやラベルを設定します。

## インストール方法
1. **Dify のプラグイン管理ページへ移動**: Dify にログイン後、画面右上にある[プラグイン]からプラグイン管理ページを開き、[プラグインをインストールする]、[GitHub]を続けてクリックします。
2. **リポジトリアドレスの入力**: インストールするプラグインの GitHub リポジトリアドレスを入力するフィールドが表示されますので、ここに、https://github.com/gao-ai-com/dify-plugin-langfuse を入力します。
3. **バージョンとパッケージファイルの選択・インストール**: リポジトリが認識されると、利用可能なバージョン番号とパッケージを選択する画面に進みます。適切なものを選択し、指示に従ってインストールを完了してください。

## 使い方

### Get Prompt ツール

Langfuse 上で管理されている特定のプロンプトの本文を Dify のワークフロー内に読み込みます。

**目的:**
Langfuse 上に保存・管理されているプロンプトの本文を、Dify のワークフローで利用可能な形で取得すること。

**主な機能:**
* プロンプト本文をプロンプト名を指定して取得します。
* ラベルやバージョンの指定が可能です。

**入力パラメータ:**
| パラメータ名 | 説明                                 | 必須 | デフォルト値     |
| :--------- | :---------------------------------- | :--- | :------------- |
| `name`       | Langfuse で管理されているプロンプトの一意な名前。                       | はい | -             |
| `label`      | 取得したいプロンプトバージョンに付与されたラベル。`version` との同時指定不可。 | いいえ | production     |
| `version`    | 取得したいプロンプトの特定のバージョン番号。`label` との同時指定不可。     | いいえ | - |

**出力:**
| 出力名 | 説明                                                                   |
| :----- | :--------------------------------------------------------------------- |
| `text` | 取得したプロンプトの本文テキスト。Dify の LLM ノードのプロンプト入力に直接利用できます。 |
| `json` | 取得したプロンプトに関するメタデータ（JSON 形式）。プロンプト名、バージョン、ラベル、作成日などが含まれます。 |

**出力例:**
```json
{
  "text": "回答の一番最後に「Hello.」とつけてください",
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
      "name": "say_hello_at_the_end",
      "projectId": "cma4zpa1j0009lc08oe82jnoy",
      "prompt": "回答の一番最後に「Hello.」とつけてください",
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

**制限事項:**
* `label` パラメータと `version` パラメータの同時指定はできません。
* Langfuse 上でタイプが text のプロンプトのみ対応しています。取得しようとしたプロンプトが chat タイプだった場合、非対応である旨のカスタムエラーを返します。

### Search Prompts ツール

Langfuse で管理されているプロンプトを様々な条件で検索し、リストとして取得します。

**目的:**
Dify のワークフロー内から Langfuse に登録されているプロンプトを検索し、利用可能なプロンプトを発見・特定すること。

**主な機能:**
* ラベルやタグによるフィルタリング検索。
* 最終更新日によるフィルタリング。
* ページネーション対応。

**入力パラメータ:**
| パラメータ名 | 説明                                                     | 型 |
| :--------- | :------------------------------------------------------ | :- |
| `name`      | 検索したいプロンプト名。 | 文字列 |
| `label`     | 検索条件とするラベル。 | 文字列 |
| `tag`       | 検索条件とするタグ。                             | 文字列 |
| `page`       | 取得したい検索結果のページ番号 (ページネーション用、1から開始)         | 数値 |
| `limit`      | 1ページあたりに取得するプロンプトの最大数。     | 数値 |
| `fromUpdatedAt` | プロンプトの作成日または最終更新日がこの日付以降のものを検索（ISO 8601形式 例: 2023-01-01T00:00:00Z）。 | 文字列(ISO 8601形式) |
| `toUpdatedAt` | プロンプトの作成日または最終更新日がこの日付以前のものを検索（ISO 8601形式 例: 2023-12-31T23:59:59Z）。 | 文字列(ISO 8601形式) |

**出力:**
| 出力名    | 説明                                                      |
| :------- | :------------------------------------------------------- |
| `json` | 検索条件に一致したプロンプトのメタデータ（名前、バージョン情報、ラベル、タグ、作成日、更新日など）を含む JSON オブジェクトのリスト。 |

**出力例:**
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
      "name": "say_lo_at_the_end",
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

**制限事項:**
* このツールは、あくまでプロンプトを発見・特定するためのものであり、検索結果のメタデータリストにはプロンプトの実際の本文テキストは含まれません。プロンプト本文の取得には Get Prompt ツールを使用してください。

### Update Prompt ツール

Langfuse で管理されているプロンプトの新しいバージョンを作成し、タグやラベルを設定します。

**目的:**
Langfuse 上に保存・管理されているプロンプトの新しいバージョンを作成し、メタデータ（タグやラベル）を設定すること。

**主な機能:**
* 既存のプロンプトの新しいバージョンを作成します。
* プロンプトのタグや新しいバージョンのラベルを設定できます。
* コミットメッセージを付けて変更履歴を管理できます。

**入力パラメータ:**
| パラメータ名 | 説明                                 | 必須 |
| :--------- | :---------------------------------- | :--- |
| `name`       | 更新するプロンプトの名前。プロンプトタイプは'text'のみです。 | はい |
| `prompt`     | 更新するプロンプトの内容。 | はい |
| `labels`     | このプロンプトバージョンのカンマ区切りのラベルのリスト。 | いいえ |
| `tag`        | このプロンプトのすべてのバージョンに適用する1つのタグ。 | いいえ |
| `commitMessage` | このプロンプトバージョンのコミットメッセージ。 | いいえ |

**出力:**
| 出力名 | 説明                                                                   |
| :----- | :--------------------------------------------------------------------- |
| `text` | 作成されたプロンプトのバージョン番号。 |
| `json` | 作成されたプロンプトバージョンのメタデータ（JSON 形式）。プロンプト名、バージョン、ラベル、タグ、作成日などが含まれます。 |

**出力例:**
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

**制限事項:**
* Langfuse 上でタイプが text のプロンプトのみ対応しています。
* 複数のラベルを設定する場合は、カンマ区切りで入力する必要があります（例：`production,latest`）。
* 1つのプロンプトに設定できるタグは1つのみです。

## ライセンス

このプロジェクトは MIT License の下で公開されています。
詳細については、リポジトリ内の `LICENSE` ファイルをご覧ください。
