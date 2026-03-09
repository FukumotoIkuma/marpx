---
marp: true
style: |
  section.with-pseudo::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100px;
    height: 100px;
    background-color: #ff0000;
  }
  section.with-pseudo::after {
    content: "";
    position: absolute;
    bottom: 0;
    right: 0;
    width: 80px;
    height: 80px;
    background-color: #00ff00;
  }
---

<!-- _class: with-pseudo -->

# Slide with pseudo-elements
