---
marp: true
---

<!-- Slide 1: test_decorated_block_with_nested_decorated_child_decomposes -->

<style scoped>
.card {
  background: white;
  border: 2px solid #bfdbfe;
  border-radius: 16px;
  padding: 24px;
}
.num {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}
</style>

# Slide

<div class="card">
  <div class="num">1</div>
  <div>Upload</div>
</div>

---

<!-- Slide 2: test_decorated_block_with_grandchild_decorated_blocks_decomposes -->

<style scoped>
.panel {
  background: #1e293b;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #334155;
}
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 120px;
}
.bar {
  width: 40px;
  border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, #3b82f6, #1d4ed8);
}
.b1 { height: 60%; }
.b2 { height: 80%; }
</style>

# Slide

<div class="panel">
  <h4>Revenue by Month</h4>
  <div class="bar-chart">
    <div class="bar b1"></div>
    <div class="bar b2"></div>
  </div>
</div>

---

<!-- Slide 3: test_presentational_list_recurses_into_children -->

<style scoped>
.stat-list { list-style: none; padding: 0; margin: 0; }
.stat-list li { display: flex; justify-content: space-between; }
.val { color: #60a5fa; font-weight: 600; }
</style>

# Slide

<ul class="stat-list">
  <li><span>Conversion</span><span class="val">12.4%</span></li>
</ul>

---

<!-- Slide 4: test_presentational_list_rows_with_decoration_extract_as_blocks -->

<style scoped>
.panel {
  background: #1e293b;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #334155;
}
.stat-list { list-style: none; padding: 0; margin: 0; }
.stat-list li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #334155;
}
.val { color: #60a5fa; font-weight: 600; }
</style>

# Slide

<div class="panel">
  <h4>Top Metrics</h4>
  <ul class="stat-list">
    <li><span>Conversion</span><span class="val">12.4%</span></li>
    <li><span>Bounce Rate</span><span class="val">23.1%</span></li>
  </ul>
</div>

---

<!-- Slide 5: test_decorated_badge_is_extracted_as_separate_element -->

<style scoped>
.card {
  background: #eef4ff;
  border: 1px solid #bfd3ff;
  border-radius: 16px;
  padding: 18px 20px;
}
.badge {
  display: inline-block;
  padding: 0.14em 0.5em;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 0.76em;
  font-weight: 700;
}
</style>

<div class="card">
  <div class="badge">Good</div>
  <p>Body text under the badge.</p>
</div>

---

<!-- Slide 6: test_decorated_card_with_table_is_shape_only_and_keeps_children -->

<style scoped>
.card {
  background: #eef4ff;
  border: 1px solid #bfd3ff;
  border-radius: 16px;
  padding: 18px 20px;
}
</style>

<div class="card">
  <h3>Left Stack</h3>
  <p>A short paragraph sits above a small table.</p>
  <table>
    <tr><th>Key</th><th>Value</th></tr>
    <tr><td>alpha</td><td>12</td></tr>
  </table>
</div>

---

<!-- Slide 7: test_figure_captions_and_image_decoration_are_extracted -->

<style scoped>
.compare-row {
  display: flex;
  gap: 20px;
}
.compare-row img {
  width: 100%;
  height: 220px;
  object-fit: contain;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}
.compare-row figcaption {
  font-size: 0.7em;
  text-align: center;
  margin-top: 8px;
}
</style>

# Slide

<div class="compare-row">
  <figure>
    <img src="./images/chart-wave-raw.png" alt="Sample image A" />
    <figcaption>Image A within the same container size</figcaption>
  </figure>
</div>

---

<!-- Slide 8: test_single_image_panel_is_extracted_as_framed_image -->

<style scoped>
.panel {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 14px 18px;
}
</style>

# Slide

<div class="panel">
  <img src="./images/diagram-network.svg" alt="Framed SVG" style="width:100%; height:420px; object-fit:contain;" />
</div>

---

<!-- Slide 9: test_absolute_block_pseudo_elements_are_extracted -->

<style scoped>
section { background: white; color: #111827; }
.timeline { position: relative; height: 40px; margin-top: 24px; }
.timeline::before { content: ''; position: absolute; top: 18px; left: 5%; right: 5%; height: 3px; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); }
.quote { position: relative; margin-top: 24px; }
.quote::before { content: '"'; position: absolute; top: -20px; left: -30px; font-size: 64px; color: rgba(59,130,246,0.5); }
.plan { position: relative; width: 220px; height: 120px; margin-top: 24px; background: #eff6ff; border-radius: 16px; }
.plan::before { content: 'POPULAR'; position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #3b82f6; color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; }
</style>

# Slide

<div class="timeline"></div>
<div class="quote">Quoted text</div>
<div class="plan"></div>
