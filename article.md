---
title: "Marp → 編集可能な PowerPoint に変換するツールを AI で作った"
emoji: "📊"
type: "tech"
topics: ["marp", "powerpoint", "python", "ai", "cli"]
published: false
---

> この記事は AI (Claude) を活用して執筆しています。

## 動機

最近、AI でスライドを作るなら Marp が都合いい、という流れをよく見かけます。Markdown で書けて、バージョン管理できて、AI との相性も抜群。

ただ現実には、**提出物が PowerPoint 指定**だったり、**チームでの共同編集が PowerPoint 前提**だったり、パワポのエコシステムからはまだ抜け出せません。

じゃあ Marp → PPTX に変換すればいい。でも既存の選択肢は：

- **marp-cli `--pptx`** → 全スライドが PNG 画像。テキスト編集不可
- **marp-cli `--pptx-editable`** → LibreOffice が必要。テーブルがバラバラのシェイプに分解される

どちらも「編集可能なネイティブ PowerPoint」には程遠い。

調べても満足いくツールが出てこなかったので、**作りました。もちろん AI で。**

## marpx

https://github.com/FukumotoIkuma/marpx

Marp の HTML レンダリングから、ネイティブな PowerPoint 要素を直接生成します。

**できること：**

- テキスト・見出し・リストがそのまま編集可能
- テーブルがネイティブ PowerPoint テーブル（colspan / rowspan も対応）
- 背景画像、スピーカーノート、ヘッダー / フッター / ページ番号
- SVG は `rsvg-convert` でラスタライズ、数式は高解像度フォールバック
- CJK フォント含む 50 以上のフォントマッピング

## 使ってみる

```bash
git clone https://github.com/FukumotoIkuma/marpx.git
cd marpx
uv sync
uv run playwright install chromium

# SVG を含むスライドを変換する場合は librsvg が必要
# macOS: brew install librsvg
# Ubuntu: sudo apt-get install librsvg2-bin

# 変換
uv run marpx your-slide.md -o output.pptx
```

リポジトリに `example.md` が入っているので、まずはこれで試すのが手っ取り早いです：

```bash
uv run marpx example.md
```

## 正直なところ

割と気に入っていますが、**完璧ではありません。**

Marp が出力する HTML / CSS のすべてのパターンを網羅的に解析しているわけではなく、自分が実際に使って観測したケースに対応しているだけです。見たことのないレイアウトやスタイルに出会うと、変換が崩れる可能性は普通にあります。

Issue や PR はいつでも歓迎です。対応ケースが増えれば、ツール全体の品質が上がります。

## 技術スタック

| 技術 | 役割 |
|------|------|
| marp-cli | Markdown → HTML |
| Playwright (Chromium) | DOM 構造・算出スタイル・座標の抽出 |
| Pydantic v2 | 中間データモデル |
| python-pptx | PPTX 生成 |
| librsvg (rsvg-convert) | SVG → PNG ラスタライズ |

要するに「ブラウザで Marp をレンダリング → DOM を全部読み取る → PowerPoint のシェイプに変換」という力技です。AI さいきょー。
