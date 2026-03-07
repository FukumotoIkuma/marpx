---
marp: true
theme: default
size: 16:9
paginate: true
header: marpx デモ
footer: github.com/FukumotoIkuma/marpx
---

<!-- Slide 1: タイトルスライド / feature: global directives (paginate, header, footer) -->

# marpx Feature Showcase

**Marp Markdown → 編集可能な PowerPoint** への変換デモです。

- テキスト・リスト・表・コードブロックがネイティブ PPTX 要素として出力されます
- 背景画像・スピーカーノート・ディレクティブにも対応しています
- Python 3.11 以上 / Node.js 18 以上で動作します

<!-- note: このノートはスピーカーノートとして PPTX のノートペインに出力されます。変換後に PowerPoint で確認してください。 -->

---

<!-- Slide 2: テキスト装飾 / feature: inline formatting -->

## テキスト装飾 — Inline Formatting

通常の段落テキストです。English and 日本語 can coexist on the same line without broken spacing.

**太字 (bold)**、*斜体 (italic)*、`インラインコード (inline code)` がそれぞれネイティブの書式として出力されます。

複数の段落は独立した段落として保持されます。
改行を明示的に入れても、段落の区切りは維持されます。

> これは Markdown ブロック引用です。引用ブロックとして抽出・描画されます。
> 2行目も同じ引用ブロック内に収まります。

---

<!-- Slide 3: 見出しレベル / feature: headings h1-h4 -->

## 見出しレベル — Headings

### h3 見出し — サブセクション

#### h4 見出し — より深いレベル

見出しは h1 から h4 まで、フォントサイズと太さの差で区別されます。PowerPoint 上でも同様の階層構造が維持されます。

---

<!-- Slide 4: リスト / feature: unordered list, ordered list, nesting -->

## リスト — Lists

- 箇条書きの第1レベル
- **強調テキスト**を含む項目と [リンク](https://github.com/FukumotoIkuma/marpx)
  - 第2レベルのネスト
  - もう一つの第2レベル
    - 第3レベルのネスト
- 第1レベルに戻る

1. 番号付きリストの第1項
2. 番号付きリストの第2項
   1. ネストされた番号付き項目
   2. もう一つのネスト項目
3. 番号付きリストの第3項

---

<!-- Slide 5: テーブル（シンプル）/ feature: native table -->

## テーブル — Simple Table

| 機能 | 対応状況 | 備考 |
| --- | :---: | --- |
| 見出し (h1〜h6) | 対応 | フォントサイズで区別 |
| 箇条書き・番号付きリスト | 対応 | ネスト段落レベルで管理 |
| コードブロック | 対応 | 等幅フォントで描画 |
| ネイティブテーブル | 対応 | colspan / rowspan も対応 |
| 背景画像 | 対応 | `![bg]`, `![bg left/right]` |
| スピーカーノート | 対応 | PPTX ノートペインに出力 |
| 数式 (MathJax) | フォールバック | 高解像度画像として配置 |

---

<!-- Slide 6: テーブル（結合セル）/ feature: colspan and rowspan -->

## テーブル — Merged Cells (colspan / rowspan)

<table>
  <tr>
    <th>カテゴリ</th>
    <th>項目</th>
    <th>ステータス</th>
    <th>備考</th>
  </tr>
  <tr>
    <td rowspan="2">テキスト系</td>
    <td>見出し・段落</td>
    <td>ネイティブ</td>
    <td>rowspan で結合</td>
  </tr>
  <tr>
    <td>リスト</td>
    <td>ネイティブ</td>
    <td>段落レベルで管理</td>
  </tr>
  <tr>
    <td colspan="2">画像・背景（colspan 結合）</td>
    <td>ネイティブ</td>
    <td>z-order 管理済み</td>
  </tr>
</table>

---

<!-- Slide 7: コードブロック / feature: fenced code block -->

## コードブロック — Code Block

```python
from dataclasses import dataclass

@dataclass
class Slide:
    title: str
    body: str

def convert(input_path: str, output_path: str) -> None:
    """Marp Markdown を PPTX に変換します。"""
    slides = extract_slides(input_path)
    build_pptx(slides, output_path)
```

インラインコードも区別されます: `uv run marpx example.md -o example.pptx`

---

<!-- Slide 8: 画像（通常）/ feature: inline image with width directive -->

## 画像 — Inline Image

![w:820](./images/chart-states.png)

画像は指定した幅でアスペクト比を維持しながら配置されます。PNG・SVG どちらも対応しています。

---

<!-- Slide 9: 背景画像（デフォルト）/ feature: ![bg] default cover -->

## 背景画像 — `![bg]`

![bg](./images/chart-comparison.png)

`![bg]` はスライド全体を背景としてカバーします。前景テキストは背景の上に重なります。

---

<!-- Slide 10: 背景画像（contain）/ feature: ![bg contain] -->

## 背景画像 — `![bg contain]`

![bg contain](./images/diagram-pipeline.svg)

`![bg contain]` は画像全体が見えるよう、トリミングせずに背景に収めます。

---

<!-- Slide 11: 背景画像（右分割）/ feature: ![bg right] split layout -->

## 背景画像 — `![bg right]` 分割レイアウト

![bg right](./images/diagram-network.svg)

`![bg right]` を使うと、スライド右半分に背景画像、左半分にコンテンツというレイアウトになります。

- コンテンツは左側に収まります
- 背景画像は右側に表示されます
- スライドサイズは 16:9 のままです

<!-- note: 背景分割レイアウトのスライドです。左側のテキストエリアと右側の背景画像の境界を確認してください。 -->

---

<!-- Slide 12: ディレクティブ上書き / feature: per-slide directive override -->

## ディレクティブ — 上書き (Per-slide Override)
<!-- _header: カスタムヘッダー -->
<!-- _footer: カスタムフッター -->
<!-- _paginate: false -->

このスライドはヘッダー・フッター・ページ番号をスライド単位で上書きしています。

- ヘッダーが「カスタムヘッダー」に変わっています
- フッターが「カスタムフッター」に変わっています
- ページ番号が非表示になっています

`<!-- _paginate: false -->` のように `_` プレフィックスを付けると、そのスライドのみに適用されます。

<!-- note: ディレクティブの上書き確認用スライドです。ヘッダー・フッターの変化とページ番号の非表示を PPTX で確認してください。 -->

---

<!-- Slide 13: 背景色 / feature: solid background color -->

## 背景色 — Solid Background Color
<!-- _backgroundColor: #1e3a5f -->
<!-- _color: #f0f8ff -->
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: false -->

単色背景はネイティブの PowerPoint スライド背景として設定されます。

テキストの色も `_color` ディレクティブで制御できます。グラデーションはフォールバック対象となります。

---

<!-- Slide 14: まとめ / feature: summary slide with mixed content -->

## まとめ — What marpx Converts Natively

| 要素 | PPTX での扱い |
| --- | --- |
| 見出し・段落・引用 | ネイティブテキストボックス |
| 箇条書き・番号リスト | ネイティブ段落レベル |
| コードブロック | 等幅フォントテキストボックス |
| テーブル (colspan/rowspan) | ネイティブ `<a:tbl>` |
| PNG / SVG 画像 | 画像シェイプ |
| 背景画像 | ピクチャーシェイプ (z-order 管理) |
| スピーカーノート | PPTX ノートペイン |
| ページ番号・ヘッダー・フッター | テキストボックス |

```bash
uv run marpx example.md -o example.pptx
```

<!-- note: まとめスライドです。変換結果の全体的な品質をここで総評してください。 -->
