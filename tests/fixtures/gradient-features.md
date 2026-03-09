---
marp: true
---

<!-- Slide 1: test_inline_gradient_text_stays_native_run -->

<style scoped>
.gradient {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>

# Slide

This has <span class="gradient">gradient text</span> inline.

---

<!-- Slide 2: test_block_gradient_text_inside_decorated_block_stays_native -->

<style scoped>
.card {
  background: rgba(59,130,246,0.12);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 16px;
  padding: 24px;
  width: 320px;
}
.metric-number {
  font-size: 56px;
  font-weight: 800;
  background: linear-gradient(135deg, #60a5fa, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}
</style>

# Slide

<div class="card">
  <div class="metric-number">2.4M</div>
  <div>Monthly Active Users</div>
</div>

---

<!-- Slide 3: test_slide_linear_gradient_background_is_extracted -->

<style scoped>
section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
</style>

# Slide

---

<!-- Slide 4: test_slide_radial_gradient_background_is_extracted -->

<style scoped>
section {
  background: radial-gradient(ellipse at 30% 50%, #312e81, #0f172a 70%);
  color: white;
}
</style>

# Slide

---

<!-- Slide 5: test_linear_gradient_box_stays_native_but_gradient_text_falls_back -->

<style scoped>
.dot {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  color: white;
}
.hero-title {
  background: linear-gradient(135deg, #c7d2fe, #818cf8, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>

<div class="dot">Q1</div>
<h1 class="hero-title">Gradient Heading</h1>
