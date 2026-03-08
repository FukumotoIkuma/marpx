---
marp: true
theme: default
size: 16:9
paginate: true
style: |
  /* ============================================================
     DEEP SEA EXPLORATION - 深海探査の最前線
     Custom CSS Theme - 200+ lines of extreme CSS
     ============================================================ */

  /* --- Custom Properties with Fallbacks --- */
  :root {
    --sea-surface: var(--custom-surface, #0077b6);
    --sea-mid: var(--custom-mid, #023e8a);
    --sea-deep: var(--custom-deep, #03071e);
    --sea-abyss: var(--custom-abyss, #000814);
    --bio-cyan: var(--custom-cyan, #00f5d4);
    --bio-violet: var(--custom-violet, #7209b7);
    --bio-pink: var(--custom-pink, #f72585);
    --bio-green: var(--custom-green, #2dc653);
    --thermal-hot: var(--custom-hot, #ff6b35);
    --thermal-warm: var(--custom-warm, #f7c59f);
    --pressure-ring: var(--custom-ring, rgba(0, 245, 212, 0.15));
    --glass-bg: var(--custom-glass, rgba(255, 255, 255, 0.08));
    --glass-border: var(--custom-glass-border, rgba(255, 255, 255, 0.18));
    --glass-shadow: var(--custom-glass-shadow, rgba(0, 0, 0, 0.45));
    --text-primary: var(--custom-text, #e0f7fa);
    --text-secondary: var(--custom-text-sec, #80deea);
    --text-accent: var(--custom-text-acc, #00f5d4);
    --depth-1000: var(--custom-d1, #005f99);
    --depth-3000: var(--custom-d3, #003566);
    --depth-6000: var(--custom-d6, #001d3d);
    --depth-11000: var(--custom-d11, #000a1a);
    --card-radius: var(--custom-radius, 16px);
    --transition-smooth: var(--custom-transition, all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94));
  }

  /* --- Keyframe Animations --- */
  @keyframes causticShimmer {
    0% { background-position: 0% 0%, 50% 50%; }
    25% { background-position: 25% 10%, 60% 40%; }
    50% { background-position: 50% 20%, 70% 30%; }
    75% { background-position: 75% 10%, 80% 50%; }
    100% { background-position: 100% 0%, 90% 60%; }
  }

  @keyframes biolumPulse {
    0%, 100% { opacity: 0.6; filter: brightness(1) blur(0px); }
    50% { opacity: 1; filter: brightness(1.4) blur(1px); }
  }

  @keyframes bubbleRise {
    0% { transform: translateY(0) scale(1); opacity: 0.7; }
    50% { transform: translateY(-120px) scale(1.1); opacity: 0.4; }
    100% { transform: translateY(-240px) scale(0.8); opacity: 0; }
  }

  @keyframes depthDescent {
    0% { background-position: center 0%; }
    100% { background-position: center 100%; }
  }

  @keyframes thermalFlow {
    0% { background-position: 0% 100%; }
    50% { background-position: 100% 0%; }
    100% { background-position: 0% 100%; }
  }

  @keyframes pressurePulse {
    0%, 100% { outline-offset: 0px; }
    50% { outline-offset: 4px; }
  }

  @keyframes glassFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
  }

  @keyframes sonarPing {
    0% { box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.5); }
    70% { box-shadow: 0 0 0 30px rgba(0, 245, 212, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 245, 212, 0); }
  }

  /* --- Global Section Styles --- */
  section {
    font-family: 'Noto Sans JP', 'Hiragino Sans', 'Yu Gothic UI', sans-serif;
    color: var(--text-primary);
    padding: 40px 60px;
    overflow: hidden;
    position: relative;
  }

  section h1 {
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1.2;
  }

  section h2 {
    font-weight: 700;
    letter-spacing: 0.01em;
    line-height: 1.3;
    margin-bottom: 0.6em;
  }

  section p, section li {
    font-size: 0.92em;
    line-height: 1.7;
  }

  /* --- Slide 1: Title with Layered Ocean Depth --- */
  section.title-slide {
    background:
      radial-gradient(ellipse 120% 60% at 50% 20%, rgba(0, 119, 182, 0.35) 0%, transparent 70%),
      radial-gradient(ellipse 80% 40% at 30% 70%, rgba(0, 245, 212, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse 60% 30% at 70% 80%, rgba(114, 9, 183, 0.1) 0%, transparent 50%),
      linear-gradient(173deg, #0077b6 0%, #023e8a 25%, #001d3d 50%, #03071e 75%, #000814 100%);
    background-blend-mode: screen, overlay, soft-light, normal;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  section.title-slide h1 {
    font-size: 3.2em;
    color: #ffffff;
    text-shadow:
      0 0 10px rgba(0, 245, 212, 0.6),
      0 0 30px rgba(0, 245, 212, 0.3),
      0 0 60px rgba(0, 119, 182, 0.4),
      0 0 100px rgba(0, 119, 182, 0.2),
      0 2px 4px rgba(0, 0, 0, 0.8);
    margin-bottom: 0.1em;
  }

  section.title-slide h2 {
    font-size: 1.5em;
    color: var(--bio-cyan);
    text-shadow:
      0 0 8px rgba(0, 245, 212, 0.5),
      0 0 20px rgba(0, 245, 212, 0.2);
    font-weight: 400;
    letter-spacing: 0.15em;
  }

  section.title-slide .subtitle-line {
    width: 300px;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--bio-cyan) 50%, transparent 100%);
    margin: 20px auto;
    border-radius: 1px;
  }

  section.title-slide .title-bubbles::before,
  section.title-slide .title-bubbles::after {
    content: '';
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 245, 212, 0.15) 0%, transparent 70%);
    animation: bubbleRise 6s ease-in-out infinite;
  }

  section.title-slide .title-bubbles::before {
    width: 40px;
    height: 40px;
    bottom: 80px;
    left: 15%;
    animation-delay: 0s;
  }

  section.title-slide .title-bubbles::after {
    width: 25px;
    height: 25px;
    bottom: 120px;
    right: 20%;
    animation-delay: 2s;
  }

  /* --- Slide 2: Depth Zones --- */
  section.depth-zones {
    background: linear-gradient(180deg, #0096c7 0%, #0077b6 15%, #023e8a 35%, #001d3d 55%, #03071e 80%, #000814 100%);
    padding: 30px 60px;
  }

  section.depth-zones h2 {
    color: #caf0f8;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  }

  section.depth-zones .zone-container {
    display: grid;
    grid-template-columns: 180px 1fr;
    grid-template-rows: repeat(5, 1fr);
    gap: 6px;
    height: 380px;
  }

  section.depth-zones .zone-bar {
    border-radius: 6px 20px 20px 6px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    font-weight: 600;
    font-size: 0.85em;
    color: #ffffff;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
    position: relative;
  }

  section.depth-zones .zone-bar::after {
    content: '';
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
  }

  section.depth-zones .zone-epipelagic {
    background: linear-gradient(90deg, #48cae4 0%, #0096c7 100%);
    box-shadow: 0 2px 8px rgba(72, 202, 228, 0.4);
  }

  section.depth-zones .zone-mesopelagic {
    background: linear-gradient(90deg, #0077b6 0%, #005f99 100%);
    box-shadow: 0 2px 8px rgba(0, 119, 182, 0.4);
  }

  section.depth-zones .zone-bathypelagic {
    background: linear-gradient(90deg, #023e8a 0%, #002855 100%);
    box-shadow: 0 2px 8px rgba(2, 62, 138, 0.4);
  }

  section.depth-zones .zone-abyssopelagic {
    background: linear-gradient(90deg, #001d3d 0%, #00132b 100%);
    box-shadow: 0 2px 8px rgba(0, 29, 61, 0.4);
  }

  section.depth-zones .zone-hadal {
    background: linear-gradient(90deg, #03071e 0%, #000000 100%);
    box-shadow: 0 2px 8px rgba(3, 7, 30, 0.6);
  }

  section.depth-zones .zone-desc {
    display: flex;
    align-items: center;
    padding-left: 18px;
    font-size: 0.78em;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  section.depth-zones .zone-label {
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8em;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #caf0f8;
    text-align: center;
    background: rgba(0, 0, 0, 0.3);
  }

  /* --- Slide 3: Exploration Technology Cards --- */
  section.tech-cards {
    background:
      repeating-linear-gradient(217deg, rgba(0, 119, 182, 0.03) 0px, transparent 2px, transparent 40px),
      repeating-linear-gradient(127deg, rgba(0, 245, 212, 0.02) 0px, transparent 2px, transparent 35px),
      linear-gradient(195deg, #001d3d 0%, #03071e 100%);
    padding: 30px 50px;
  }

  section.tech-cards h2 {
    color: var(--bio-cyan);
    text-shadow: 0 0 12px rgba(0, 245, 212, 0.3);
  }

  section.tech-cards .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
    margin-top: 10px;
  }

  section.tech-cards .tech-card {
    background: linear-gradient(145deg, rgba(2, 62, 138, 0.4) 0%, rgba(0, 29, 61, 0.6) 100%);
    border: 1px solid rgba(0, 245, 212, 0.12);
    border-radius: var(--card-radius);
    padding: 22px;
    position: relative;
    box-shadow:
      0 1px 2px rgba(0, 0, 0, 0.15),
      0 2px 4px rgba(0, 0, 0, 0.12),
      0 4px 8px rgba(0, 0, 0, 0.1),
      0 8px 16px rgba(0, 0, 0, 0.08),
      0 16px 32px rgba(0, 0, 0, 0.06),
      0 32px 64px rgba(0, 0, 0, 0.04),
      inset 0 1px 0 rgba(255, 255, 255, 0.05),
      inset 0 -1px 0 rgba(0, 0, 0, 0.2),
      0 0 0 1px rgba(0, 245, 212, 0.05),
      0 0 20px rgba(0, 119, 182, 0.08),
      0 0 40px rgba(0, 119, 182, 0.04),
      0 2px 1px rgba(0, 0, 0, 0.2),
      0 4px 2px rgba(0, 0, 0, 0.15),
      0 8px 4px rgba(0, 0, 0, 0.1),
      0 16px 8px rgba(0, 0, 0, 0.06);
    transition: var(--transition-smooth);
  }

  section.tech-cards .tech-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent 0%, var(--bio-cyan) 30%, var(--bio-violet) 70%, transparent 100%);
    border-radius: var(--card-radius) var(--card-radius) 0 0;
    opacity: 0.7;
  }

  section.tech-cards .tech-card h3 {
    color: var(--bio-cyan);
    font-size: 1em;
    margin-bottom: 8px;
    font-weight: 700;
  }

  section.tech-cards .tech-card p {
    font-size: 0.75em;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.6;
  }

  /* --- Slide 4: Bioluminescent Creatures --- */
  section.bioluminescent {
    background:
      radial-gradient(circle 200px at 20% 30%, rgba(0, 245, 212, 0.06) 0%, transparent 100%),
      radial-gradient(circle 150px at 75% 60%, rgba(114, 9, 183, 0.08) 0%, transparent 100%),
      radial-gradient(circle 100px at 50% 80%, rgba(247, 37, 133, 0.06) 0%, transparent 100%),
      radial-gradient(circle 300px at 60% 20%, rgba(0, 119, 182, 0.05) 0%, transparent 100%),
      linear-gradient(180deg, #03071e 0%, #000814 40%, #000000 100%);
    animation: causticShimmer 12s ease-in-out infinite;
  }

  section.bioluminescent h2 {
    color: var(--bio-cyan);
    text-shadow:
      0 0 6px rgba(0, 245, 212, 0.8),
      0 0 20px rgba(0, 245, 212, 0.4),
      0 0 40px rgba(0, 245, 212, 0.2);
  }

  section.bioluminescent .creature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 12px;
  }

  section.bioluminescent .creature-card {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid;
    border-radius: 20px 8px 20px 8px;
    padding: 20px;
    position: relative;
    animation: biolumPulse 4s ease-in-out infinite;
  }

  section.bioluminescent .creature-card.glow-cyan {
    border-color: rgba(0, 245, 212, 0.4);
    box-shadow:
      0 0 8px rgba(0, 245, 212, 0.2),
      0 0 20px rgba(0, 245, 212, 0.1),
      inset 0 0 15px rgba(0, 245, 212, 0.05);
    animation-delay: 0s;
  }

  section.bioluminescent .creature-card.glow-violet {
    border-color: rgba(114, 9, 183, 0.5);
    box-shadow:
      0 0 8px rgba(114, 9, 183, 0.3),
      0 0 20px rgba(114, 9, 183, 0.15),
      inset 0 0 15px rgba(114, 9, 183, 0.05);
    animation-delay: 1.3s;
  }

  section.bioluminescent .creature-card.glow-pink {
    border-color: rgba(247, 37, 133, 0.4);
    box-shadow:
      0 0 8px rgba(247, 37, 133, 0.2),
      0 0 20px rgba(247, 37, 133, 0.1),
      inset 0 0 15px rgba(247, 37, 133, 0.05);
    animation-delay: 2.6s;
  }

  section.bioluminescent .creature-card h3 {
    font-size: 0.95em;
    margin-bottom: 6px;
    font-weight: 700;
  }

  section.bioluminescent .creature-card.glow-cyan h3 { color: var(--bio-cyan); }
  section.bioluminescent .creature-card.glow-violet h3 { color: var(--bio-violet); }
  section.bioluminescent .creature-card.glow-pink h3 { color: var(--bio-pink); }

  section.bioluminescent .creature-card p {
    font-size: 0.72em;
    color: rgba(224, 247, 250, 0.75);
    margin: 0;
    line-height: 1.6;
  }

  /* --- Slide 5: Hydrothermal Vents Split Layout --- */
  section.thermal-vents {
    background: linear-gradient(90deg,
      #03071e 0%, #001d3d 48%,
      #001d3d 48%, #001d3d 52%,
      #001d3d 52%, #03071e 100%);
    padding: 30px 50px;
  }

  section.thermal-vents h2 {
    text-align: center;
    color: var(--thermal-warm);
    text-shadow: 0 0 10px rgba(255, 107, 53, 0.4);
    margin-bottom: 15px;
  }

  section.thermal-vents .split-container {
    display: grid;
    grid-template-columns: 1fr 4px 1fr;
    gap: 20px;
    height: 370px;
  }

  section.thermal-vents .hot-side {
    background:
      radial-gradient(ellipse 80% 60% at 50% 80%, rgba(255, 107, 53, 0.2) 0%, transparent 70%),
      radial-gradient(ellipse 60% 40% at 30% 60%, rgba(247, 197, 159, 0.1) 0%, transparent 60%),
      linear-gradient(173deg, rgba(255, 107, 53, 0.05) 0%, rgba(3, 7, 30, 0.8) 100%);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255, 107, 53, 0.2);
    box-shadow:
      inset 0 -40px 60px rgba(255, 107, 53, 0.08),
      0 4px 20px rgba(0, 0, 0, 0.3);
  }

  section.thermal-vents .cold-side {
    background:
      radial-gradient(ellipse 80% 60% at 50% 30%, rgba(0, 150, 199, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse 50% 50% at 70% 50%, rgba(0, 245, 212, 0.05) 0%, transparent 60%),
      linear-gradient(187deg, rgba(0, 150, 199, 0.05) 0%, rgba(3, 7, 30, 0.8) 100%);
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(0, 150, 199, 0.2);
    box-shadow:
      inset 0 40px 60px rgba(0, 150, 199, 0.05),
      0 4px 20px rgba(0, 0, 0, 0.3);
  }

  section.thermal-vents .divider-line {
    background: linear-gradient(180deg, rgba(255, 107, 53, 0.6) 0%, rgba(0, 245, 212, 0.1) 40%, rgba(0, 150, 199, 0.6) 100%);
    border-radius: 2px;
    box-shadow: 0 0 12px rgba(255, 107, 53, 0.3);
  }

  section.thermal-vents .hot-side h3 {
    color: var(--thermal-hot);
    font-size: 0.95em;
    text-shadow: 0 0 8px rgba(255, 107, 53, 0.4);
  }

  section.thermal-vents .cold-side h3 {
    color: #48cae4;
    font-size: 0.95em;
    text-shadow: 0 0 8px rgba(72, 202, 228, 0.3);
  }

  section.thermal-vents .hot-side p,
  section.thermal-vents .cold-side p {
    font-size: 0.72em;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  section.thermal-vents .temp-badge {
    display: inline-block;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 700;
    margin-top: 8px;
  }

  section.thermal-vents .hot-side .temp-badge {
    background: linear-gradient(90deg, rgba(255, 107, 53, 0.3), rgba(247, 37, 133, 0.2));
    border: 1px solid rgba(255, 107, 53, 0.4);
    color: var(--thermal-warm);
  }

  section.thermal-vents .cold-side .temp-badge {
    background: linear-gradient(90deg, rgba(0, 150, 199, 0.3), rgba(0, 245, 212, 0.2));
    border: 1px solid rgba(0, 150, 199, 0.4);
    color: #48cae4;
  }

  /* --- Slide 6: Pressure Visualization with Concentric Rings --- */
  section.pressure-viz {
    background:
      radial-gradient(circle at 50% 50%, rgba(0, 245, 212, 0.03) 0%, transparent 50%),
      linear-gradient(180deg, #001d3d 0%, #000814 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  section.pressure-viz h2 {
    color: var(--text-primary);
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
    width: 100%;
  }

  section.pressure-viz .pressure-center {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background:
      radial-gradient(circle, rgba(0, 245, 212, 0.15) 0%, rgba(0, 245, 212, 0.02) 60%, transparent 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin: 20px auto 0;
    position: relative;
    outline: 2px solid rgba(0, 245, 212, 0.08);
    outline-offset: 15px;
    box-shadow:
      0 0 0 30px rgba(0, 245, 212, 0.06),
      0 0 0 60px rgba(0, 245, 212, 0.04),
      0 0 0 90px rgba(0, 119, 182, 0.04),
      0 0 0 120px rgba(0, 119, 182, 0.03),
      0 0 0 150px rgba(0, 119, 182, 0.02),
      0 0 0 180px rgba(2, 62, 138, 0.02),
      0 0 0 210px rgba(2, 62, 138, 0.015),
      0 0 0 240px rgba(0, 29, 61, 0.01),
      0 0 60px rgba(0, 245, 212, 0.08),
      0 0 120px rgba(0, 119, 182, 0.05),
      inset 0 0 30px rgba(0, 245, 212, 0.08),
      inset 0 0 60px rgba(0, 119, 182, 0.04),
      0 0 0 2px rgba(0, 245, 212, 0.12),
      0 0 0 4px rgba(0, 245, 212, 0.08),
      0 0 0 6px rgba(0, 245, 212, 0.04);
    animation: pressurePulse 3s ease-in-out infinite;
  }

  section.pressure-viz .pressure-value {
    font-size: 1.8em;
    font-weight: 900;
    color: var(--bio-cyan);
    text-shadow: 0 0 10px rgba(0, 245, 212, 0.6);
  }

  section.pressure-viz .pressure-unit {
    font-size: 0.7em;
    color: var(--text-secondary);
  }

  section.pressure-viz .pressure-labels {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    width: 100%;
    margin-top: 30px;
  }

  section.pressure-viz .p-label {
    text-align: center;
    padding: 10px;
    border-radius: 10px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 245, 212, 0.1);
    font-size: 0.7em;
  }

  section.pressure-viz .p-label .p-depth {
    color: var(--bio-cyan);
    font-weight: 700;
    font-size: 1.1em;
  }

  section.pressure-viz .p-label .p-atm {
    color: var(--text-secondary);
    font-size: 0.9em;
  }

  /* --- Slide 7: Submersible History Timeline --- */
  section.timeline-slide {
    background:
      repeating-linear-gradient(90deg, rgba(0, 245, 212, 0.02) 0px, transparent 1px, transparent 120px),
      linear-gradient(195deg, #001d3d 0%, #03071e 60%, #000814 100%);
    padding: 30px 50px;
  }

  section.timeline-slide h2 {
    color: var(--text-primary);
    margin-bottom: 20px;
  }

  section.timeline-slide .timeline {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    position: relative;
    padding-top: 30px;
  }

  section.timeline-slide .timeline::before {
    content: '';
    position: absolute;
    top: 14px;
    left: 5%;
    right: 5%;
    height: 3px;
    background: linear-gradient(90deg,
      var(--bio-cyan) 0%,
      var(--sea-surface) 30%,
      var(--bio-violet) 60%,
      var(--bio-pink) 100%);
    border-radius: 2px;
    box-shadow: 0 0 10px rgba(0, 245, 212, 0.3);
  }

  section.timeline-slide .t-node {
    text-align: center;
    position: relative;
  }

  section.timeline-slide .t-node::before {
    content: '';
    position: absolute;
    top: -22px;
    left: 50%;
    transform: translateX(-50%);
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--bio-cyan);
    border: 3px solid var(--sea-deep);
    box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
    z-index: 2;
  }

  section.timeline-slide .t-node .t-year {
    font-size: 0.85em;
    font-weight: 800;
    color: var(--bio-cyan);
    margin-bottom: 4px;
  }

  section.timeline-slide .t-node .t-name {
    font-size: 0.8em;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  section.timeline-slide .t-node .t-desc {
    font-size: 0.62em;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  section.timeline-slide .t-node .t-card {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(0, 245, 212, 0.1);
    border-radius: 10px;
    padding: 12px 10px;
  }

  /* --- Slide 8: Deep Sea Resources - Organic Shapes --- */
  section.resources-slide {
    background:
      radial-gradient(circle 400px at 80% 70%, rgba(114, 9, 183, 0.06) 0%, transparent 100%),
      radial-gradient(circle 300px at 20% 40%, rgba(0, 245, 212, 0.04) 0%, transparent 100%),
      linear-gradient(217deg, #001d3d 0%, #03071e 50%, #000814 100%);
    padding: 30px 50px;
  }

  section.resources-slide h2 {
    color: var(--text-primary);
  }

  section.resources-slide .resource-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 10px;
  }

  section.resources-slide .res-card {
    padding: 20px;
    position: relative;
    border: 1px solid rgba(0, 245, 212, 0.12);
    background:
      radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0, 119, 182, 0.08) 0%, transparent 100%),
      rgba(0, 0, 0, 0.35);
    transition: var(--transition-smooth);
  }

  section.resources-slide .res-card.shape-1 {
    border-radius: 30px 10px 30px 10px;
    box-shadow:
      0 4px 15px rgba(0, 245, 212, 0.06),
      0 8px 30px rgba(0, 0, 0, 0.3);
  }

  section.resources-slide .res-card.shape-2 {
    border-radius: 10px 30px 10px 30px;
    box-shadow:
      0 4px 15px rgba(114, 9, 183, 0.06),
      0 8px 30px rgba(0, 0, 0, 0.3);
  }

  section.resources-slide .res-card.shape-3 {
    border-radius: 20px 5px 20px 5px;
    box-shadow:
      0 4px 15px rgba(247, 37, 133, 0.06),
      0 8px 30px rgba(0, 0, 0, 0.3);
  }

  section.resources-slide .res-card.shape-4 {
    border-radius: 5px 20px 5px 20px;
    box-shadow:
      0 4px 15px rgba(0, 119, 182, 0.08),
      0 8px 30px rgba(0, 0, 0, 0.3);
  }

  section.resources-slide .res-card h3 {
    font-size: 0.9em;
    color: var(--bio-cyan);
    margin-bottom: 6px;
  }

  section.resources-slide .res-card p {
    font-size: 0.7em;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.6;
  }

  /* --- Slide 9: Environmental Conservation - Glassmorphism --- */
  section.conservation {
    background:
      radial-gradient(ellipse 100% 80% at 30% 40%, rgba(0, 119, 182, 0.25) 0%, transparent 60%),
      radial-gradient(ellipse 80% 60% at 70% 60%, rgba(0, 245, 212, 0.1) 0%, transparent 50%),
      radial-gradient(ellipse 60% 50% at 50% 80%, rgba(114, 9, 183, 0.08) 0%, transparent 50%),
      linear-gradient(173deg, #023e8a 0%, #001d3d 40%, #03071e 100%);
    background-blend-mode: screen, overlay, soft-light, normal;
    padding: 30px 50px;
  }

  section.conservation h2 {
    color: var(--bio-green);
    text-shadow: 0 0 8px rgba(45, 198, 83, 0.3);
    margin-bottom: 15px;
  }

  section.conservation .glass-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
  }

  section.conservation .glass-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(12px) saturate(1.4);
    -webkit-backdrop-filter: blur(12px) saturate(1.4);
    border: 1px solid var(--glass-border);
    border-radius: var(--card-radius);
    padding: 22px;
    box-shadow:
      0 8px 32px var(--glass-shadow),
      inset 0 1px 0 rgba(255, 255, 255, 0.1),
      0 0 0 1px rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
  }

  section.conservation .glass-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%);
  }

  section.conservation .glass-panel h3 {
    font-size: 0.9em;
    color: var(--bio-green);
    margin-bottom: 8px;
    font-weight: 700;
  }

  section.conservation .glass-panel p {
    font-size: 0.72em;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.65;
  }

  /* --- Slide 10: Summary - Dramatic Glassmorphism --- */
  section.summary-slide {
    background:
      radial-gradient(circle 300px at 25% 35%, rgba(0, 245, 212, 0.12) 0%, transparent 100%),
      radial-gradient(circle 250px at 75% 65%, rgba(114, 9, 183, 0.1) 0%, transparent 100%),
      radial-gradient(circle 200px at 50% 90%, rgba(247, 37, 133, 0.08) 0%, transparent 100%),
      radial-gradient(ellipse 150% 100% at 50% 0%, rgba(0, 119, 182, 0.2) 0%, transparent 60%),
      linear-gradient(195deg, #023e8a 0%, #001d3d 30%, #03071e 60%, #000814 100%);
    background-blend-mode: screen, overlay, soft-light, screen, normal;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    filter: brightness(1.02) saturate(1.1);
  }

  section.summary-slide h2 {
    color: #ffffff;
    font-size: 1.8em;
    text-shadow:
      0 0 15px rgba(0, 245, 212, 0.5),
      0 0 40px rgba(0, 245, 212, 0.2),
      0 2px 4px rgba(0, 0, 0, 0.8);
    margin-bottom: 20px;
  }

  section.summary-slide .summary-glass {
    background: var(--glass-bg);
    backdrop-filter: blur(16px) saturate(1.6) brightness(1.1);
    -webkit-backdrop-filter: blur(16px) saturate(1.6) brightness(1.1);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 35px 50px;
    max-width: 700px;
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.4),
      0 16px 64px rgba(0, 0, 0, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.12),
      inset 0 -1px 0 rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(255, 255, 255, 0.06),
      0 0 60px rgba(0, 245, 212, 0.05),
      0 0 120px rgba(114, 9, 183, 0.03);
    position: relative;
    overflow: hidden;
    animation: glassFloat 6s ease-in-out infinite;
  }

  section.summary-slide .summary-glass::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0, 245, 212, 0.4) 30%, rgba(114, 9, 183, 0.3) 70%, transparent 100%);
  }

  section.summary-slide .summary-glass::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 20%;
    right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
  }

  section.summary-slide .summary-glass p {
    font-size: 0.88em;
    line-height: 1.8;
    color: var(--text-primary);
    margin: 0;
  }

  section.summary-slide .closing-line {
    margin-top: 20px;
    font-size: 0.8em;
    color: var(--bio-cyan);
    text-shadow: 0 0 6px rgba(0, 245, 212, 0.3);
    letter-spacing: 0.08em;
  }
---

<!-- _class: title-slide -->

<div class="title-bubbles"></div>

# Deep Sea Exploration

<div class="subtitle-line"></div>

## 深海探査の最前線

---

<!-- _class: depth-zones -->

## 深海の定義 ― 海洋の垂直構造

<div class="zone-container">
  <div class="zone-label">表層帯</div>
  <div class="zone-bar zone-epipelagic">0〜200m ― 光合成が可能な有光層</div>
  <div class="zone-label">中深層帯</div>
  <div class="zone-bar zone-mesopelagic">200〜1,000m ― 薄明帯、微弱な光が届く限界</div>
  <div class="zone-label">漸深層帯</div>
  <div class="zone-bar zone-bathypelagic">1,000〜4,000m ― 完全な暗黒、水温2〜4℃</div>
  <div class="zone-label">深海層帯</div>
  <div class="zone-bar zone-abyssopelagic">4,000〜6,000m ― 深海平原が広がる領域</div>
  <div class="zone-label">超深海帯</div>
  <div class="zone-bar zone-hadal">6,000〜11,000m ― 海溝のみに存在する極限環境</div>
</div>

---

<!-- _class: tech-cards -->

## 探査技術の進化

<div class="card-grid">
  <div class="tech-card">
    <h3>有人潜水調査船 (HOV)</h3>
    <p>「しんかい6500」に代表される有人潜水船。研究者が直接深海を観察し、マニピュレータでサンプルを採取できる。最大潜航深度6,500mで世界屈指の性能を誇る。</p>
  </div>
  <div class="tech-card">
    <h3>遠隔操作型無人探査機 (ROV)</h3>
    <p>母船からケーブルで接続された無人機。JAMSTECの「かいこう」は11,000m級の超深海調査が可能。リアルタイム映像伝送と精密な作業能力を持つ。</p>
  </div>
  <div class="tech-card">
    <h3>自律型無人探査機 (AUV)</h3>
    <p>プログラムされた経路を自律航行する無人機。広域の海底地形マッピングや環境モニタリングに最適。「うらしま」は航続距離300km超を実現。</p>
  </div>
</div>

---

<!-- _class: bioluminescent -->

## 深海生物 ― 生物発光の世界

<div class="creature-grid">
  <div class="creature-card glow-cyan">
    <h3>チョウチンアンコウ</h3>
    <p>頭部のエスカ（疑似餌）に共生する発光バクテリアを利用して獲物を誘引する。水深200〜2,000mに生息し、雌雄の極端な性的二形が特徴。雄は雌の体に寄生して融合する。</p>
  </div>
  <div class="creature-card glow-violet">
    <h3>クシクラゲ類</h3>
    <p>繊毛板の光の回折により虹色に輝くが、体内でも青緑色の生物発光を行う。深海種のブラッディベリーは赤い体色で捕食した発光生物の光を隠蔽する戦略をとる。</p>
  </div>
  <div class="creature-card glow-pink">
    <h3>ホウライエソ</h3>
    <p>下顎に長い髭状のバーベルを持ち、先端が発光する。赤色光を発する珍しい深海魚で、他の深海生物が感知できない波長の光で獲物を照らし出す「ステルス照明」を使う。</p>
  </div>
</div>

---

<!-- _class: thermal-vents -->

## 熱水噴出孔 ― 生命の起源への手がかり

<div class="split-container">
  <div class="hot-side">
    <h3>ブラックスモーカー</h3>
    <p>海底の割れ目から噴出する熱水が海水中の金属イオンと反応し、黒い煙のような硫化物の粒子を放出する。噴出口温度は最高400℃を超え、煙突状のチムニー構造を形成する。</p>
    <p>チムニー周辺には硫化銅・硫化鉄・硫化亜鉛などの鉱物が沈殿し、海底熱水鉱床を形成する。</p>
    <span class="temp-badge">最大 407℃</span>
  </div>
  <div class="divider-line"></div>
  <div class="cold-side">
    <h3>化学合成生態系</h3>
    <p>太陽光に依存しない独自の生態系。化学合成細菌が硫化水素やメタンを酸化してエネルギーを得る。この細菌を基盤として、チューブワーム・シロウリガイ・ユノハナガニなどが共生する。</p>
    <p>1977年のガラパゴス海嶺での発見は、生命の起源に関する理論を根本から変えた。</p>
    <span class="temp-badge">周辺水温 2〜4℃</span>
  </div>
</div>

---

<!-- _class: pressure-viz -->

## 深海の圧力 ― 想像を超える力

<div class="pressure-center">
  <span class="pressure-value">1,100</span>
  <span class="pressure-unit">気圧 (マリアナ海溝底部)</span>
</div>

<div class="pressure-labels">
  <div class="p-label">
    <div class="p-depth">1,000m</div>
    <div class="p-atm">約100気圧</div>
    <div style="font-size:0.65em;color:#80deea;margin-top:4px;">1cm²に100kgの力</div>
  </div>
  <div class="p-label">
    <div class="p-depth">3,000m</div>
    <div class="p-atm">約300気圧</div>
    <div style="font-size:0.65em;color:#80deea;margin-top:4px;">スチール缶が瞬時に圧壊</div>
  </div>
  <div class="p-label">
    <div class="p-depth">6,000m</div>
    <div class="p-atm">約600気圧</div>
    <div style="font-size:0.65em;color:#80deea;margin-top:4px;">特殊チタン合金が必要</div>
  </div>
  <div class="p-label">
    <div class="p-depth">10,920m</div>
    <div class="p-atm">約1,100気圧</div>
    <div style="font-size:0.65em;color:#80deea;margin-top:4px;">地球最深部の極限圧力</div>
  </div>
</div>

---

<!-- _class: timeline-slide -->

## 探査機の歴史 ― 深海への挑戦

<div class="timeline">
  <div class="t-node">
    <div class="t-card">
      <div class="t-year">1960</div>
      <div class="t-name">トリエステ号</div>
      <div class="t-desc">ジャック・ピカールとドン・ウォルシュがマリアナ海溝チャレンジャー海淵に到達。深度10,916m。人類初の最深部到達。</div>
    </div>
  </div>
  <div class="t-node">
    <div class="t-card">
      <div class="t-year">1964</div>
      <div class="t-name">アルビン号</div>
      <div class="t-desc">ウッズホール海洋研究所の有人潜水船。タイタニック号調査（1986年）や熱水噴出孔発見に貢献。5,000回以上の潜航実績。</div>
    </div>
  </div>
  <div class="t-node">
    <div class="t-card">
      <div class="t-year">1989</div>
      <div class="t-name">しんかい6500</div>
      <div class="t-desc">JAMSTECが運用する日本の有人潜水調査船。6,500mまで潜航可能。累計1,500回以上の潜航で多数の科学的発見に貢献。</div>
    </div>
  </div>
  <div class="t-node">
    <div class="t-card">
      <div class="t-year">1995</div>
      <div class="t-name">かいこう</div>
      <div class="t-desc">JAMSTECの無人探査機。1995年にマリアナ海溝最深部10,911mに到達。ランチャー・ビークル方式の革新的設計。</div>
    </div>
  </div>
  <div class="t-node">
    <div class="t-card">
      <div class="t-year">2012</div>
      <div class="t-name">ディープシーチャレンジャー</div>
      <div class="t-desc">ジェームズ・キャメロン監督が単独でマリアナ海溝最深部に到達。深度10,908m。3Dカメラで深海を撮影。</div>
    </div>
  </div>
</div>

---

<!-- _class: resources-slide -->

## 深海資源 ― 未開拓のフロンティア

<div class="resource-grid">
  <div class="res-card shape-1">
    <h3>マンガン団塊</h3>
    <p>深海底に散在する直径数cmの球状鉱物。マンガン・ニッケル・コバルト・銅を含む。クラリオン・クリッパートン断裂帯に世界最大の鉱床が存在。形成速度は100万年に数mm。</p>
  </div>
  <div class="res-card shape-2">
    <h3>コバルトリッチクラスト</h3>
    <p>海山の斜面を覆う厚さ数cmの鉱物被覆層。コバルト・白金・レアアース元素を高濃度で含有。日本の排他的経済水域内の海山に豊富に分布。</p>
  </div>
  <div class="res-card shape-3">
    <h3>海底熱水鉱床</h3>
    <p>熱水噴出孔周辺に形成される金属硫化物の堆積体。金・銀・銅・亜鉛・鉛を含む。沖縄トラフや伊豆小笠原弧で大規模鉱床が発見されている。</p>
  </div>
  <div class="res-card shape-4">
    <h3>メタンハイドレート</h3>
    <p>低温高圧の深海底堆積物中に存在するメタンの氷状固体。日本周辺海域に大量に賦存。次世代エネルギー資源として研究開発が進行中。南海トラフでの産出試験を実施。</p>
  </div>
</div>

---

<!-- _class: conservation -->

## 環境保全 ― 深海生態系の保護

<div class="glass-grid">
  <div class="glass-panel">
    <h3>深海採掘の環境影響</h3>
    <p>海底鉱物資源の採掘は、堆積物の巻き上げによる濁水プルーム、底生生物の生息地破壊、騒音・光害による生態系攪乱など深刻な影響が懸念される。深海生態系の回復には数十年〜数百年を要する可能性がある。</p>
  </div>
  <div class="glass-panel">
    <h3>国際海底機構 (ISA) の役割</h3>
    <p>国連海洋法条約に基づき設立されたISAは、国際海底区域の鉱物資源管理を担う。探査契約の発行と環境規制の策定を行い、「人類共同の財産」としての深海底資源の適切な管理を目指している。</p>
  </div>
  <div class="glass-panel">
    <h3>脆弱な深海生態系 (VME)</h3>
    <p>冷水サンゴ礁・海綿群集・熱水噴出孔生態系などのVMEは、一度破壊されると回復が極めて困難。国際的な保護区域の設定やEIA（環境影響評価）の義務化が進められている。</p>
  </div>
  <div class="glass-panel">
    <h3>持続可能な深海研究</h3>
    <p>非破壊的な観測技術（環境DNA分析、水中ドローン、長期海底観測ステーション）の発展により、生態系への負荷を最小化した研究が可能に。JAMSTECのDONETは南海トラフの長期監視を実現。</p>
  </div>
</div>

---

<!-- _class: summary-slide -->

## まとめ ― 深海探査の未来

<div class="summary-glass">
  <p>深海は地球表面の60%以上を占めながら、その95%以上が未探査のまま残されている。極限環境に適応した生命体は、新薬開発や生命の起源解明に繋がる可能性を秘めている。</p>
  <p style="margin-top:14px;">熱水噴出孔の化学合成生態系の発見は、地球外生命探査にも新たな視点を提供した。エウロパやエンケラドスの海底でも同様の生態系が存在する可能性が指摘されている。</p>
  <p style="margin-top:14px;">技術革新と環境保全を両立させ、人類最後のフロンティアである深海の解明を進めていくことが、21世紀の海洋科学に課せられた使命である。</p>
</div>

<div class="closing-line">The Deep Sea — 地球最後のフロンティア</div>
