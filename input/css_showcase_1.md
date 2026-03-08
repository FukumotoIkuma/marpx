---
marp: true
theme: default
size: 16:9
paginate: true
style: |
  /* ============================================================
     QUANTUM COMPUTING PRESENTATION - CUSTOM CSS
     量子コンピューティングの世界
     200+ lines of advanced CSS techniques
     ============================================================ */

  /* --- Custom Properties (CSS Variables) --- */
  :root {
    --q-primary: #0ff;
    --q-secondary: #f0f;
    --q-accent: #ff0;
    --q-dark: #0a0a1a;
    --q-darker: #050510;
    --q-glass-bg: rgba(255, 255, 255, 0.08);
    --q-glass-border: rgba(255, 255, 255, 0.18);
    --q-glass-shadow: rgba(0, 0, 0, 0.45);
    --q-glow-cyan: 0 0 20px rgba(0, 255, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.3), 0 0 80px rgba(0, 255, 255, 0.1);
    --q-glow-magenta: 0 0 20px rgba(255, 0, 255, 0.6), 0 0 40px rgba(255, 0, 255, 0.3), 0 0 80px rgba(255, 0, 255, 0.1);
    --q-radius: 16px;
    --q-spacing: calc(1rem * 1.5);
    --q-font-heading: "Noto Sans JP", "Hiragino Kaku Gothic ProN", sans-serif;
    --q-font-body: "Noto Sans JP", "Hiragino Kaku Gothic ProN", sans-serif;
    --q-col-gap: calc(var(--q-spacing) * 1.2);
    --q-card-padding: calc(var(--q-spacing) * 0.9);
    --q-timeline-dot: 18px;
    --q-hex-size: 140px;
    --q-bar-height: 32px;
  }

  /* --- Base Section Reset --- */
  section {
    font-family: var(--q-font-body);
    color: #e0e0e0;
    background: var(--q-dark);
    padding: 50px 60px;
    line-height: 1.6;
  }
  section h1, section h2, section h3 {
    font-family: var(--q-font-heading);
    font-weight: 700;
    letter-spacing: 0.02em;
  }
  section a { color: var(--q-primary); text-decoration: none; }
  section strong { color: var(--q-primary); }
  section em { color: var(--q-secondary); font-style: normal; }
  section code {
    background: rgba(0,255,255,0.1);
    color: var(--q-primary);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.9em;
  }

  /* ============================================================
     SLIDE 1: TITLE - Dark quantum with glowing text
     ============================================================ */
  section.title {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background:
      radial-gradient(ellipse 120% 80% at 50% 50%, rgba(0,255,255,0.12) 0%, transparent 50%),
      radial-gradient(ellipse 80% 60% at 20% 80%, rgba(255,0,255,0.10) 0%, transparent 50%),
      radial-gradient(ellipse 60% 90% at 80% 20%, rgba(100,0,255,0.08) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, #0a0a2e 0%, #050510 100%);
    position: relative;
    overflow: hidden;
  }
  section.title::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
      radial-gradient(circle 3px at 10% 20%, rgba(0,255,255,0.8) 0%, transparent 100%),
      radial-gradient(circle 2px at 30% 70%, rgba(255,0,255,0.6) 0%, transparent 100%),
      radial-gradient(circle 2px at 70% 30%, rgba(0,255,255,0.5) 0%, transparent 100%),
      radial-gradient(circle 3px at 85% 80%, rgba(255,0,255,0.7) 0%, transparent 100%),
      radial-gradient(circle 1px at 50% 50%, rgba(255,255,0,0.4) 0%, transparent 100%),
      radial-gradient(circle 2px at 15% 85%, rgba(0,255,255,0.6) 0%, transparent 100%),
      radial-gradient(circle 1px at 90% 10%, rgba(255,0,255,0.5) 0%, transparent 100%);
    pointer-events: none;
  }
  section.title::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent 0%, var(--q-primary) 20%, var(--q-secondary) 50%, var(--q-primary) 80%, transparent 100%);
    box-shadow: 0 0 20px var(--q-primary), 0 0 40px var(--q-secondary);
  }
  section.title h1 {
    font-size: 3.2em;
    background: linear-gradient(135deg, #0ff 0%, #0af 25%, #f0f 50%, #f0a 75%, #0ff 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 0 30px rgba(0,255,255,0.4)) drop-shadow(0 0 60px rgba(255,0,255,0.2));
    margin-bottom: 0.2em;
  }
  section.title h2 {
    font-size: 1.4em;
    color: rgba(255,255,255,0.7);
    font-weight: 400;
    text-shadow: 0 0 10px rgba(0,255,255,0.3);
  }
  section.title p {
    color: rgba(255,255,255,0.5);
    font-size: 0.9em;
    margin-top: var(--q-spacing);
  }

  /* ============================================================
     SLIDE 2: AGENDA - Glassmorphism cards grid
     ============================================================ */
  section.agenda {
    background:
      linear-gradient(135deg, #0a0a2e 0%, #1a0a3e 30%, #0a1a3e 60%, #0a0a2e 100%);
    padding: 40px 50px;
  }
  section.agenda h2 {
    text-align: center;
    font-size: 2em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
    margin-bottom: calc(var(--q-spacing) * 0.8);
  }
  section.agenda .grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: calc(var(--q-col-gap) * 0.7);
    height: calc(100% - 120px);
  }
  section.agenda .card {
    background: var(--q-glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--q-glass-border);
    border-radius: var(--q-radius);
    padding: var(--q-card-padding);
    box-shadow:
      0 8px 32px var(--q-glass-shadow),
      inset 0 1px 0 rgba(255,255,255,0.1),
      0 0 0 1px rgba(0,255,255,0.05);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }
  section.agenda .card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--q-primary), var(--q-secondary), transparent);
  }
  section.agenda .card .num {
    font-size: 2em;
    font-weight: 800;
    background: linear-gradient(135deg, var(--q-primary), var(--q-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 4px;
  }
  section.agenda .card .label {
    font-size: 0.82em;
    color: rgba(255,255,255,0.85);
    line-height: 1.4;
  }

  /* ============================================================
     SLIDE 3: QUBIT - Diagonal split clip-path
     ============================================================ */
  section.split-diag {
    padding: 0;
    position: relative;
    overflow: hidden;
    color: #fff;
  }
  section.split-diag .left-panel {
    position: absolute;
    top: 0; left: 0;
    width: 55%;
    height: 100%;
    background:
      linear-gradient(160deg, #050520 0%, #0a0a3e 40%, #1a0a4e 70%, #0f0f2a 100%);
    clip-path: polygon(0 0, 100% 0, 75% 100%, 0 100%);
    padding: 60px 50px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    z-index: 2;
  }
  section.split-diag .left-panel::after {
    content: "";
    position: absolute;
    top: 20%;
    right: 10%;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, var(--q-primary), var(--q-secondary), var(--q-accent), var(--q-primary));
    opacity: 0.15;
    filter: blur(2px);
  }
  section.split-diag .right-panel {
    position: absolute;
    top: 0; right: 0;
    width: 60%;
    height: 100%;
    background:
      linear-gradient(200deg, #e8eaf6 0%, #c5cae9 30%, #9fa8da 60%, #7986cb 100%);
    clip-path: polygon(42% 0, 100% 0, 100% 100%, 17% 100%);
    padding: 60px 60px 60px 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    z-index: 1;
    color: #1a1a3a;
  }
  section.split-diag .right-panel h3 {
    color: #2a2a5a;
    border-bottom: 2px solid rgba(0,0,0,0.1);
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  section.split-diag h2 {
    font-size: 2.2em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
    margin-bottom: 16px;
  }
  section.split-diag .bloch {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 2px solid var(--q-primary);
    position: relative;
    margin: 12px auto;
    box-shadow: var(--q-glow-cyan);
  }
  section.split-diag .bloch::before {
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    width: 2px; height: 50px;
    background: linear-gradient(to bottom, var(--q-primary), var(--q-secondary));
    transform: translate(-50%, -100%) rotate(30deg);
    transform-origin: bottom center;
  }
  section.split-diag .bloch::after {
    content: "|ψ⟩";
    position: absolute;
    top: -4px; right: -24px;
    font-size: 0.7em;
    color: var(--q-primary);
    text-shadow: 0 0 6px rgba(0,255,255,0.5);
  }

  /* ============================================================
     SLIDE 4: SUPERPOSITION - Conic gradient + floating cards
     ============================================================ */
  section.superposition {
    background:
      radial-gradient(ellipse 60% 50% at 80% 20%, rgba(255,0,255,0.08) 0%, transparent 60%),
      linear-gradient(180deg, #0a0a1a 0%, #0f0a2a 50%, #0a0a1a 100%);
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "heading heading"
      "left right";
    gap: 20px;
    padding: 45px 55px;
  }
  section.superposition h2 {
    grid-area: heading;
    font-size: 2em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
    text-align: center;
  }
  section.superposition .conic-deco {
    grid-area: left;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  section.superposition .conic-deco .wheel {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: conic-gradient(
      from 0deg,
      rgba(0,255,255,0.9) 0deg,
      rgba(0,100,255,0.7) 45deg,
      rgba(100,0,255,0.7) 90deg,
      rgba(255,0,255,0.9) 135deg,
      rgba(255,0,100,0.7) 180deg,
      rgba(255,100,0,0.7) 225deg,
      rgba(255,255,0,0.9) 270deg,
      rgba(0,255,100,0.7) 315deg,
      rgba(0,255,255,0.9) 360deg
    );
    box-shadow:
      0 0 30px rgba(0,255,255,0.3),
      0 0 60px rgba(255,0,255,0.2),
      inset 0 0 40px rgba(0,0,0,0.5);
    position: relative;
  }
  section.superposition .conic-deco .wheel::after {
    content: "α|0⟩ + β|1⟩";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0,0,0,0.85);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 1.1em;
    color: var(--q-primary);
    text-shadow: 0 0 8px rgba(0,255,255,0.5);
    white-space: nowrap;
  }
  section.superposition .conic-deco .caption {
    text-align: center;
    margin-top: 12px;
    font-size: 0.8em;
    color: rgba(255,255,255,0.5);
  }
  section.superposition .float-cards {
    grid-area: right;
    display: flex;
    flex-direction: column;
    gap: 14px;
    justify-content: center;
  }
  section.superposition .fcard {
    background: var(--q-glass-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--q-glass-border);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow:
      0 4px 24px var(--q-glass-shadow),
      inset 0 1px 0 rgba(255,255,255,0.08);
    position: relative;
  }
  section.superposition .fcard::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
    background: linear-gradient(to bottom, var(--q-primary), var(--q-secondary));
  }
  section.superposition .fcard .fcard-title {
    font-weight: 700;
    color: var(--q-primary);
    margin-bottom: 4px;
    font-size: 0.95em;
  }
  section.superposition .fcard .fcard-body {
    font-size: 0.82em;
    color: rgba(255,255,255,0.75);
    line-height: 1.5;
  }

  /* ============================================================
     SLIDE 5: ENTANGLEMENT - Connected nodes via CSS
     ============================================================ */
  section.entangle {
    background:
      radial-gradient(circle at 30% 40%, rgba(0,255,255,0.06) 0%, transparent 40%),
      radial-gradient(circle at 70% 60%, rgba(255,0,255,0.06) 0%, transparent 40%),
      var(--q-dark);
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "heading heading"
      "viz desc";
    gap: 20px;
    padding: 45px 55px;
  }
  section.entangle h2 {
    grid-area: heading;
    font-size: 2em;
    text-align: center;
    color: var(--q-secondary);
    text-shadow: var(--q-glow-magenta);
  }
  section.entangle .nodes-viz {
    grid-area: viz;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 280px;
  }
  section.entangle .node {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1em;
    font-weight: 700;
    z-index: 2;
  }
  section.entangle .node-a {
    background: radial-gradient(circle, rgba(0,255,255,0.3) 0%, rgba(0,255,255,0.05) 70%);
    border: 2px solid var(--q-primary);
    box-shadow: var(--q-glow-cyan);
    color: var(--q-primary);
    top: 30%; left: 15%;
  }
  section.entangle .node-b {
    background: radial-gradient(circle, rgba(255,0,255,0.3) 0%, rgba(255,0,255,0.05) 70%);
    border: 2px solid var(--q-secondary);
    box-shadow: var(--q-glow-magenta);
    color: var(--q-secondary);
    top: 30%; right: 15%;
  }
  section.entangle .link {
    position: absolute;
    top: calc(30% + 40px);
    left: calc(15% + 80px);
    width: calc(70% - 160px);
    height: 2px;
    background: linear-gradient(90deg, var(--q-primary), var(--q-accent), var(--q-secondary));
    z-index: 1;
    box-shadow: 0 0 12px rgba(255,255,0,0.3);
  }
  section.entangle .link::before {
    content: "EPR";
    position: absolute;
    top: -22px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.7em;
    color: var(--q-accent);
    background: rgba(0,0,0,0.7);
    padding: 2px 10px;
    border-radius: 4px;
  }
  section.entangle .link::after {
    content: "";
    position: absolute;
    top: -4px; left: 50%;
    transform: translateX(-50%);
    width: 10px; height: 10px;
    background: var(--q-accent);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--q-accent);
  }
  section.entangle .bell-eq {
    position: absolute;
    bottom: 20%;
    left: 50%;
    transform: translateX(-50%);
    font-size: 1.1em;
    color: var(--q-accent);
    text-shadow: 0 0 10px rgba(255,255,0,0.4);
    white-space: nowrap;
    background: rgba(0,0,0,0.6);
    padding: 6px 18px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,0,0.2);
  }
  section.entangle .desc-area {
    grid-area: desc;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 14px;
  }
  section.entangle .desc-area .point {
    background: var(--q-glass-bg);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid var(--q-glass-border);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.85em;
    line-height: 1.5;
    position: relative;
  }
  section.entangle .desc-area .point::after {
    content: "";
    position: absolute;
    right: 12px; top: 12px;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--q-secondary);
    box-shadow: 0 0 8px var(--q-secondary);
  }

  /* ============================================================
     SLIDE 6: QUANTUM GATES - CSS circuit diagram
     ============================================================ */
  section.gates {
    background:
      linear-gradient(180deg, #050520 0%, #0a0a2a 100%);
    padding: 40px 50px;
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 16px;
  }
  section.gates h2 {
    text-align: center;
    font-size: 1.9em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
  }
  section.gates .circuit {
    display: grid;
    grid-template-columns: 60px repeat(5, 1fr) 60px;
    grid-template-rows: repeat(3, 1fr);
    gap: 0;
    align-items: center;
    position: relative;
  }
  section.gates .wire {
    height: 2px;
    background: rgba(0,255,255,0.4);
    grid-column: 1 / -1;
    box-shadow: 0 0 4px rgba(0,255,255,0.2);
  }
  section.gates .wire-label {
    font-size: 0.85em;
    color: var(--q-primary);
    text-align: center;
    font-weight: 700;
  }
  section.gates .gate-box {
    width: 60px;
    height: 60px;
    border: 2px solid var(--q-primary);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1em;
    color: var(--q-primary);
    background: rgba(0,255,255,0.08);
    box-shadow:
      0 0 12px rgba(0,255,255,0.15),
      inset 0 0 8px rgba(0,255,255,0.05);
    justify-self: center;
    z-index: 2;
  }
  section.gates .gate-box.hadamard {
    border-color: var(--q-accent);
    color: var(--q-accent);
    background: rgba(255,255,0,0.08);
    box-shadow: 0 0 12px rgba(255,255,0,0.15);
  }
  section.gates .gate-box.cnot {
    border-color: var(--q-secondary);
    color: var(--q-secondary);
    background: rgba(255,0,255,0.08);
    box-shadow: 0 0 12px rgba(255,0,255,0.15);
    border-radius: 50%;
    width: 50px; height: 50px;
  }
  section.gates .gate-box.cnot::after {
    content: "";
    position: absolute;
    width: 2px;
    height: 60px;
    background: var(--q-secondary);
    opacity: 0.4;
  }
  section.gates .gate-desc {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    font-size: 0.78em;
  }
  section.gates .gate-desc .gd-item {
    background: var(--q-glass-bg);
    border: 1px solid var(--q-glass-border);
    border-radius: 10px;
    padding: 10px 14px;
    text-align: center;
  }
  section.gates .gate-desc .gd-item strong {
    display: block;
    margin-bottom: 4px;
    font-size: 1.1em;
  }

  /* ============================================================
     SLIDE 7: APPLICATIONS - Hexagonal cards via clip-path
     ============================================================ */
  section.hex-apps {
    background:
      radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,100,255,0.08) 0%, transparent 60%),
      linear-gradient(135deg, #0a0a1a 0%, #0f0a2a 50%, #0a0a1a 100%);
    padding: 40px 50px;
  }
  section.hex-apps h2 {
    text-align: center;
    font-size: 2em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
    margin-bottom: 20px;
  }
  section.hex-apps .hex-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 18px;
  }
  section.hex-apps .hex-item {
    width: var(--q-hex-size);
    height: calc(var(--q-hex-size) * 1.1);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 18px 10px;
    font-size: 0.72em;
    line-height: 1.3;
    position: relative;
  }
  section.hex-apps .hex-item::before {
    content: "";
    position: absolute;
    inset: 0;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    background: linear-gradient(135deg, rgba(0,255,255,0.15), rgba(255,0,255,0.15));
    z-index: -1;
  }
  section.hex-apps .hex-item.hex-1 { background: linear-gradient(135deg, #0d2a4a, #1a3a6a); }
  section.hex-apps .hex-item.hex-2 { background: linear-gradient(135deg, #2a0d4a, #4a1a6a); }
  section.hex-apps .hex-item.hex-3 { background: linear-gradient(135deg, #0d4a2a, #1a6a4a); }
  section.hex-apps .hex-item.hex-4 { background: linear-gradient(135deg, #4a2a0d, #6a4a1a); }
  section.hex-apps .hex-item.hex-5 { background: linear-gradient(135deg, #4a0d2a, #6a1a4a); }
  section.hex-apps .hex-item.hex-6 { background: linear-gradient(135deg, #0d4a4a, #1a6a6a); }
  section.hex-apps .hex-icon {
    font-size: 1.8em;
    margin-bottom: 4px;
  }
  section.hex-apps .hex-label {
    font-weight: 700;
    color: #fff;
  }

  /* ============================================================
     SLIDE 8: COMPARISON - Gradient bar chart
     ============================================================ */
  section.compare {
    background:
      linear-gradient(180deg, #0a0a1a 0%, #0f0a2a 100%);
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas:
      "heading heading"
      "bars legend";
    gap: 20px;
    padding: 45px 55px;
  }
  section.compare h2 {
    grid-area: heading;
    text-align: center;
    font-size: 1.9em;
    background: linear-gradient(90deg, var(--q-primary), var(--q-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(0,255,255,0.3));
  }
  section.compare .bars-area {
    grid-area: bars;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 18px;
  }
  section.compare .bar-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  section.compare .bar-row .bar-label {
    font-size: 0.8em;
    color: rgba(255,255,255,0.7);
  }
  section.compare .bar-row .bar-track {
    height: var(--q-bar-height);
    border-radius: 6px;
    position: relative;
    overflow: hidden;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
  }
  section.compare .bar-row .bar-fill-q {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, rgba(0,255,255,0.3) 0%, rgba(0,255,255,0.8) 50%, rgba(0,200,255,0.9) 100%);
    box-shadow: 0 0 12px rgba(0,255,255,0.3);
    display: flex;
    align-items: center;
    padding-left: 10px;
    font-size: 0.75em;
    font-weight: 700;
    color: #fff;
  }
  section.compare .bar-row .bar-fill-c {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.3) 100%);
    display: flex;
    align-items: center;
    padding-left: 10px;
    font-size: 0.75em;
    color: rgba(255,255,255,0.6);
  }
  section.compare .legend-area {
    grid-area: legend;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
    padding-left: 30px;
  }
  section.compare .legend-area .legend-card {
    background: var(--q-glass-bg);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid var(--q-glass-border);
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 0.82em;
    line-height: 1.5;
  }
  section.compare .legend-area .legend-card::before {
    content: "";
    display: inline-block;
    width: 12px; height: 12px;
    border-radius: 3px;
    margin-right: 8px;
    vertical-align: middle;
  }
  section.compare .legend-area .legend-card.lq::before {
    background: var(--q-primary);
    box-shadow: 0 0 6px var(--q-primary);
  }
  section.compare .legend-area .legend-card.lc::before {
    background: rgba(255,255,255,0.4);
  }

  /* ============================================================
     SLIDE 9: ROADMAP - Timeline pseudo-elements
     ============================================================ */
  section.roadmap {
    background:
      radial-gradient(ellipse 50% 80% at 15% 50%, rgba(0,255,255,0.06) 0%, transparent 60%),
      linear-gradient(135deg, #050520 0%, #0a0a2a 50%, #050520 100%);
    padding: 40px 55px;
  }
  section.roadmap h2 {
    text-align: center;
    font-size: 1.9em;
    color: var(--q-primary);
    text-shadow: var(--q-glow-cyan);
    margin-bottom: 24px;
  }
  section.roadmap .timeline {
    position: relative;
    padding-left: 40px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  section.roadmap .timeline::before {
    content: "";
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 3px;
    background: linear-gradient(
      to bottom,
      var(--q-primary) 0%,
      var(--q-secondary) 30%,
      var(--q-accent) 60%,
      rgba(255,255,255,0.2) 100%
    );
    border-radius: 2px;
    box-shadow: 0 0 8px rgba(0,255,255,0.2);
  }
  section.roadmap .tl-item {
    position: relative;
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 14px;
    align-items: start;
    font-size: 0.82em;
  }
  section.roadmap .tl-item::before {
    content: "";
    position: absolute;
    left: -36px;
    top: 4px;
    width: var(--q-timeline-dot);
    height: var(--q-timeline-dot);
    border-radius: 50%;
    border: 2px solid var(--q-primary);
    background: var(--q-dark);
    box-shadow: 0 0 10px rgba(0,255,255,0.4);
    z-index: 1;
  }
  section.roadmap .tl-item.done::before {
    background: var(--q-primary);
    box-shadow: var(--q-glow-cyan);
  }
  section.roadmap .tl-item.active::before {
    background: var(--q-secondary);
    border-color: var(--q-secondary);
    box-shadow: var(--q-glow-magenta);
  }
  section.roadmap .tl-year {
    font-weight: 700;
    color: var(--q-primary);
    font-size: 1.05em;
  }
  section.roadmap .tl-item.active .tl-year { color: var(--q-secondary); }
  section.roadmap .tl-desc {
    color: rgba(255,255,255,0.8);
    line-height: 1.4;
  }
  section.roadmap .tl-desc strong { color: #fff; }

  /* ============================================================
     SLIDE 10: SUMMARY - Gradient text + glassmorphism
     ============================================================ */
  section.summary {
    background:
      radial-gradient(ellipse 100% 80% at 50% 50%, rgba(0,255,255,0.08) 0%, transparent 50%),
      radial-gradient(ellipse 60% 60% at 20% 80%, rgba(255,0,255,0.06) 0%, transparent 50%),
      linear-gradient(180deg, #0a0a1a 0%, #0f0a2a 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  section.summary::before {
    content: "";
    position: absolute;
    top: 10%;
    left: 50%;
    transform: translateX(-50%);
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: conic-gradient(
      from 0deg,
      rgba(0,255,255,0.05) 0deg,
      rgba(255,0,255,0.05) 120deg,
      rgba(255,255,0,0.05) 240deg,
      rgba(0,255,255,0.05) 360deg
    );
    filter: blur(40px);
    pointer-events: none;
  }
  section.summary h2 {
    font-size: 2.6em;
    background: linear-gradient(135deg, #0ff 0%, #0af 20%, #f0f 40%, #f0a 60%, #ff0 80%, #0ff 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 20px rgba(0,255,255,0.3));
    margin-bottom: 24px;
    position: relative;
    z-index: 1;
  }
  section.summary .summary-card {
    background: var(--q-glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--q-glass-border);
    border-radius: 20px;
    padding: 32px 48px;
    max-width: 700px;
    box-shadow:
      0 8px 40px var(--q-glass-shadow),
      inset 0 1px 0 rgba(255,255,255,0.12),
      0 0 0 1px rgba(0,255,255,0.08),
      0 0 60px rgba(0,255,255,0.05);
    position: relative;
    z-index: 1;
    text-align: left;
  }
  section.summary .summary-card::before {
    content: "";
    position: absolute;
    top: -1px; left: -1px; right: -1px;
    height: 3px;
    border-radius: 20px 20px 0 0;
    background: linear-gradient(90deg, var(--q-primary), var(--q-secondary), var(--q-accent), var(--q-primary));
    background-size: 300% 100%;
  }
  section.summary .summary-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  section.summary .summary-card li {
    padding: 8px 0;
    padding-left: 24px;
    position: relative;
    font-size: 0.92em;
    line-height: 1.6;
    color: rgba(255,255,255,0.85);
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  section.summary .summary-card li:last-child { border-bottom: none; }
  section.summary .summary-card li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 8px; height: 8px;
    background: linear-gradient(135deg, var(--q-primary), var(--q-secondary));
    border-radius: 2px;
    transform: translateY(-50%) rotate(45deg);
  }
  section.summary .closing {
    margin-top: 24px;
    font-size: 1.1em;
    color: rgba(255,255,255,0.5);
    position: relative;
    z-index: 1;
  }
  section.summary .closing strong {
    color: var(--q-primary);
    text-shadow: 0 0 8px rgba(0,255,255,0.3);
  }

---

<!-- _class: title -->

# Quantum Computing
## 量子コンピューティングの世界

2026 — 次世代計算パラダイムへの招待

---

<!-- _class: agenda -->

## アジェンダ

<div class="grid">
<div class="card">
  <span class="num">01</span>
  <span class="label">量子ビット<br>基本単位</span>
</div>
<div class="card">
  <span class="num">02</span>
  <span class="label">重ね合わせ<br>同時存在</span>
</div>
<div class="card">
  <span class="num">03</span>
  <span class="label">量子もつれ<br>非局所相関</span>
</div>
<div class="card">
  <span class="num">04</span>
  <span class="label">量子ゲート<br>回路操作</span>
</div>
<div class="card">
  <span class="num">05</span>
  <span class="label">応用分野<br>産業インパクト</span>
</div>
<div class="card">
  <span class="num">06</span>
  <span class="label">量子 vs 古典<br>性能比較</span>
</div>
<div class="card">
  <span class="num">07</span>
  <span class="label">ロードマップ<br>実用化への道</span>
</div>
<div class="card">
  <span class="num">08</span>
  <span class="label">まとめ<br>未来展望</span>
</div>
</div>

---

<!-- _class: split-diag -->

<div class="left-panel">

## 量子ビット (Qubit)

古典ビットが **0** か **1** の二値を取るのに対し、量子ビットは **|0⟩** と **|1⟩** の重ね合わせ状態を保持できます。

<div class="bloch"></div>

ブロッホ球上の任意の点が量子状態を表現します。

</div>
<div class="right-panel">

### 物理的実装方式

- **超伝導量子ビット** — ジョセフソン接合を利用。IBM・Google が採用
- **イオントラップ** — レーザーで捕捉した個別イオン。IonQ・Quantinuum
- **光量子ビット** — 光子の偏光状態を利用。Xanadu・PsiQuantum
- **トポロジカル** — エニオンの編み込み。Microsoft が研究中
- **中性原子** — 光ピンセットで配列。QuEra・Pasqal

</div>

---

<!-- _class: superposition -->

## 量子重ね合わせ — Superposition

<div class="conic-deco">
  <div class="wheel"></div>
  <div class="caption">観測前: 全状態が同時に共存</div>
</div>

<div class="float-cards">
  <div class="fcard">
    <div class="fcard-title">原理</div>
    <div class="fcard-body">量子ビットは |ψ⟩ = α|0⟩ + β|1⟩ と表され、|α|² + |β|² = 1 を満たす複素確率振幅 α, β で定義されます。観測するまで確定しません。</div>
  </div>
  <div class="fcard">
    <div class="fcard-title">並列性の源泉</div>
    <div class="fcard-body">n 量子ビットは 2ⁿ 個の基底状態を同時に保持。50量子ビットで約10¹⁵ の状態空間 — 古典コンピュータでは再現不可能な並列性。</div>
  </div>
  <div class="fcard">
    <div class="fcard-title">デコヒーレンス</div>
    <div class="fcard-body">環境との相互作用で重ね合わせが崩壊する現象。超伝導方式で T₂ ≈ 100μs。エラー訂正が実用化の鍵です。</div>
  </div>
</div>

---

<!-- _class: entangle -->

## 量子もつれ — Entanglement

<div class="nodes-viz">
  <div class="node node-a">|ψ⟩</div>
  <div class="link"></div>
  <div class="node node-b">|φ⟩</div>
  <div class="bell-eq">|Φ⁺⟩ = (|00⟩ + |11⟩) / √2</div>
</div>

<div class="desc-area">
  <div class="point">
    <strong>ベル状態:</strong> 2つの量子ビットが最大限にもつれた状態。一方を観測すると、もう一方の状態が瞬時に確定します。これは情報の超光速伝達ではなく、量子相関の帰結です。
  </div>
  <div class="point">
    <strong>量子テレポーテーション:</strong> もつれと古典通信を組み合わせ、量子状態を遠隔地に転送。量子インターネットの基盤技術として期待されています。
  </div>
  <div class="point">
    <strong>実験的検証:</strong> 2022年ノーベル物理学賞はベルの不等式の破れを実証した Aspect, Clauser, Zeilinger に授与。局所実在論の否定が確立しました。
  </div>
</div>

---

<!-- _class: gates -->

## 量子ゲート — Quantum Gates

<div class="circuit">
  <div class="wire-label">|q₀⟩</div>
  <div class="gate-box hadamard">H</div>
  <div class="gate-box">X</div>
  <div class="gate-box cnot">●</div>
  <div class="gate-box">Rz</div>
  <div class="gate-box">M</div>
  <div class="wire-label">→</div>

  <div class="wire-label">|q₁⟩</div>
  <div class="gate-box">I</div>
  <div class="gate-box hadamard">H</div>
  <div class="gate-box cnot">⊕</div>
  <div class="gate-box">T</div>
  <div class="gate-box">M</div>
  <div class="wire-label">→</div>

  <div class="wire-label">|q₂⟩</div>
  <div class="gate-box">I</div>
  <div class="gate-box">I</div>
  <div class="gate-box">X</div>
  <div class="gate-box hadamard">H</div>
  <div class="gate-box">M</div>
  <div class="wire-label">→</div>
</div>

<div class="gate-desc">
  <div class="gd-item">
    <strong>Hadamard (H)</strong>
    重ね合わせを生成。|0⟩ → (|0⟩+|1⟩)/√2
  </div>
  <div class="gd-item">
    <strong>CNOT (CX)</strong>
    制御ビットに条件付きで反転。もつれ生成の基本操作
  </div>
  <div class="gd-item">
    <strong>T / Rz ゲート</strong>
    位相回転ゲート。ユニバーサルゲートセットの構成要素
  </div>
</div>

---

<!-- _class: hex-apps -->

## 応用分野 — Applications

<div class="hex-grid">
  <div class="hex-item hex-1">
    <span class="hex-icon">🔐</span>
    <span class="hex-label">暗号解読</span>
    RSA破壊
  </div>
  <div class="hex-item hex-2">
    <span class="hex-icon">💊</span>
    <span class="hex-label">創薬</span>
    分子シミュレーション
  </div>
  <div class="hex-item hex-3">
    <span class="hex-icon">📈</span>
    <span class="hex-label">金融</span>
    ポートフォリオ最適化
  </div>
  <div class="hex-item hex-4">
    <span class="hex-icon">🧪</span>
    <span class="hex-label">材料科学</span>
    触媒・超伝導体設計
  </div>
  <div class="hex-item hex-5">
    <span class="hex-icon">🤖</span>
    <span class="hex-label">量子ML</span>
    カーネル法・最適化
  </div>
  <div class="hex-item hex-6">
    <span class="hex-icon">🌐</span>
    <span class="hex-label">量子通信</span>
    QKD・量子ネット
  </div>
</div>

---

<!-- _class: compare -->

## 量子 vs 古典コンピュータ

<div class="bars-area">
  <div class="bar-row">
    <span class="bar-label">素因数分解（2048ビット RSA）</span>
    <div class="bar-track"><div class="bar-fill-q" style="width:95%">量子: ~8時間（Shor）</div></div>
    <div class="bar-track"><div class="bar-fill-c" style="width:8%">古典: ~10²³ 年</div></div>
  </div>
  <div class="bar-row">
    <span class="bar-label">非構造化探索（N=10⁶）</span>
    <div class="bar-track"><div class="bar-fill-q" style="width:60%">量子: ~1000ステップ（Grover）</div></div>
    <div class="bar-track"><div class="bar-fill-c" style="width:30%">古典: ~500,000ステップ</div></div>
  </div>
  <div class="bar-row">
    <span class="bar-label">分子エネルギー計算（FeMoCo）</span>
    <div class="bar-track"><div class="bar-fill-q" style="width:80%">量子: 数日（VQE/QPE）</div></div>
    <div class="bar-track"><div class="bar-fill-c" style="width:5%">古典: 実質不可能</div></div>
  </div>
  <div class="bar-row">
    <span class="bar-label">組合せ最適化（巡回セールスマン）</span>
    <div class="bar-track"><div class="bar-fill-q" style="width:50%">量子: 多項式的加速（QAOA）</div></div>
    <div class="bar-track"><div class="bar-fill-c" style="width:20%">古典: NP困難</div></div>
  </div>
</div>

<div class="legend-area">
  <div class="legend-card lq">
    **量子コンピュータ** — 特定問題で指数関数的・二次的加速を実現。ノイズ耐性のある論理量子ビット（FTQC）が鍵。
  </div>
  <div class="legend-card lc">
    **古典コンピュータ** — 汎用性と安定性に優れる。量子アルゴリズムの古典シミュレーションも重要な研究分野。
  </div>
</div>

---

<!-- _class: roadmap -->

## ロードマップ — 量子コンピューティングの実用化

<div class="timeline">
  <div class="tl-item done">
    <span class="tl-year">2019</span>
    <span class="tl-desc"><strong>量子超越性の実証</strong> — Google Sycamore (53量子ビット) が古典スパコンで1万年かかる計算を200秒で実行</span>
  </div>
  <div class="tl-item done">
    <span class="tl-year">2021</span>
    <span class="tl-desc"><strong>100+量子ビット時代</strong> — IBM Eagle (127量子ビット) 発表。エラー軽減技術の進展</span>
  </div>
  <div class="tl-item done">
    <span class="tl-year">2023</span>
    <span class="tl-desc"><strong>1000量子ビット突破</strong> — IBM Condor (1,121量子ビット)。量子エラー訂正コードの実証実験が加速</span>
  </div>
  <div class="tl-item active">
    <span class="tl-year">2025-26</span>
    <span class="tl-desc"><strong>初期エラー訂正</strong> — 論理量子ビットの実用的な実証。Google Willow による画期的なエラー訂正の成功</span>
  </div>
  <div class="tl-item">
    <span class="tl-year">2028-30</span>
    <span class="tl-desc"><strong>量子実用優位性</strong> — 100論理量子ビット級で実問題の量子加速を初めて産業応用</span>
  </div>
  <div class="tl-item">
    <span class="tl-year">2035+</span>
    <span class="tl-desc"><strong>汎用FTQC</strong> — 数百万物理量子ビットでフォールトトレラント汎用量子コンピュータの実現</span>
  </div>
</div>

---

<!-- _class: summary -->

## 量子コンピューティングの世界

<div class="summary-card">
<ul>
  <li><strong>量子ビット</strong>は重ね合わせともつれにより、古典ビットを超越した計算資源を提供する</li>
  <li><strong>Shor・Groverアルゴリズム</strong>が暗号・探索問題で指数的〜二次的加速を実現する</li>
  <li><strong>NISQ時代</strong>の現在、変分量子アルゴリズム（VQE, QAOA）が実用化の先駆けとなっている</li>
  <li><strong>エラー訂正</strong>が最大の技術課題であり、2025年以降のブレークスルーに世界が注目している</li>
  <li><strong>創薬・材料・金融・暗号</strong>の各分野で、量子コンピュータは産業構造を根本から変革する</li>
</ul>
</div>

<div class="closing">
  <strong>量子の力で、不可能を可能に。</strong>
</div>
