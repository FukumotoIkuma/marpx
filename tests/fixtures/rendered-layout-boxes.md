---
marp: true
style: |
  .quote-box {
    background: #f8f4ff;
    border-left: 5px solid #4a3a8a;
    padding: 0.6em 1em;
    border-radius: 4px;
    margin: 0.5em 0;
    font-style: italic;
    color: #2a1a5a;
  }
  .pipeline {
    background: #eef2ff;
    border-left: 4px solid #1a2a4a;
    padding: 0.5em 1em;
    border-radius: 4px;
    font-size: 0.9em;
    margin: 0.5em 0;
  }
  .flow-chart {
    background: #eef2ff;
    border-left: 4px solid #1a2a4a;
    padding: 0.8em 1.2em;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    text-align: center;
    margin: 0.5em 0;
    white-space: pre;
  }
  .checklist {
    list-style: none;
    padding-left: 0.5em;
  }
  .checklist li::before {
    content: "☐ ";
    color: #1a2a4a;
    font-weight: bold;
  }
---

# Decorated Layouts

<div class="quote-box">
<strong>あああああああ</strong>

- ああああああああああああああ
- あああああああああああああああ
- <strong>あああああああああああああああ</strong>
</div>

<div class="pipeline">
Capture rendered decoration instead of matching individual CSS class names.
</div>

<div class="flow-chart">Input
|
v
Output</div>

<ul class="checklist">
  <li>First item</li>
  <li>Second item</li>
</ul>
