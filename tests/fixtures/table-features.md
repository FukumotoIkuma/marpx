---
marp: true
---

<!-- Slide 1: test_transparent_table_cell_background_does_not_become_alpha_zero -->

<style scoped>
table { color: white; }
</style>

| A | B |
|---|---|
| 1 | 2 |

---

<!-- Slide 2: test_background_split_ratio_is_extracted -->

![bg left:40%](https://picsum.photos/800/600)

# Slide

---

<!-- Slide 3: test_multiple_background_images_keep_distinct_boxes -->

![bg](https://picsum.photos/1280/720?random=1)
![bg](https://picsum.photos/1280/720?random=2)

# Slide

---

<!-- Slide 4: test_table_text_does_not_inherit_hidden_svg_opacity -->

<style scoped>
th { color: white; background: linear-gradient(135deg, #3b82f6, #2563eb); }
</style>

| Feature | Free |
|---------|:----:|
| Users | 5 |

---

<!-- Slide 5: test_table_cell_resolves_gradient_and_row_background_styles -->

<style scoped>
th { color: white; background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 14px 16px; }
td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }
tbody tr:nth-child(odd) { background: #f1f5f9; }
</style>

| Feature | Free |
|---------|:----:|
| Users | 5 |

---

<!-- Slide 6: test_parent_opacity_propagates_to_text_decoration_image_and_table -->

<div style="opacity: 0.6">
  <p style="color: rgb(10, 20, 30)">Alpha text</p>
  <div style="background: rgba(255, 0, 0, 0.5); padding: 12px">Panel</div>
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR42mP4z8AAAwEBAMn+ku8AAAAASUVORK5CYII=" />
  <table>
    <tr><td style="background: rgba(0, 128, 0, 0.5)">Cell</td></tr>
  </table>
</div>
