---
marp: true
style: |
  @keyframes biolumPulse {
    0%, 100% { filter: blur(0px); }
    50% { filter: blur(1px); }
  }
  .animated-box {
    animation: biolumPulse 4s ease-in-out infinite;
    padding: 1em;
  }
---

# Animated Filter Test

<div class="animated-box">

This text has a CSS animation that transitions `filter: blur()`.
Without freezing animations, Playwright may capture a mid-flight
computed style like `filter: blur(0.008px)`, causing this element
to be classified as UNSUPPORTED.

</div>
