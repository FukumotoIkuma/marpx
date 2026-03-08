---
marp: true
theme: default
size: 16:9
paginate: true
style: |
  /* ============================================================
     SPACE ARCHITECTURE: 宇宙建築の未来
     Ultra-heavy CSS presentation — 200+ lines of custom styles
     ============================================================ */

  /* ---------- Root color tokens ---------- */
  :root {
    --deep-space:    #0a0a23;
    --deep-navy:     #16213e;
    --nebula-purple: #533483;
    --nebula-magenta:#7b2d8e;
    --starlight:     #f8f9fa;
    --starlight-dim: #e2e8f0;
    --solar-gold:    #fbbf24;
    --mars-red:      #dc2626;
    --earth-blue:    #3b82f6;
    --lunar-gray:    #94a3b8;
    --void-black:    #020617;
  }

  /* ---------- Global section reset ---------- */
  section {
    background: var(--deep-space);
    color: var(--starlight);
    font-family: "Noto Sans JP", "Helvetica Neue", Arial, sans-serif;
    padding: 40px 60px;
    overflow: hidden;
  }
  section h1, section h2, section h3 {
    color: var(--starlight);
    letter-spacing: 0.04em;
  }

  /* ---------- 1. Title — starfield ---------- */
  section.title {
    background:
      repeating-radial-gradient(circle at 12% 28%, #ffffff22 0px, transparent 1px, transparent 80px),
      repeating-radial-gradient(circle at 55% 72%, #ffffff18 0px, transparent 1px, transparent 120px),
      repeating-radial-gradient(circle at 83% 15%, #ffffff25 0px, transparent 1.5px, transparent 60px),
      repeating-radial-gradient(circle at 37% 88%, #ffffff10 0px, transparent 1px, transparent 100px),
      repeating-radial-gradient(circle at 68% 42%, #ffffff15 0px, transparent 0.8px, transparent 90px),
      radial-gradient(ellipse at 30% 60%, #533483aa 0%, transparent 55%),
      radial-gradient(ellipse at 75% 35%, #16213ecc 0%, transparent 60%),
      var(--deep-space);
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  section.title h1 {
    font-size: 3.2em;
    background: linear-gradient(135deg, var(--solar-gold) 0%, #fff 40%, var(--earth-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
    filter: drop-shadow(0 0 30px rgba(251,191,36,0.4)) drop-shadow(0 0 60px rgba(59,130,246,0.25));
    margin-bottom: 0.1em;
  }
  section.title p.subtitle {
    font-size: 1.4em;
    color: var(--starlight-dim);
    text-shadow: 0 0 20px rgba(251,191,36,0.3);
    margin-top: 0;
  }
  section.title .star-deco {
    font-size: 2em;
    letter-spacing: 0.5em;
    color: var(--solar-gold);
    opacity: 0.5;
    margin-top: 30px;
  }

  /* ---------- 2. Orbital ring — conic gradient ---------- */
  section.orbital {
    background:
      conic-gradient(from 0deg at 50% 50%, transparent 0deg, #533483aa 30deg, transparent 60deg, transparent 120deg, #7b2d8e66 150deg, transparent 180deg, transparent 240deg, #3b82f644 270deg, transparent 300deg, transparent 360deg),
      radial-gradient(circle at 50% 50%, transparent 28%, #533483 28.5%, #53348300 29%, transparent 100%),
      radial-gradient(circle at 50% 50%, transparent 38%, #3b82f644 38.5%, #3b82f600 39%, transparent 100%),
      radial-gradient(circle at 50% 50%, #0a0a23 0%, #16213e 100%);
    padding: 60px 100px;
  }
  section.orbital .content-box {
    background: rgba(10,10,35,0.85);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 16px;
    padding: 30px 40px;
    box-shadow: 0 0 40px rgba(83,52,131,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
    max-width: 700px;
    margin: 0 auto;
  }
  section.orbital h2 {
    text-align: center;
    font-size: 2em;
    border-bottom: 2px solid var(--nebula-purple);
    padding-bottom: 10px;
  }

  /* ---------- 3. Lunar split — clip-path diagonal ---------- */
  section.lunar {
    background: var(--deep-space);
    padding: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr;
    gap: 0;
  }
  section.lunar .panel-left {
    background:
      linear-gradient(135deg, #1e293b 0%, #334155 100%);
    clip-path: polygon(0 0, 100% 0, 75% 100%, 0 100%);
    padding: 50px 80px 50px 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 8px 0 30px rgba(0,0,0,0.5);
    z-index: 2;
  }
  section.lunar .panel-right {
    background:
      repeating-radial-gradient(circle at 60% 50%, #94a3b811 0px, transparent 2px, transparent 30px),
      linear-gradient(225deg, #0f172a 0%, #1e293b 100%);
    clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%);
    margin-left: -80px;
    padding: 50px 60px 50px 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    z-index: 1;
  }
  section.lunar h2 {
    font-size: 1.8em;
    color: var(--starlight);
    border-image: linear-gradient(90deg, var(--lunar-gray), transparent) 1;
    border-bottom: 3px solid;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }
  section.lunar .spec-item {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 0.92em;
    color: var(--starlight-dim);
  }
  section.lunar .spec-item .label {
    color: var(--lunar-gray);
    min-width: 80px;
    text-align: right;
    font-size: 0.85em;
  }

  /* ---------- 4. Mars habitat — 3D perspective cards ---------- */
  section.mars {
    background:
      radial-gradient(ellipse at 80% 90%, rgba(220,38,38,0.15) 0%, transparent 50%),
      linear-gradient(180deg, #0a0a23 0%, #1a0505 100%);
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto 1fr;
    gap: 20px;
    padding: 40px 50px;
  }
  section.mars h2 {
    grid-column: 1 / -1;
    text-align: center;
    font-size: 2em;
    color: var(--mars-red);
    text-shadow: 0 0 20px rgba(220,38,38,0.4);
    margin: 0 0 5px 0;
  }
  section.mars .card-3d {
    background: linear-gradient(145deg, #1e1e2f 0%, #0f0f1f 100%);
    border: 1px solid rgba(220,38,38,0.25);
    border-radius: 12px;
    padding: 24px 20px;
    transform: perspective(800px) rotateY(-3deg) rotateX(2deg);
    box-shadow:
      8px 8px 24px rgba(0,0,0,0.6),
      -2px -2px 8px rgba(220,38,38,0.08),
      inset 0 1px 0 rgba(255,255,255,0.04);
    aspect-ratio: 4 / 3.5;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }
  section.mars .card-3d:nth-child(3) {
    transform: perspective(800px) rotateY(0deg) rotateX(2deg);
    border-color: rgba(251,191,36,0.25);
  }
  section.mars .card-3d:nth-child(4) {
    transform: perspective(800px) rotateY(3deg) rotateX(2deg);
  }
  section.mars .card-3d h3 {
    font-size: 1.15em;
    color: var(--mars-red);
    margin: 0 0 10px 0;
    border-bottom: 1px solid rgba(220,38,38,0.2);
    padding-bottom: 6px;
  }
  section.mars .card-3d:nth-child(3) h3 { color: var(--solar-gold); }
  section.mars .card-3d p { font-size: 0.78em; color: var(--starlight-dim); line-height: 1.6; margin: 4px 0; }

  /* ---------- 5. Space station — radial layout ---------- */
  section.station {
    background:
      radial-gradient(circle at 50% 50%, rgba(59,130,246,0.08) 0%, transparent 40%),
      var(--deep-space);
    position: relative;
  }
  section.station h2 {
    text-align: center;
    font-size: 1.8em;
    color: var(--earth-blue);
    margin-bottom: 20px;
  }
  section.station .hub {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 120px;
    height: 120px;
    background: conic-gradient(from 45deg, var(--earth-blue), var(--nebula-purple), var(--earth-blue));
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 40px rgba(59,130,246,0.4), 0 0 80px rgba(59,130,246,0.15);
    z-index: 10;
  }
  section.station .hub span { font-size: 0.7em; font-weight: 700; text-align: center; line-height: 1.2; }
  section.station .module {
    position: absolute;
    background: rgba(22,33,62,0.9);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 10px;
    padding: 12px 16px;
    width: 190px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
  }
  section.station .module h3 { font-size: 0.85em; color: var(--earth-blue); margin: 0 0 4px 0; }
  section.station .module p { font-size: 0.68em; color: var(--starlight-dim); margin: 0; line-height: 1.5; }
  section.station .m1 { top: 12%;  left: 8%; }
  section.station .m2 { top: 12%;  right: 8%; }
  section.station .m3 { bottom: 15%; left: 5%; }
  section.station .m4 { bottom: 15%; right: 5%; }
  section.station .m5 { top: 45%;  left: 3%; transform: translateY(-50%); }
  section.station .m6 { top: 45%;  right: 3%; transform: translateY(-50%); }

  /* ---------- 6. Materials — gradient-border embossed grid ---------- */
  section.materials {
    background: linear-gradient(160deg, #0a0a23 0%, #16213e 100%);
    display: grid;
    grid-template-columns: repeat(3, minmax(200px, 1fr));
    grid-template-rows: auto 1fr 1fr;
    gap: 16px;
    padding: 35px 50px;
  }
  section.materials h2 {
    grid-column: 1 / -1;
    text-align: center;
    font-size: 1.9em;
    margin: 0;
    background: linear-gradient(90deg, var(--solar-gold), var(--starlight));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  section.materials .mat-card {
    background: linear-gradient(145deg, #1a1a3a 0%, #0d0d24 100%);
    border-radius: 10px;
    padding: 18px 16px;
    border: 2px solid transparent;
    border-image: linear-gradient(135deg, var(--solar-gold) 0%, var(--nebula-purple) 50%, var(--earth-blue) 100%) 1;
    box-shadow:
      4px 4px 12px rgba(0,0,0,0.7),
      -2px -2px 6px rgba(255,255,255,0.02),
      inset 2px 2px 4px rgba(0,0,0,0.4),
      inset -1px -1px 3px rgba(255,255,255,0.03);
  }
  section.materials .mat-card h3 {
    font-size: 0.95em;
    color: var(--solar-gold);
    margin: 0 0 6px 0;
    text-decoration: underline;
    text-decoration-color: rgba(251,191,36,0.3);
    text-underline-offset: 4px;
  }
  section.materials .mat-card p { font-size: 0.72em; color: var(--starlight-dim); margin: 3px 0; line-height: 1.55; }
  section.materials .mat-card .bar {
    height: 3px;
    margin-top: 8px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--solar-gold) 0%, transparent 100%);
  }

  /* ---------- 7. Life support — grid flow diagram ---------- */
  section.lifesupport {
    background:
      linear-gradient(180deg, #0a0a23 0%, #0d1b2a 100%);
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: auto auto 1fr auto;
    gap: 10px 12px;
    padding: 35px 40px;
  }
  section.lifesupport h2 {
    grid-column: 1 / -1;
    text-align: center;
    font-size: 1.8em;
    margin: 0 0 5px 0;
    color: #22c55e;
  }
  section.lifesupport .desc {
    grid-column: 1 / -1;
    text-align: center;
    font-size: 0.8em;
    color: var(--starlight-dim);
    margin: 0 0 8px 0;
  }
  section.lifesupport .flow-node {
    background: rgba(22,33,62,0.85);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4), inset 0 1px 0 rgba(34,197,94,0.08);
  }
  section.lifesupport .flow-node h3 { font-size: 0.82em; color: #22c55e; margin: 0 0 5px 0; }
  section.lifesupport .flow-node p { font-size: 0.65em; color: var(--starlight-dim); margin: 0; line-height: 1.5; }
  section.lifesupport .arrow-right {
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(34,197,94,0.5);
    font-size: 1.5em;
  }
  section.lifesupport .cycle-label {
    grid-column: 1 / -1;
    text-align: center;
    font-size: 0.75em;
    color: rgba(34,197,94,0.6);
    margin-top: 4px;
    border-top: 1px dashed rgba(34,197,94,0.2);
    padding-top: 6px;
  }

  /* ---------- 8. Radiation — concentric shields ---------- */
  section.radiation {
    background:
      repeating-radial-gradient(circle at 50% 55%, transparent 0px, transparent 48px, rgba(251,191,36,0.06) 50px, transparent 52px, transparent 100px),
      repeating-radial-gradient(circle at 50% 55%, transparent 0px, transparent 98px, rgba(220,38,38,0.05) 100px, transparent 102px, transparent 150px),
      repeating-radial-gradient(circle at 50% 55%, transparent 0px, transparent 148px, rgba(59,130,246,0.04) 150px, transparent 152px, transparent 200px),
      radial-gradient(circle at 50% 55%, rgba(220,38,38,0.12) 0%, transparent 25%),
      var(--deep-space);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 35px 60px;
  }
  section.radiation h2 {
    font-size: 1.9em;
    text-align: center;
    color: var(--solar-gold);
    margin-bottom: 12px;
  }
  section.radiation .shield-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
    max-width: 750px;
  }
  section.radiation .shield {
    background: rgba(22,33,62,0.75);
    border-left: 4px solid var(--mars-red);
    border-radius: 0 8px 8px 0;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4), inset 0 0 20px rgba(220,38,38,0.03);
  }
  section.radiation .shield:nth-child(2) { border-left-color: var(--solar-gold); }
  section.radiation .shield:nth-child(3) { border-left-color: var(--earth-blue); }
  section.radiation .shield:nth-child(4) { border-left-color: var(--nebula-purple); }
  section.radiation .shield:nth-child(5) { border-left-color: #22c55e; }
  section.radiation .shield .layer-num {
    font-size: 1.6em;
    font-weight: 800;
    color: var(--mars-red);
    min-width: 40px;
    text-align: center;
  }
  section.radiation .shield:nth-child(2) .layer-num { color: var(--solar-gold); }
  section.radiation .shield:nth-child(3) .layer-num { color: var(--earth-blue); }
  section.radiation .shield:nth-child(4) .layer-num { color: var(--nebula-purple); }
  section.radiation .shield:nth-child(5) .layer-num { color: #22c55e; }
  section.radiation .shield h3 { font-size: 0.9em; margin: 0; color: var(--starlight); }
  section.radiation .shield p { font-size: 0.7em; margin: 2px 0 0 0; color: var(--starlight-dim); }

  /* ---------- 9. International — overlapping cards ---------- */
  section.international {
    background:
      linear-gradient(135deg, #0a0a23 0%, #16213e 50%, #0d1b2a 100%);
    padding: 35px 60px;
  }
  section.international h2 {
    text-align: center;
    font-size: 1.9em;
    margin-bottom: 20px;
    color: var(--earth-blue);
  }
  section.international .region-wrap {
    display: flex;
    justify-content: center;
    padding: 0 20px;
  }
  section.international .region {
    background: rgba(22,33,62,0.9);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 14px;
    padding: 22px 24px;
    width: 230px;
    margin-left: -20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative;
    mix-blend-mode: normal;
  }
  section.international .region:first-child { margin-left: 0; z-index: 5; }
  section.international .region:nth-child(2) { z-index: 4; border-color: rgba(251,191,36,0.2); }
  section.international .region:nth-child(3) { z-index: 3; border-color: rgba(220,38,38,0.2); }
  section.international .region:nth-child(4) { z-index: 2; border-color: rgba(123,45,142,0.2); }
  section.international .region h3 {
    font-size: 0.9em;
    margin: 0 0 8px 0;
    color: var(--earth-blue);
    text-decoration: underline;
    text-decoration-color: rgba(59,130,246,0.3);
    text-underline-offset: 3px;
  }
  section.international .region:nth-child(2) h3 { color: var(--solar-gold); text-decoration-color: rgba(251,191,36,0.3); }
  section.international .region:nth-child(3) h3 { color: var(--mars-red); text-decoration-color: rgba(220,38,38,0.3); }
  section.international .region:nth-child(4) h3 { color: var(--nebula-magenta); text-decoration-color: rgba(123,45,142,0.3); }
  section.international .region p { font-size: 0.68em; color: var(--starlight-dim); line-height: 1.55; margin: 3px 0; }

  /* ---------- 10. Summary — counter-numbered takeaways ---------- */
  section.summary {
    background:
      conic-gradient(from 180deg at 80% 20%, rgba(83,52,131,0.2) 0deg, transparent 90deg, transparent 360deg),
      radial-gradient(ellipse at 20% 80%, rgba(59,130,246,0.1) 0%, transparent 50%),
      radial-gradient(ellipse at 90% 90%, rgba(220,38,38,0.08) 0%, transparent 40%),
      linear-gradient(150deg, #0a0a23 0%, #16213e 40%, #0d1b2a 100%);
    padding: 35px 60px;
    counter-reset: takeaway;
  }
  section.summary h2 {
    text-align: center;
    font-size: 2em;
    margin-bottom: 16px;
    background: linear-gradient(90deg, var(--solar-gold), var(--starlight), var(--earth-blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  section.summary .takeaway {
    counter-increment: takeaway;
    background: rgba(22,33,62,0.7);
    border: 1px solid rgba(251,191,36,0.15);
    border-radius: 10px;
    padding: 14px 20px 14px 60px;
    margin-bottom: 10px;
    position: relative;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.02);
  }
  section.summary .takeaway::before {
    content: counter(takeaway, decimal-leading-zero);
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5em;
    font-weight: 800;
    color: var(--solar-gold);
    opacity: 0.7;
  }
  section.summary .takeaway h3 { font-size: 0.95em; color: var(--starlight); margin: 0 0 3px 0; }
  section.summary .takeaway p { font-size: 0.72em; color: var(--starlight-dim); margin: 0; line-height: 1.5; }
  section.summary .closing {
    text-align: center;
    margin-top: 16px;
    font-size: 0.85em;
    color: var(--solar-gold);
    letter-spacing: 0.15em;
  }
---

<!-- slide 1: title -->
<section class="title">

# Space Architecture: 宇宙建築の未来

<p class="subtitle">人類の宇宙居住を支える建築技術の最前線</p>

<div class="star-deco">★ ● ★ ● ★</div>

</section>

---

<!-- slide 2: why space architecture -->
<section class="orbital">

## なぜ宇宙建築か

<div class="content-box">

宇宙建築とは、地球外環境における人間の居住・活動空間を設計・構築する分野である。2020年代後半、アルテミス計画やSpaceX Starshipの進展により、月面・火星への持続的な人類進出が現実味を帯びている。

**核心的課題：**
- 真空・微小重力・放射線という極限環境への対応
- 地球からの物資輸送コスト（1kgあたり約100万円以上）の制約
- 現地資源利用（ISRU: In-Situ Resource Utilization）の必要性
- 居住者の身体的・心理的健康の維持

宇宙建築は、構造工学・材料科学・生命維持工学・人間工学の学際的統合を要求する、21世紀最大の建築的挑戦である。

</div>

</section>

---

<!-- slide 3: lunar base -->
<section class="lunar">

<div class="panel-left">

## 月面基地設計

月面基地は宇宙建築の最初の大規模実証となる。レゴリス（月の表土）を建材として活用し、3Dプリンティング技術で構造体を現地製造する計画が進む。

<div class="spec-item"><span class="label">重力</span> 地球の1/6（1.62 m/s²）</div>
<div class="spec-item"><span class="label">気温</span> -173℃〜127℃（昼夜差300℃）</div>
<div class="spec-item"><span class="label">大気</span> 実質真空（10⁻¹² atm）</div>
<div class="spec-item"><span class="label">放射線</span> 年間約380 mSv（地球の約150倍）</div>

</div>

<div class="panel-right">

### 構造アプローチ

**レゴリスシンタリング工法：** ESAのCONCEPTプロジェクトでは、マイクロ波焼結により月のレゴリスを建築用ブロックに変換する技術を開発中。

**溶岩チューブ活用：** 月面下の溶岩チューブ（直径数百m）を天然のシェルターとして利用。放射線遮蔽と温度安定性を同時に確保できる。

**インフレータブル構造：** NASA/Bigelow Aerospaceの膨張型モジュールは、打上げ時はコンパクトに、展開後は大容積の居住空間を提供。

</div>

</section>

---

<!-- slide 4: mars habitat -->
<section class="mars">

## 火星居住モジュール

<div class="card-3d">

### 与圧居住区
火星の大気圧は地球の約0.6%（636 Pa）であり、居住区には1気圧の与圧が必須。多層構造の外殻が微小隕石と放射線から居住者を保護する。二重エアロック方式により、EVA（船外活動）時の減圧リスクを最小化する。

</div>

<div class="card-3d">

### エネルギーシステム
火星での太陽光強度は地球の約43%。大面積の薄膜太陽電池パネルと、バックアップ用の小型原子炉（Kilopower）を併用する設計が主流。砂嵐時（数週間〜数ヶ月継続）は原子力が唯一の安定電源となる。

</div>

<div class="card-3d">

### 食料生産区画
水耕栽培・エアロポニクスによる植物工場を居住モジュールに統合。レタス、トマト、大豆、ジャガイモなどを栽培し、必須栄養素の60%以上を現地生産する目標。CO₂吸収と酸素供給の副次効果も重要。

</div>

</section>

---

<!-- slide 5: space station -->
<section class="station">

## 次世代宇宙ステーション

<div class="hub"><span>中央<br>ハブ</span></div>

<div class="module m1">

### 居住モジュール
人工重力区画を回転機構で実現。月面レベル（0.16G）から地球レベル（1G）まで可変。長期滞在者の骨密度・筋力低下を防止。

</div>

<div class="module m2">

### 研究モジュール
微小重力を活用した材料科学・生命科学の実験施設。地上では不可能な結晶成長や細胞培養を実施。

</div>

<div class="module m3">

### 製造モジュール
宇宙空間での3Dプリンティングとアセンブリ。大型構造物や衛星の軌道上製造を行い、打上げコストを削減。

</div>

<div class="module m4">

### 推進モジュール
イオンエンジンと化学推進の併用。軌道維持とデブリ回避機動を自律的に実行するAI制御システム搭載。

</div>

<div class="module m5">

### ドッキング港
最大6機の宇宙船同時接続。自動ドッキングシステムと緊急離脱機構を備えた万全の安全設計。

</div>

<div class="module m6">

### 太陽電池翼
ペロブスカイト太陽電池による高効率発電。総出力500kW級。回転機構で常時太陽追尾を実施。

</div>

</section>

---

<!-- slide 6: materials technology -->
<section class="materials">

## 建材技術イノベーション

<div class="mat-card">

### カーボンナノチューブ複合材
引張強度が鋼鉄の100倍、重量は1/6。宇宙エレベーターのテザー候補材料。現在は大量生産技術の確立が課題。
<div class="bar" style="width:90%"></div>

</div>

<div class="mat-card">

### エアロゲル断熱材
密度3 mg/cm³の超軽量断熱体。熱伝導率0.015 W/mKで、極端な温度差環境に最適。NASAのStardust計画で宇宙実証済み。
<div class="bar" style="width:85%"></div>

</div>

<div class="mat-card">

### 自己修復ポリマー
微小クラックを自動検知し、内包されたマイクロカプセルから修復剤を放出。与圧構造の長期健全性を維持する次世代材料。
<div class="bar" style="width:70%"></div>

</div>

<div class="mat-card">

### レゴリスコンクリート
月・火星の表土に硫黄バインダーを混合した宇宙コンクリート。水が不要で現地製造可能。圧縮強度は地球のコンクリートに匹敵。
<div class="bar" style="width:75%"></div>

</div>

<div class="mat-card">

### 放射線遮蔽セラミックス
ボロンカーバイドやハイドロキシアパタイト系のセラミックス。中性子線と荷電粒子線を効率的に吸収。構造材と遮蔽材の一体化を実現。
<div class="bar" style="width:65%"></div>

</div>

<div class="mat-card">

### 形状記憶合金フレーム
ニッケルチタン合金を用いた展開型構造。打上げ時は折り畳み、軌道上で加熱により設計形状に自動展開。省スペースで大型構造を実現。
<div class="bar" style="width:80%"></div>

</div>

</section>

---

<!-- slide 7: life support -->
<section class="lifesupport">

## 生命維持システム

<p class="desc">閉鎖生態系生命維持（CELSS）は、物質とエネルギーの循環により長期的に居住者の生存を支える統合システムである。</p>

<div class="flow-node">

### 大気制御
CO₂除去（アミン吸着）と O₂生成（電気分解）。気圧・湿度・温度を恒常的に維持。

</div>

<div class="arrow-right">▸</div>

<div class="flow-node">

### 水循環
尿・汗・排気中の水蒸気を回収・浄化。ISSでは93%の水を再利用。逆浸透膜+UV殺菌で飲料水品質を確保。

</div>

<div class="arrow-right">▸</div>

<div class="flow-node">

### 食料生産
LED植物工場で光合成を最適化。バイオリアクターで藻類（スピルリナ）を培養しタンパク質を補給。

</div>

<div class="cycle-label">★ 廃棄物 → 堆肥化 → 植物栽培基質 → 食料 → 代謝 → CO₂ + 水 → 電気分解 → O₂ ★ 閉鎖循環</div>

</section>

---

<!-- slide 8: radiation protection -->
<section class="radiation">

## 放射線防護：多層シールド戦略

<div class="shield-list">

<div class="shield">
<span class="layer-num">01</span>
<div>
<h3>電磁シールド（第1層）</h3>
<p>超伝導コイルによる磁気圏の人工的再現。荷電粒子を偏向させ、居住区への到達を防ぐ。消費電力が課題。</p>
</div>
</div>

<div class="shield">
<span class="layer-num">02</span>
<div>
<h3>水素リッチ材料層（第2層）</h3>
<p>ポリエチレンや水タンクを構造壁に統合。水素原子核が二次放射線の生成を最小化し、最も効率的な受動遮蔽を提供。</p>
</div>
</div>

<div class="shield">
<span class="layer-num">03</span>
<div>
<h3>レゴリス外殻（第3層）</h3>
<p>2〜3mの月面レゴリス層は、銀河宇宙線を約50%低減。ロボットによる自動積層施工で、人間のEVA不要。</p>
</div>
</div>

<div class="shield">
<span class="layer-num">04</span>
<div>
<h3>シェルター区画（第4層）</h3>
<p>太陽フレア時の緊急退避室。全方位30 g/cm²以上の遮蔽を確保し、数日間の高線量イベントに対応。</p>
</div>
</div>

<div class="shield">
<span class="layer-num">05</span>
<div>
<h3>生体防御（第5層）</h3>
<p>放射線防護薬（アミフォスチン等）と遺伝子治療によるDNA修復能力の強化。宇宙医学の最前線。</p>
</div>
</div>

</div>

</section>

---

<!-- slide 9: international cooperation -->
<section class="international">

## 国際協力と宇宙建築

<div class="region-wrap">

<div class="region">

### 北米・NASA
アルテミス計画で月面Gateway建設を主導。Lunar Surface Habitatの設計をAxiom Spaceと共同開発。CHAPEA（火星模擬居住実験）により1年間の閉鎖居住データを蓄積中。

</div>

<div class="region">

### 欧州・ESA
Moon Villageコンセプトを提唱。レゴリス3Dプリンティング技術でリード。CONCRETEプロジェクトで月面建設ロボットを開発中。国際宇宙法の整備にも主導的役割。

</div>

<div class="region">

### アジア・JAXA/CNSA
JAXAは有人与圧ローバーで月面探査の足場を構築。CNSAは天宮ステーションで長期滞在技術を実証し、国際月面研究ステーション（ILRS）を計画。インドISROも月探査に参入。

</div>

<div class="region">

### 民間セクター
SpaceXのStarship、Blue OriginのBlue Moon、Sierra SpaceのDream Chaserが輸送インフラを担う。Vast社の人工重力ステーションHaven-1は商業宇宙建築の先駆け。

</div>

</div>

</section>

---

<!-- slide 10: summary -->
<section class="summary">

## まとめ：宇宙建築が拓く未来

<div class="takeaway">

### 現地資源利用（ISRU）が建設コストの鍵
月面レゴリスや火星の氷を活用することで、地球からの輸送依存を大幅に削減。建設コストを1/10以下に抑える技術的目処が立ちつつある。

</div>

<div class="takeaway">

### 閉鎖生態系技術は地球環境問題にも応用可能
宇宙で培われた水循環・大気制御・食料生産技術は、砂漠緑化や気候変動対策にも直接的に転用できる。

</div>

<div class="takeaway">

### 放射線防護が最大の技術的障壁
深宇宙放射線の完全遮蔽には、能動的（電磁）・受動的（物質）防御の多層アプローチと生体医学的介入の統合が不可欠。

</div>

<div class="takeaway">

### 国際協力と民間投資の両輪が不可欠
宇宙建築は一国では実現不可能。国際的な技術標準化と、民間企業の資金・イノベーションの融合が成功の必須条件。

</div>

<div class="takeaway">

### 2040年代の恒久月面基地が次のマイルストーン
アルテミス計画の成功を足がかりに、2040年代には数十人規模の恒久居住施設が実現する見通し。火星は2050年代。

</div>

<p class="closing">★ 宇宙建築は人類文明の次のフロンティアである ★</p>

</section>
