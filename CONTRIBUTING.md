# コントリビューション

marpx へのコントリビューションを歓迎します！

## 開発環境

```bash
git clone https://github.com/FukumotoIkuma/marpx.git
cd marpx
uv sync
uv run playwright install chromium
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
