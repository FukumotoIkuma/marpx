# コントリビューション

marpx へのコントリビューションを歓迎します！

## 開発環境

```bash
git clone https://github.com/FukumotoIkuma/marpx.git
cd marpx
uv sync
uv run playwright install chromium
```

`src/marpx/extraction/extract_slides.bundle.js` は Playwright が実行時に読む静的 bundle です。
抽出ロジック本体は `src/marpx/extraction/js/` 配下の分割ソースにあります。

- `pytest` 実行時は、分割ソースが bundle より新しければ自動で再生成されます
- CLI で分割ソースを反映したい場合は `uv run marpx --dev ...` を使います
- ライブラリ import 時には `node` / `npm` は実行されません
- bundle を手動で再生成したい場合:

```bash
cd src/marpx/extraction/js
npm run build
```

## テスト

```bash
uv run pytest tests/ -x -q
```

## コードスタイル

[ruff](https://docs.astral.sh/ruff/) を使用しています。

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## プルリクエスト

1. フォークしてブランチを作成
2. テストを書く・通す
3. ruff check / format が通ることを確認
4. PR を作成
