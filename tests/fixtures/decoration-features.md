---
marp: true
---

<!-- Slide 1: test_code_block_preserves_pre_decoration -->
# Slide

<pre style="background:#f6f8fa; border:1px solid #d1d9e0; border-radius:6px; padding:16px; margin:0;"><code>alpha
beta</code></pre>

---

<!-- Slide 2: test_box_shadow_is_extracted_into_decoration -->

<style scoped>
.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow:
    inset 0 2px 8px rgba(15,23,42,0.08),
    0 8px 32px rgba(59,130,246,0.15);
}
</style>

# Slide

<div class="card">Shadow card</div>

---

<!-- Slide 3: test_scaled_block_scales_text_and_decoration_metrics -->

<style scoped>
.card {
  background: white;
  border: 2px solid #bfdbfe;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 20px;
  line-height: 1.2;
  transform: scale(1.25);
  transform-origin: top left;
}
</style>

# Slide

<div class="card">Scaled text</div>

---

<!-- Slide 4: test_complex_3d_transform_is_kept_on_native_route -->

<style scoped>
.floating {
  width: 280px;
  height: 200px;
  background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(168,85,247,0.3));
  transform: perspective(800px) rotateY(-8deg) rotateX(4deg);
}
</style>

# Slide

<div class="floating"></div>

---

<!-- Slide 5: test_decorated_block_does_not_duplicate_container_background_as_run_highlight -->

<style scoped>
.badge {
  display: inline-block;
  background: rgba(99,102,241,0.2);
  border: 1px solid #6366f1;
  border-radius: 20px;
  padding: 6px 16px;
  color: #a5b4fc;
}
</style>

<div class="badge">Now in Public Beta</div>

---

<!-- Slide 6: test_rounded_overflow_container_becomes_unsupported -->

<style scoped>
.shell {
  width: 320px;
  border-radius: 16px;
  overflow: hidden;
  background: white;
}
.shell table {
  width: 100%;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.shell td {
  background: white;
  padding: 12px 16px;
}
</style>

# Slide

<div class="shell">
  <table>
    <tr><td>Hello</td></tr>
  </table>
</div>

---

<!-- Slide 7: test_rounded_overflow_table_stays_native -->

<style scoped>
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
th { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
</style>

# Slide

| A | B |
|---|---|
| 1 | 2 |

---

<!-- Slide 8: test_backdrop_filter_block_stays_native -->

<style scoped>
.glass {
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
}
</style>

# Slide

<div class="glass">Glass panel</div>

---

<!-- Slide 9: test_decoration_only_leaf_block_is_extracted -->

<style scoped>
.bar {
  width: 40px;
  height: 100px;
  background: linear-gradient(180deg, #3b82f6, #1d4ed8);
  border-radius: 4px 4px 0 0;
}
</style>

# Slide

<div class="bar"></div>

---

<!-- Slide 10: test_flex_centered_decorated_text_sets_middle_vertical_align -->

<style scoped>
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

<div class="num">1</div>

---

<!-- Slide 11: test_flex_column_centered_child_blocks_inherit_center_alignment -->

<style scoped>
.floating {
  width: 280px;
  height: 200px;
  background: rgba(99,102,241,0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>

# Slide

<div class="floating"><div>🤖</div><div>AI Engine v3</div></div>

---

<!-- Slide 12: test_leaf_block_text_is_extracted_as_paragraph -->

# Slide

<div>Upload</div>
