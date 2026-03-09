# marpx

[![CI](https://github.com/FukumotoIkuma/marpx/actions/workflows/ci.yml/badge.svg)](https://github.com/FukumotoIkuma/marpx/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Marp Markdown スライドを編集可能な PowerPoint プレゼンテーションに変換します。

## なぜこのツール？

Marp CLI には 2 つの PPTX エクスポートモードがありますが、どちらも完全に編集可能なネイティブ PowerPoint を出力しません。

- **標準 `--pptx`** -- 各スライドを 1 枚の PNG 画像としてレンダリング。テキスト編集不可、テーブル・リスト・見出しもすべてラスタライズされます。
- **実験的 `--pptx-editable`** -- LibreOffice のインストールが必要。テキストボックスは編集可能になりますが、テーブルは個別のテキストボックスとフリーフォームシェイプに分解され（ネイティブ `<a:tbl>` ではない）、箇条書きのセマンティック構造が失われ、シェイプ数が過剰になります。

**marpx** は Marp の HTML レンダリングからネイティブ PowerPoint 要素を直接生成します。ネイティブテーブル、段落レベル付き箇条書き、適切な見出しなど、LibreOffice なしで実現します。

## 前提条件

- Python >= 3.11
- Node.js >= 18（marp-cli を npx 経由で使用）
- npm / npx
- librsvg（`rsvg-convert`） -- SVG 画像サポート用（オプション）
  - macOS: `brew install librsvg`
  - Debian/Ubuntu: `sudo apt-get install librsvg2-bin`

## インストール

```bash
git clone https://github.com/FukumotoIkuma/marpx.git
cd marpx
uv sync
uv run playwright install chromium
```

## 使い方

```bash
uv run marpx input.md -o output.pptx
```

`--output` を省略した場合、入力ファイル名の拡張子を `.pptx` に変えたパスに出力されます。

リポジトリに含まれる `example.md` で対応機能を確認できます:

```bash
uv run marpx example.md
```

### CLI オプション

| オプション | 説明 |
|-----------|------|
| `-o`, `--output` | 出力 PPTX ファイルパス（デフォルト: 入力ファイル名 + `.pptx`） |
| `--theme` | Marp テーマ名または CSS ファイルパス |
| `--fallback-mode` | `subtree`（デフォルト）または `slide` -- 非対応コンテンツのフォールバック粒度 |
| `--prefer-editable` | 複雑なコンテンツでも編集可能シェイプを最大化 |
| `--keep-temp` | 変換後に一時ファイルを保持 |
| `-v`, `--verbose` | 詳細ログを有効化 |
| `--version` | バージョンを表示して終了 |

## 対応要素

- 見出し（h1〜h6）
- 段落
- 引用
- 順序なし・順序付きリスト（段落レベルによるネスト対応）
- コードブロック（`pre > code`）
- 画像
- テーブル（ネイティブ PowerPoint テーブル、colspan/rowspan 対応）
- 単色背景
- 背景画像（`![bg]`、`![bg contain]`、`![bg left/right]`）
- スピーカーノート
- Marp ディレクティブ: paginate（ページ番号）、header、footer
  - スライド単位のオーバーライド対応（例: `<!-- _paginate: false -->`）

## フォント処理

CSS フォントから PowerPoint へのマッピングでフォントの忠実性を維持します。

- **システムフォント**: Windows / macOS で一般的なフォント（Calibri、Segoe UI、Helvetica Neue、Avenir など）はそのまま PowerPoint に渡されます。
- **CJK フォント**: Yu Gothic、Meiryo、Hiragino Sans、Microsoft YaHei、Malgun Gothic など、日本語・中国語・韓国語フォントに対応。
- **人気の Web フォント**: Roboto、Open Sans、Lato、Montserrat、Fira Code、Source Code Pro などはシステムにあればそのまま使用。
- **CSS 汎用ファミリー**: `sans-serif`、`serif`、`monospace`、`cursive`、`fantasy` および `system-ui`、`-apple-system` は最も近い PowerPoint フォントにマッピング。
- **Web 専用フォント**: ローカルに存在しないフォント（Inter、JetBrains Mono、Ubuntu、IBM Plex など）は視覚的に近い PowerPoint 対応フォントにマッピング。
- **不明なフォント**: そのまま渡され、PowerPoint 側のフォント置換に委ねます。

フォント埋め込みは行いません。PPTX を開くシステムにインストールされたフォントに依存します。

## フォールバックレンダリング

以下の要素はネイティブ PowerPoint シェイプに変換されず、要素単位の高品質ラスター画像（2x DPI）としてレンダリングされます。

- **数式**（MathJax） -- `<mjx-container>` 要素として検出し、2x DPI でクリアに出力
- **SVG グラフィック** -- `rsvg-convert` によるベクター→PNG ラスタライズ（SVG 画像はネイティブ画像シェイプとして、インライン SVG はフォールバック画像として配置）
- **Mermaid 図** -- コードブロックとして表示（marp-cli は Mermaid をレンダリングしないため、`mmdc` による前処理を将来対応予定）

その他の非対応要素:

- グラデーション背景
- アニメーション / トランジション
- フォント埋め込み

`--fallback-mode` オプションで、非対応サブツリーのみキャプチャ（`subtree`、デフォルト）か、スライド全体をキャプチャ（`slide`）かを選択できます。

## 制限事項と貢献

このツールは Marp が出力する HTML/CSS のすべてのパターンを網羅的に解析しているわけではありません。作者が実際に観測・テストしたケースにのみ対応しているため、未対応のレイアウトやスタイルが存在する可能性があります。

変換結果に問題を見つけた場合は、[Issue](https://github.com/FukumotoIkuma/marpx/issues) での報告や [Pull Request](https://github.com/FukumotoIkuma/marpx/pulls) を歓迎します。対応ケースを増やすことでツールの品質が向上します。

## アーキテクチャ

```
Marp MD --> marp-cli HTML --> Playwright 抽出 --> 正規化モデル --> python-pptx --> PPTX
```

1. **marp-cli** が Markdown をスタンドアロン HTML に変換（`marp_renderer.py`）。
2. **Playwright**（Chromium）が HTML を開き、各要素の DOM 構造・算出スタイル・バウンディングボックスを抽出（`extractor.py` + `extract_slides.bundle.js`）。
3. **正規化中間モデル**（Pydantic v2）がスライドコンテンツをツール非依存な形式で表現（`models.py`）。
4. **python-pptx** が正規化モデルからネイティブ PowerPoint 要素を含む PPTX を生成（`pptx_builder/` パッケージ）。

### モジュール構成

| モジュール | 責務 |
|-----------|------|
| `cli.py` | CLI エントリーポイント |
| `converter.py` | 変換パイプラインのオーケストレーション |
| `pipeline.py` | パイプラインコンテキスト・レンダリングメタデータ（`PipelineContext`, `SlideRenderInfo`, `ElementRenderInfo`） |
| `marp_renderer.py` | marp-cli による Markdown → HTML 変換 |
| `extractor.py` | Playwright による DOM 抽出・モデル構築（`SyncBrowserManager` コンテキストマネージャ含む） |
| `extract_slides.bundle.js` | 実行時に Playwright へ渡されるブラウザ内抽出バンドル |
| `extract_slides_js/` | 抽出ロジックの分割ソース（entry/runs/paragraphs/blocks/handlers など） |
| `extract_notes.js` | ブラウザ内で実行されるスピーカーノート抽出 JavaScript |
| `models.py` | Pydantic v2 による中間データモデル |
| `capabilities.py` | 要素ごとのレンダリング能力分類（`CapabilityDecision` は NamedTuple） |
| `pptx_builder/builder.py` | PPTX 生成のトップレベルオーケストレーション |
| `pptx_builder/text.py` | テキスト・見出し・リスト・コードブロックのレンダリング |
| `pptx_builder/text_grouping.py` | 隣接テキスト要素を共有テキストボックスにグループ化 |
| `pptx_builder/image.py` | 画像シェイプの生成（SVG は `svg_utils.rasterize_svg_to_png()` で直接ラスタライズ） |
| `pptx_builder/table.py` | ネイティブテーブル生成（colspan / rowspan 対応） |
| `pptx_builder/background.py` | 背景色・背景画像シェイプの生成 |
| `pptx_builder/decoration.py` | 装飾シェイプの生成 |
| `pptx_builder/directives.py` | ページ番号・ヘッダー・フッターの描画 |
| `pptx_builder/_helpers.py` | 色処理ヘルパー（RGBA→RGB、オパシティ） |
| `async_utils.py` | 非同期→同期ブリッジユーティリティ（`run_coroutine_sync()`） |
| `fallback_renderer.py` | 非対応要素のスクリーンショットフォールバック |
| `svg_utils.py` | SVG の PNG ラスタライズ（`rasterize_svg_to_png()`） |
| `fonts.py` | CSS → PowerPoint フォントマッピング |
| `image_utils.py` | 画像ソース解決ユーティリティ |
| `utils.py` | 単位変換・レイアウト・色処理 |

## 依存パッケージ

| パッケージ | 用途 |
|-----------|------|
| `python-pptx` | PowerPoint ファイル生成 |
| `playwright` | HTML パース・要素抽出用のヘッドレス Chromium |
| `click` | CLI インターフェース |
| `pydantic`（v2+） | データバリデーションと中間モデル |
| `Pillow` | フォールバックレンダリング用の画像処理 |
| `rich` | CLI 出力のフォーマット・色分け |

## 開発

```bash
uv sync
uv run pytest
```

`extract_slides.bundle.js` は実行時に静的ファイルとして読み込まれます。  
開発中は、`pytest` の入口で自動再生成されます。CLI で分割ソースを反映したい場合は `--dev` を付けて実行します。

- ライブラリ import 時には `node` / `npm` は実行されません
- 通常の CLI 実行では bundle を読むだけです
- 分割ソースを使って CLI デバッグする場合だけ `--dev` で stale bundle を自動更新します
- bundle を手で再生成したい場合は次を実行します

```bash
cd src/marpx/extract_slides_js
npm run build
```

```bash
uv run marpx --dev input.md -o output.pptx
```

リンティングとフォーマットは [ruff](https://docs.astral.sh/ruff/) を使用:

```bash
uv run ruff check src/
uv run ruff format src/
```

## ライセンス

MIT
