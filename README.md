# UTgroup - 解析 & 実験データ分析リポジトリ

本リポジトリは、数値シミュレーション（COMSOL, ComWAVE, JMAG）の解析データおよび実験計測データの処理・分析・可視化を統合管理するためのプロジェクトです。

---

## 📋 ディレクトリ構成と概要

本プロジェクトは各種数値解析ツールおよび実験系ごとにディレクトリが分かれています。

| ディレクトリ | 概要 | 主な内容・ノートブック |
| :--- | :--- | :--- |
| **`COMSOL/`** | COMSOL Multiphysics 解析データ処理 | `AnalysisBiasField.ipynb`<br>・電流変化に伴う励磁磁場・磁束密度分布の解析 |
| **`ComWAVE/`** | ComWAVE（超音波・弾性波解析）データ処理 | `test.ipynb`<br>・解析用テンプレート |
| **`Experiment/`** | 実験計測データ処理 | `AnalysisMagnetostrictive.ipynb`<br>・磁気ひずみ（歪-励磁磁場曲線）のデータ解析 |
| **`JMAG/`** | JMAG 電磁界解析データ処理 | `test.ipynb`<br>・解析用テンプレート |

---

## 🚀 セットアップ手順（フォルダ構造の作成）

本リポジトリでは、大容量データや解析結果出力先（`source/`, `results/`, `MasterData/` など）は Git の追跡対象外 (`.gitignore`) となっています。

新規にリポジトリをクローンした後は、環境に合わせて以下のスクリプトを実行し、必要なフォルダ構造を一括作成してください。

### 実行方法

#### Windows環境
`create_folders.bat` をダブルクリックして実行するか、コマンドプロンプト等から実行します。

```cmd
create_folders.bat
```

#### macOS / Linux環境
ターミナルから `create_folders.sh` を実行します。

```bash
./create_folders.sh
```

またはターミナルで直に以下のコマンドを実行することもできます：

```bash
mkdir -p COMSOL/{source,results} ComWAVE/{source,results} Experiment/{source/MasterData,results} JMAG/{source,results}
```

### 生成されるディレクトリ構造

```text
UTgroup/
├── COMSOL/
│   ├── source/      # COMSOL 入力データ配置先 (Git管理外)
│   └── results/     # COMSOL 解析結果出力先 (Git管理外)
├── ComWAVE/
│   ├── source/      # ComWAVE 入力データ配置先 (Git管理外)
│   └── results/     # ComWAVE 解析結果出力先 (Git管理外)
├── Experiment/
│   ├── source/      # 実験データ配置先 (Git管理外)
│   │   └── MasterData/ # マスターデータ配置先 (Git管理外)
│   └── results/     # 実験データ解析結果出力先 (Git管理外)
├── JMAG/
│   ├── source/      # JMAG 入力データ配置先 (Git管理外)
│   └── results/     # JMAG 解析結果出力先 (Git管理外)
```

---

## 📂 データ運用ルール (`.gitignore`)

1. **入力データ (`source/`, `MasterData/`)**
   - シミュレーション結果データや実験の生データファイル（CSV, TXT, Excel等）は、各ディレクトリの `source/` または `MasterData/` に配置して解析を行ってください。
2. **出力結果 (`results/`)**
   - Jupyter Notebook等で生成されるグラフ画像や解析出力ファイルは `results/` ディレクトリ内に保存される仕様になっています。
3. **バージョン管理**
   - `source/` および `results/` ディレクトリ配下のファイルは Git で管理されません。必要なプログラム（`.ipynb`, `.py`等）および設定ファイルのみを Git 管理します。

---

## 📜 ライセンス

本プロジェクトは [MIT License](LICENSE) の下で公開されています。