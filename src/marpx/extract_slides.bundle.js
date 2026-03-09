() => {
// backgrounds.js
function extractBackgroundImages(slideRoot, advBg, section) {
  const bgImages = [];
  if (advBg === "content") {
    const slideRect = slideRoot.getBoundingClientRect();
    const splitValue = window.getComputedStyle(section).getPropertyValue("--marpit-advanced-background-split").trim();
    const splitRatio = splitValue.endsWith("%") ? Math.max(0, Math.min(parseFloat(splitValue) / 100, 1)) : null;
    const bgSection = slideRoot.querySelector(
      'section[data-marpit-advanced-background="background"]'
    );
    if (bgSection) {
      const figures = bgSection.querySelectorAll("figure");
      for (const fig of figures) {
        const figCs = window.getComputedStyle(fig);
        const bgImg = figCs.backgroundImage;
        if (bgImg && bgImg !== "none") {
          const urlMatch = bgImg.match(/url\(["']?([^"')]+)["']?\)/);
          if (urlMatch) {
            const figRect = fig.getBoundingClientRect();
            bgImages.push({
              url: urlMatch[1],
              size: figCs.backgroundSize || "cover",
              position: figCs.backgroundPosition || "center",
              splitRatio,
              box: {
                x: figRect.left - slideRect.left,
                y: figRect.top - slideRect.top,
                width: figRect.width,
                height: figRect.height
              }
            });
          }
        }
      }
    }
    const split = section.getAttribute("data-marpit-advanced-background-split");
    if (split) {
      for (const bg of bgImages) {
        bg.split = split;
      }
    }
  }
  return bgImages;
}
function extractDirectives(section) {
  const paginate = section.getAttribute("data-paginate") === "true";
  const paginationNum = section.getAttribute("data-marpit-pagination");
  const paginationTotal = section.getAttribute("data-marpit-pagination-total");
  const headerEl = section.querySelector(":scope > header");
  const footerEl = section.querySelector(":scope > footer");
  return {
    paginate,
    pageNumber: paginationNum ? parseInt(paginationNum) : null,
    pageTotal: paginationTotal ? parseInt(paginationTotal) : null,
    headerText: headerEl ? headerEl.textContent.trim() : null,
    footerText: footerEl ? footerEl.textContent.trim() : null
  };
}

// render-context.js
function _parseOpacity(raw) {
  const parsed = parseFloat(raw || "1");
  if (!Number.isFinite(parsed)) return 1;
  return Math.max(0, Math.min(parsed, 1));
}
function createRenderContext(effectiveOpacity = 1) {
  return {
    effectiveOpacity: Math.max(0, Math.min(effectiveOpacity, 1)),
    effectiveScaleX: 1,
    effectiveScaleY: 1,
    effectiveRotationDeg: 0,
    effectiveRotation3dXDeg: 0,
    effectiveRotation3dYDeg: 0,
    effectiveRotation3dZDeg: 0
  };
}
function _clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
function _parseTransformScale(transform) {
  if (!transform || transform === "none" || transform === "matrix(1, 0, 0, 1, 0, 0)") {
    return {
      scaleX: 1,
      scaleY: 1,
      rotationDeg: 0,
      rotation3dXDeg: 0,
      rotation3dYDeg: 0,
      rotation3dZDeg: 0,
      complex: false
    };
  }
  if (transform.startsWith("matrix3d(")) {
    const vals2 = transform.slice(9, -1).split(",").map((value) => parseFloat(value.trim()));
    if (vals2.length !== 16 || vals2.some((value) => !Number.isFinite(value))) {
      return {
        scaleX: 1,
        scaleY: 1,
        rotationDeg: 0,
        rotation3dXDeg: 0,
        rotation3dYDeg: 0,
        rotation3dZDeg: 0,
        complex: true
      };
    }
    return {
      scaleX: 1,
      scaleY: 1,
      rotationDeg: 0,
      rotation3dXDeg: Math.asin(_clamp(-vals2[9], -1, 1)) * (180 / Math.PI),
      rotation3dYDeg: Math.asin(_clamp(vals2[2], -1, 1)) * (180 / Math.PI),
      rotation3dZDeg: 0,
      complex: false
    };
  }
  const matrixMatch = transform.match(/matrix\(([^)]+)\)/);
  if (!matrixMatch) {
    return {
      scaleX: 1,
      scaleY: 1,
      rotationDeg: 0,
      rotation3dXDeg: 0,
      rotation3dYDeg: 0,
      rotation3dZDeg: 0,
      complex: true
    };
  }
  const vals = matrixMatch[1].split(",").map((value) => parseFloat(value.trim()));
  if (vals.length !== 6 || vals.some((value) => !Number.isFinite(value))) {
    return {
      scaleX: 1,
      scaleY: 1,
      rotationDeg: 0,
      rotation3dXDeg: 0,
      rotation3dYDeg: 0,
      rotation3dZDeg: 0,
      complex: true
    };
  }
  const [a, b, c, d] = vals;
  const scaleX = Math.hypot(a, b);
  const scaleY = Math.hypot(c, d);
  const dot = a * c + b * d;
  if (scaleX <= 1e-4 || scaleY <= 1e-4 || Math.abs(dot) > 0.01) {
    return {
      scaleX: 1,
      scaleY: 1,
      rotationDeg: 0,
      rotation3dXDeg: 0,
      rotation3dYDeg: 0,
      rotation3dZDeg: 0,
      complex: true
    };
  }
  return {
    scaleX,
    scaleY,
    rotationDeg: Math.atan2(b, a) * (180 / Math.PI),
    rotation3dXDeg: 0,
    rotation3dYDeg: 0,
    rotation3dZDeg: 0,
    complex: false
  };
}
function _textScale(ctx) {
  return (ctx.effectiveScaleX + ctx.effectiveScaleY) / 2;
}
function _scaleX(value, ctx) {
  return value * ctx.effectiveScaleX;
}
function _scaleY(value, ctx) {
  return value * ctx.effectiveScaleY;
}
function _scaleText(value, ctx) {
  return value * _textScale(ctx);
}
function deriveRenderContext(el, parentCtx = null, computedStyle = null) {
  if (!el) return parentCtx || createRenderContext();
  const cs = computedStyle || window.getComputedStyle(el);
  const ownOpacity = _parseOpacity(cs.opacity);
  const ownTransform = _parseTransformScale(cs.transform);
  if (parentCtx) {
    const ctx2 = createRenderContext(parentCtx.effectiveOpacity * ownOpacity);
    ctx2.effectiveScaleX = parentCtx.effectiveScaleX * ownTransform.scaleX;
    ctx2.effectiveScaleY = parentCtx.effectiveScaleY * ownTransform.scaleY;
    ctx2.effectiveRotationDeg = parentCtx.effectiveRotationDeg + ownTransform.rotationDeg;
    ctx2.effectiveRotation3dXDeg = parentCtx.effectiveRotation3dXDeg + ownTransform.rotation3dXDeg;
    ctx2.effectiveRotation3dYDeg = parentCtx.effectiveRotation3dYDeg + ownTransform.rotation3dYDeg;
    ctx2.effectiveRotation3dZDeg = parentCtx.effectiveRotation3dZDeg + ownTransform.rotation3dZDeg;
    return ctx2;
  }
  let effectiveOpacity = ownOpacity;
  let effectiveScaleX = ownTransform.scaleX;
  let effectiveScaleY = ownTransform.scaleY;
  let effectiveRotationDeg = ownTransform.rotationDeg;
  let effectiveRotation3dXDeg = ownTransform.rotation3dXDeg;
  let effectiveRotation3dYDeg = ownTransform.rotation3dYDeg;
  let effectiveRotation3dZDeg = ownTransform.rotation3dZDeg;
  let current = el.parentElement;
  while (current) {
    const currentStyle = window.getComputedStyle(current);
    effectiveOpacity *= _parseOpacity(currentStyle.opacity);
    const currentTransform = _parseTransformScale(currentStyle.transform);
    effectiveScaleX *= currentTransform.scaleX;
    effectiveScaleY *= currentTransform.scaleY;
    effectiveRotationDeg += currentTransform.rotationDeg;
    effectiveRotation3dXDeg += currentTransform.rotation3dXDeg;
    effectiveRotation3dYDeg += currentTransform.rotation3dYDeg;
    effectiveRotation3dZDeg += currentTransform.rotation3dZDeg;
    current = current.parentElement;
  }
  const ctx = createRenderContext(effectiveOpacity);
  ctx.effectiveScaleX = effectiveScaleX;
  ctx.effectiveScaleY = effectiveScaleY;
  ctx.effectiveRotationDeg = effectiveRotationDeg;
  ctx.effectiveRotation3dXDeg = effectiveRotation3dXDeg;
  ctx.effectiveRotation3dYDeg = effectiveRotation3dYDeg;
  ctx.effectiveRotation3dZDeg = effectiveRotation3dZDeg;
  return ctx;
}
function deriveSubtreeRenderContext(target, rootEl, rootContext = null) {
  if (target === rootEl) {
    return rootContext || deriveRenderContext(rootEl);
  }
  const chain = [];
  let current = target;
  while (current && current !== rootEl) {
    chain.push(current);
    current = current.parentElement;
  }
  if (current !== rootEl) {
    return deriveRenderContext(target);
  }
  let context = rootContext || deriveRenderContext(rootEl);
  for (let index = chain.length - 1; index >= 0; index--) {
    context = deriveRenderContext(chain[index], context);
  }
  return context;
}

// style.js
function _parseCssColor(color) {
  if (!color) return null;
  const normalized = color.trim().toLowerCase();
  if (!normalized || normalized === "transparent") {
    return { r: 0, g: 0, b: 0, a: 0 };
  }
  const match = normalized.match(
    /^rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*[,/]\s*([0-9.]+))?\s*\)$/
  );
  if (!match) return null;
  return {
    r: Math.max(0, Math.min(parseFloat(match[1]), 255)),
    g: Math.max(0, Math.min(parseFloat(match[2]), 255)),
    b: Math.max(0, Math.min(parseFloat(match[3]), 255)),
    a: match[4] === void 0 ? 1 : Math.max(0, Math.min(parseFloat(match[4]), 1))
  };
}
function applyOpacityToColor(color, opacity) {
  const parsed = _parseCssColor(color);
  if (!parsed) return color;
  const alpha = Math.max(0, Math.min(parsed.a * opacity, 1));
  return `rgba(${parsed.r}, ${parsed.g}, ${parsed.b}, ${alpha})`;
}
function _isTransparentTextFill(cs) {
  const textFill = _parseCssColor(cs.webkitTextFillColor || "");
  if (textFill) return textFill.a === 0;
  const color = _parseCssColor(cs.color || "");
  return !!color && color.a === 0;
}
function _extractTextGradient(cs, ctx) {
  const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || "").toLowerCase();
  if (backgroundClip.includes("text") && cs.backgroundImage && cs.backgroundImage.includes("gradient(") && _isTransparentTextFill(cs)) {
    return _applyOpacityToGradient(cs.backgroundImage, ctx.effectiveOpacity);
  }
  return null;
}
function getUnsupportedStyleReason(cs) {
  const filter = cs.filter || "";
  if (filter && filter !== "none") {
    return "CSS filter";
  }
  return null;
}
function _splitTopLevelCommas(value) {
  const parts = [];
  let current = "";
  let depth = 0;
  for (const char of value) {
    if (char === "(") depth += 1;
    if (char === ")") depth = Math.max(depth - 1, 0);
    if (char === "," && depth === 0) {
      parts.push(current.trim());
      current = "";
      continue;
    }
    current += char;
  }
  if (current.trim()) parts.push(current.trim());
  return parts;
}
function _extractRepresentativeGradientColor(backgroundImage) {
  if (!backgroundImage || !backgroundImage.includes("gradient(")) return null;
  const open = backgroundImage.indexOf("(");
  const close = backgroundImage.lastIndexOf(")");
  if (open < 0 || close <= open) return null;
  const inner = backgroundImage.slice(open + 1, close);
  const parts = _splitTopLevelCommas(inner);
  const stopParts = parts.filter((part, index) => {
    const lowered = part.trim().toLowerCase();
    if (index === 0 && (lowered.startsWith("to ") || lowered.endsWith("deg") || lowered.startsWith("at "))) {
      return false;
    }
    return true;
  });
  if (stopParts.length === 0) return null;
  const firstStop = stopParts[0].replace(/\s+[0-9.]+%\s*$/, "").trim();
  return firstStop || null;
}
function _applyOpacityToGradient(backgroundImage, opacity) {
  if (!backgroundImage || !backgroundImage.includes("gradient(")) return backgroundImage;
  const open = backgroundImage.indexOf("(");
  const close = backgroundImage.lastIndexOf(")");
  if (open < 0 || close <= open) return backgroundImage;
  const fnName = backgroundImage.slice(0, open);
  const inner = backgroundImage.slice(open + 1, close);
  const parts = _splitTopLevelCommas(inner);
  const rewritten = parts.map((part, index) => {
    const lowered = part.trim().toLowerCase();
    if (index === 0 && (lowered.startsWith("to ") || lowered.endsWith("deg") || lowered.startsWith("at "))) {
      return part.trim();
    }
    const match = part.match(/^(.*?)(\s+[0-9.]+%\s*)?$/);
    if (!match) return part.trim();
    const colorPart = match[1].trim();
    const positionPart = match[2] || "";
    return `${applyOpacityToColor(colorPart, opacity)}${positionPart}`;
  });
  return `${fnName}(${rewritten.join(", ")})`;
}
function _splitTopLevelSpaces(value) {
  const parts = [];
  let current = "";
  let depth = 0;
  for (const char of value) {
    if (char === "(") depth += 1;
    if (char === ")") depth = Math.max(depth - 1, 0);
    if (/\s/.test(char) && depth === 0) {
      if (current) {
        parts.push(current);
        current = "";
      }
      continue;
    }
    current += char;
  }
  if (current) parts.push(current);
  return parts;
}
function _isCssLengthToken(token) {
  return /^-?(?:\d+|\d*\.\d+)(?:px|r?em|%|pt)?$/i.test(token);
}
function _resolveCssColorToken(token, fallbackColor) {
  if (!token) return fallbackColor;
  const probe = document.createElement("span");
  probe.style.color = "";
  probe.style.color = token;
  if (!probe.style.color) return fallbackColor;
  return probe.style.color;
}
function _parseBoxShadow(boxShadow, fallbackColor, ctx) {
  if (!boxShadow || boxShadow === "none") return [];
  return _splitTopLevelCommas(boxShadow).map((shadowValue) => {
    const tokens = _splitTopLevelSpaces(shadowValue);
    if (tokens.length < 2) return null;
    let inset = false;
    const lengthTokens = [];
    const colorTokens = [];
    for (const token of tokens) {
      if (token === "inset") {
        inset = true;
        continue;
      }
      if (_isCssLengthToken(token)) {
        lengthTokens.push(token);
        continue;
      }
      colorTokens.push(token);
    }
    if (lengthTokens.length < 2) return null;
    const color = applyOpacityToColor(
      _resolveCssColorToken(
        colorTokens.join(" ").trim(),
        fallbackColor
      ),
      ctx.effectiveOpacity
    );
    return {
      offsetXPx: _scaleX(parseFloat(lengthTokens[0]) || 0, ctx),
      offsetYPx: _scaleY(parseFloat(lengthTokens[1]) || 0, ctx),
      blurRadiusPx: _scaleText(parseFloat(lengthTokens[2]) || 0, ctx),
      spreadPx: _scaleText(parseFloat(lengthTokens[3]) || 0, ctx),
      color,
      inset
    };
  }).filter((shadow) => shadow !== null);
}
function _resolveRunTextColor(cs, ctx) {
  const textFill = _parseCssColor(cs.webkitTextFillColor || "");
  const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || "").toLowerCase();
  if (textFill && textFill.a === 0 && backgroundClip.includes("text") && cs.backgroundImage && cs.backgroundImage.includes("linear-gradient(")) {
    const representative = _extractRepresentativeGradientColor(cs.backgroundImage);
    if (representative) {
      return applyOpacityToColor(representative, ctx.effectiveOpacity);
    }
  }
  return applyOpacityToColor(cs.color, ctx.effectiveOpacity);
}
function _resolveEffectiveTextDecoration(el, cs) {
  const decorations = /* @__PURE__ */ new Set();
  const addTokens = (value) => {
    for (const token of (value || "").split(/\s+/)) {
      if (token && token !== "none") decorations.add(token);
    }
  };
  addTokens(cs.textDecorationLine || cs.textDecoration || "");
  let current = el ? el.parentElement : null;
  while (current) {
    const currentStyle = window.getComputedStyle(current);
    addTokens(currentStyle.textDecorationLine || currentStyle.textDecoration || "");
    current = current.parentElement;
  }
  return decorations;
}
function _runBackgroundColor(el, cs) {
  if (!el) return "transparent";
  const tag = (el.localName || el.tagName || "").toLowerCase();
  const display = cs.display || "";
  if (display.startsWith("inline") || ["code", "mark", "kbd", "samp"].includes(tag)) {
    return cs.backgroundColor;
  }
  return "transparent";
}
function styleToRunStyle(cs, el = null, renderContext = null) {
  const textDecoration = _resolveEffectiveTextDecoration(el, cs);
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  const textGradient = _extractTextGradient(cs, ctx);
  return {
    fontFamily: cs.fontFamily,
    fontSizePx: _scaleText(parseFloat(cs.fontSize), ctx),
    bold: parseInt(cs.fontWeight) >= 600 || cs.fontWeight === "bold",
    italic: cs.fontStyle === "italic",
    underline: textDecoration.has("underline"),
    strike: textDecoration.has("line-through"),
    color: _resolveRunTextColor(cs, ctx),
    backgroundColor: applyOpacityToColor(_runBackgroundColor(el, cs), ctx.effectiveOpacity),
    textGradient
  };
}

// decoration.js
function _extractDecorationFromComputedStyle(cs, ctx) {
  const backgroundClip = (cs.webkitBackgroundClip || cs.backgroundClip || "").toLowerCase();
  const hasTextClippedGradient = backgroundClip.includes("text");
  const borderSide = (side) => {
    const width = side === "Left" || side === "Right" ? _scaleX(parseFloat(cs[`border${side}Width`]) || 0, ctx) : _scaleY(parseFloat(cs[`border${side}Width`]) || 0, ctx);
    return {
      widthPx: width,
      style: cs[`border${side}Style`] || "none",
      color: width > 0 ? applyOpacityToColor(cs[`border${side}Color`], ctx.effectiveOpacity) : null
    };
  };
  return {
    backgroundColor: applyOpacityToColor(cs.backgroundColor, ctx.effectiveOpacity),
    backgroundGradient: !hasTextClippedGradient && cs.backgroundImage && cs.backgroundImage.includes("gradient(") ? _applyOpacityToGradient(cs.backgroundImage, ctx.effectiveOpacity) : null,
    borderTop: borderSide("Top"),
    borderRight: borderSide("Right"),
    borderBottom: borderSide("Bottom"),
    borderLeft: borderSide("Left"),
    borderRadiusPx: _scaleText(parseFloat(cs.borderTopLeftRadius) || 0, ctx),
    padding: {
      topPx: _scaleY(parseFloat(cs.paddingTop) || 0, ctx),
      rightPx: _scaleX(parseFloat(cs.paddingRight) || 0, ctx),
      bottomPx: _scaleY(parseFloat(cs.paddingBottom) || 0, ctx),
      leftPx: _scaleX(parseFloat(cs.paddingLeft) || 0, ctx)
    },
    boxShadows: _parseBoxShadow(
      cs.boxShadow,
      cs.color || "rgba(0, 0, 0, 1)",
      ctx
    ),
    opacity: 1
  };
}
function extractDecoration(el, renderContext = null) {
  const cs = window.getComputedStyle(el);
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  return _extractDecorationFromComputedStyle(cs, ctx);
}
function hasMeaningfulDecoration(decoration) {
  const normalizedBg = decoration.backgroundColor ? decoration.backgroundColor.replace(/\s+/g, "").toLowerCase() : "";
  const hasVisibleBackground = normalizedBg && normalizedBg !== "rgba(0,0,0,0)" && normalizedBg !== "transparent";
  const hasGradientBackground = !!(decoration.backgroundGradient && decoration.backgroundGradient !== "none");
  const hasBoxShadow = (decoration.boxShadows || []).some((shadow) => {
    if (shadow.inset || !shadow.color) return false;
    const normalized = shadow.color.replace(/\s+/g, "").toLowerCase();
    return normalized !== "transparent" && normalized !== "rgba(0,0,0,0)" && normalized !== "rgb(0,0,0,0)";
  });
  const borders = [
    decoration.borderTop,
    decoration.borderRight,
    decoration.borderBottom,
    decoration.borderLeft
  ];
  const hasVisibleBorder = borders.some(
    (b) => b.widthPx > 0 && b.style && b.style !== "none"
  );
  const hasRadius = decoration.borderRadiusPx > 0;
  return hasVisibleBackground || hasGradientBackground || hasVisibleBorder || hasRadius || hasBoxShadow;
}
function normalizeContentValue(content) {
  if (!content || content === "none" || content === "normal") return null;
  if (content.startsWith('"') && content.endsWith('"') || content.startsWith("'") && content.endsWith("'")) {
    try {
      return JSON.parse(content);
    } catch (_err) {
      return content.slice(1, -1);
    }
  }
  return content;
}
function extractPseudoRuns(el, pseudo, renderContext = null) {
  const cs = window.getComputedStyle(el, pseudo);
  if (["absolute", "fixed"].includes(cs.position)) return [];
  const content = normalizeContentValue(cs.content);
  if (!content) return [];
  const ctx = renderContext || deriveRenderContext(el);
  return [{
    text: content,
    style: styleToRunStyle(cs, el, ctx),
    linkUrl: null
  }];
}
function _parsePseudoZIndex(cs, fallbackZ) {
  const parsed = parseInt(cs.zIndex, 10);
  return Number.isFinite(parsed) ? parsed : fallbackZ;
}
function _buildPseudoParagraph(content, cs, el, ctx) {
  return [{
    runs: [{
      text: content,
      style: styleToRunStyle(cs, el, ctx),
      linkUrl: null
    }],
    alignment: cs.textAlign || "left",
    lineHeightPx: parseFloat(cs.lineHeight) || null,
    spaceBeforePx: 0,
    spaceAfterPx: 0
  }];
}
function _measurePseudoRect(el, pseudo, content) {
  const pseudoCs = window.getComputedStyle(el, pseudo);
  const probe = document.createElement(content ? "span" : "div");
  probe.textContent = content || "";
  probe.setAttribute("aria-hidden", "true");
  probe.style.position = pseudoCs.position;
  probe.style.display = content ? "inline-block" : "block";
  probe.style.visibility = "hidden";
  probe.style.pointerEvents = "none";
  probe.style.margin = "0";
  probe.style.left = pseudoCs.left;
  probe.style.right = pseudoCs.right;
  probe.style.top = pseudoCs.top;
  probe.style.bottom = pseudoCs.bottom;
  probe.style.width = pseudoCs.width;
  probe.style.height = pseudoCs.height;
  probe.style.minWidth = pseudoCs.minWidth;
  probe.style.minHeight = pseudoCs.minHeight;
  probe.style.maxWidth = pseudoCs.maxWidth;
  probe.style.maxHeight = pseudoCs.maxHeight;
  probe.style.boxSizing = pseudoCs.boxSizing;
  probe.style.paddingTop = pseudoCs.paddingTop;
  probe.style.paddingRight = pseudoCs.paddingRight;
  probe.style.paddingBottom = pseudoCs.paddingBottom;
  probe.style.paddingLeft = pseudoCs.paddingLeft;
  probe.style.borderTopWidth = pseudoCs.borderTopWidth;
  probe.style.borderRightWidth = pseudoCs.borderRightWidth;
  probe.style.borderBottomWidth = pseudoCs.borderBottomWidth;
  probe.style.borderLeftWidth = pseudoCs.borderLeftWidth;
  probe.style.borderTopStyle = pseudoCs.borderTopStyle;
  probe.style.borderRightStyle = pseudoCs.borderRightStyle;
  probe.style.borderBottomStyle = pseudoCs.borderBottomStyle;
  probe.style.borderLeftStyle = pseudoCs.borderLeftStyle;
  probe.style.borderTopColor = pseudoCs.borderTopColor;
  probe.style.borderRightColor = pseudoCs.borderRightColor;
  probe.style.borderBottomColor = pseudoCs.borderBottomColor;
  probe.style.borderLeftColor = pseudoCs.borderLeftColor;
  probe.style.borderTopLeftRadius = pseudoCs.borderTopLeftRadius;
  probe.style.borderTopRightRadius = pseudoCs.borderTopRightRadius;
  probe.style.borderBottomRightRadius = pseudoCs.borderBottomRightRadius;
  probe.style.borderBottomLeftRadius = pseudoCs.borderBottomLeftRadius;
  probe.style.backgroundColor = pseudoCs.backgroundColor;
  probe.style.backgroundImage = pseudoCs.backgroundImage;
  probe.style.color = pseudoCs.color;
  probe.style.fontFamily = pseudoCs.fontFamily;
  probe.style.fontSize = pseudoCs.fontSize;
  probe.style.fontWeight = pseudoCs.fontWeight;
  probe.style.fontStyle = pseudoCs.fontStyle;
  probe.style.lineHeight = pseudoCs.lineHeight;
  probe.style.letterSpacing = pseudoCs.letterSpacing;
  probe.style.whiteSpace = pseudoCs.whiteSpace;
  probe.style.textAlign = pseudoCs.textAlign;
  probe.style.transform = pseudoCs.transform;
  probe.style.transformOrigin = pseudoCs.transformOrigin;
  probe.style.opacity = pseudoCs.opacity;
  el.appendChild(probe);
  const rect = probe.getBoundingClientRect();
  probe.remove();
  return rect;
}
function extractBlockPseudoElements(el, sectionRect, renderContext = null) {
  const results = [];
  const parentZ = _getZIndex(el);
  const ctx = renderContext || deriveRenderContext(el);
  for (const pseudo of ["::before", "::after"]) {
    const cs = window.getComputedStyle(el, pseudo);
    const content = normalizeContentValue(cs.content) || "";
    const unsupportedReason = getUnsupportedStyleReason(cs);
    if (!["absolute", "fixed"].includes(cs.position)) continue;
    const decoration = _extractDecorationFromComputedStyle(cs, ctx);
    const hasText = content.length > 0;
    if (!hasText && !hasMeaningfulDecoration(decoration) && !unsupportedReason) continue;
    const rect = _measurePseudoRect(el, pseudo, content);
    if (rect.width <= 0 || rect.height <= 0) continue;
    if (unsupportedReason) {
      results.push({
        type: "unsupported",
        box: _boxFromRect(rect, sectionRect),
        zIndex: _parsePseudoZIndex(cs, parentZ),
        unsupportedInfo: {
          reason: unsupportedReason,
          tagName: "pseudo"
        }
      });
      continue;
    }
    results.push({
      type: "decorated_block",
      box: _boxFromRect(rect, sectionRect),
      contentBox: hasMeaningfulDecoration(decoration) ? _contentBoxFromRectAndStyle(rect, cs, sectionRect, ctx) : null,
      zIndex: _parsePseudoZIndex(cs, parentZ),
      paragraphs: hasText ? _buildPseudoParagraph(content, cs, el, ctx) : [],
      decoration: hasMeaningfulDecoration(decoration) ? decoration : null
    });
  }
  return results;
}
function _getZIndex(el) {
  const raw = window.getComputedStyle(el).zIndex;
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : 0;
}
function _boxFromRect(rect, sectionRect) {
  return {
    x: rect.left - sectionRect.left,
    y: rect.top - sectionRect.top,
    width: rect.width,
    height: rect.height
  };
}
function _contentBoxFromRectAndStyle(rect, cs, sectionRect, ctx) {
  const leftInset = _scaleX((parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0), ctx);
  const topInset = _scaleY((parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0), ctx);
  const rightInset = _scaleX((parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0), ctx);
  const bottomInset = _scaleY((parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0), ctx);
  return {
    x: rect.left - sectionRect.left + leftInset,
    y: rect.top - sectionRect.top + topInset,
    width: Math.max(rect.width - leftInset - rightInset, 1),
    height: Math.max(rect.height - topInset - bottomInset, 1)
  };
}

// entry.js
function getComputedStyles(el) {
  const cs = window.getComputedStyle(el);
  return {
    fontFamily: cs.fontFamily,
    fontSize: cs.fontSize,
    fontWeight: cs.fontWeight,
    fontStyle: cs.fontStyle,
    textDecoration: cs.textDecorationLine || cs.textDecoration,
    color: cs.color,
    textAlign: cs.textAlign,
    backgroundColor: cs.backgroundColor,
    backgroundImage: cs.backgroundImage,
    backgroundClip: cs.backgroundClip,
    webkitBackgroundClip: cs.webkitBackgroundClip,
    webkitTextFillColor: cs.webkitTextFillColor,
    lineHeight: cs.lineHeight,
    marginTop: cs.marginTop,
    marginBottom: cs.marginBottom,
    display: cs.display,
    alignItems: cs.alignItems,
    justifyContent: cs.justifyContent,
    flexDirection: cs.flexDirection
  };
}
function resolveVerticalAlign(cs) {
  const display = (cs.display || "").toLowerCase();
  if (display.includes("flex")) {
    const flexDirection = (cs.flexDirection || "row").toLowerCase();
    const crossAxisAlign = (cs.alignItems || "").toLowerCase();
    const mainAxisJustify = (cs.justifyContent || "").toLowerCase();
    const relevant = flexDirection.startsWith("column") ? mainAxisJustify : crossAxisAlign;
    if (relevant.includes("center")) return "middle";
    if (relevant.includes("end")) return "bottom";
  }
  if (display.includes("grid")) {
    const alignItems = (cs.alignItems || "").toLowerCase();
    if (alignItems.includes("center")) return "middle";
    if (alignItems.includes("end")) return "bottom";
  }
  return "top";
}
function resolveHorizontalAlign(cs) {
  const textAlign = (cs.textAlign || "").toLowerCase();
  if (textAlign && !["start", "initial", "auto", "normal", "unset"].includes(textAlign)) {
    return textAlign;
  }
  const display = (cs.display || "").toLowerCase();
  if (display.includes("flex")) {
    const flexDirection = (cs.flexDirection || "row").toLowerCase();
    const crossAxisAlign = (cs.alignItems || "").toLowerCase();
    const mainAxisJustify = (cs.justifyContent || "").toLowerCase();
    const relevant = flexDirection.startsWith("column") ? crossAxisAlign : mainAxisJustify;
    if (relevant.includes("center")) return "center";
    if (relevant.includes("end") || relevant.includes("right")) return "right";
    if (relevant.includes("start") || relevant.includes("left")) return "left";
  }
  if (display.includes("grid")) {
    const justifyItems = (cs.justifyItems || "").toLowerCase();
    const justifyContent = (cs.justifyContent || "").toLowerCase();
    const relevant = justifyItems || justifyContent;
    if (relevant.includes("center")) return "center";
    if (relevant.includes("end") || relevant.includes("right")) return "right";
    if (relevant.includes("start") || relevant.includes("left")) return "left";
  }
  return null;
}
function buildTextElement(el, sectionRect, type, extra = {}) {
  const styles = getComputedStyles(el);
  const { renderContext = null, ...restExtra } = extra;
  const ctx = renderContext || deriveRenderContext(el);
  return {
    type,
    box: getBox(el, sectionRect, ctx),
    zIndex: getZIndex(el),
    alignment: resolveHorizontalAlign(styles) || "left",
    verticalAlign: resolveVerticalAlign(styles),
    rotationDeg: ctx.effectiveRotationDeg,
    rotation3dXDeg: ctx.effectiveRotation3dXDeg,
    rotation3dYDeg: ctx.effectiveRotation3dYDeg,
    rotation3dZDeg: ctx.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, sectionRect, ctx),
    lineHeightPx: parseFloat(styles.lineHeight) ? _scaleY(parseFloat(styles.lineHeight), ctx) : null,
    spaceBeforePx: _scaleY(parseFloat(styles.marginTop) || 0, ctx),
    spaceAfterPx: _scaleY(parseFloat(styles.marginBottom) || 0, ctx),
    ...restExtra
  };
}
function getZIndex(el) {
  const raw = window.getComputedStyle(el).zIndex;
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : 0;
}
function getBox(el, sectionRect, renderContext = null) {
  const rect = el.getBoundingClientRect();
  const cs = window.getComputedStyle(el);
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  const hasRotation = Math.abs(ctx.effectiveRotationDeg) > 0.01;
  const has3dRotation = Math.abs(ctx.effectiveRotation3dXDeg) > 0.01 || Math.abs(ctx.effectiveRotation3dYDeg) > 0.01 || Math.abs(ctx.effectiveRotation3dZDeg) > 0.01;
  if (hasRotation || has3dRotation) {
    const width = Math.max(
      (el.offsetWidth || parseFloat(cs.width) || rect.width) * ctx.effectiveScaleX,
      1
    );
    const height = Math.max(
      (el.offsetHeight || parseFloat(cs.height) || rect.height) * ctx.effectiveScaleY,
      1
    );
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    return {
      x: centerX - width / 2 - sectionRect.left,
      y: centerY - height / 2 - sectionRect.top,
      width,
      height
    };
  }
  return {
    x: rect.left - sectionRect.left,
    y: rect.top - sectionRect.top,
    width: rect.width,
    height: rect.height
  };
}
function getContentBox(el, sectionRect, renderContext = null) {
  const cs = window.getComputedStyle(el);
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  const box = getBox(el, sectionRect, ctx);
  const leftInset = _scaleX((parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0), ctx);
  const topInset = _scaleY((parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.paddingTop) || 0), ctx);
  const rightInset = _scaleX((parseFloat(cs.borderRightWidth) || 0) + (parseFloat(cs.paddingRight) || 0), ctx);
  const bottomInset = _scaleY((parseFloat(cs.borderBottomWidth) || 0) + (parseFloat(cs.paddingBottom) || 0), ctx);
  return {
    x: box.x + leftInset,
    y: box.y + topInset,
    width: Math.max(box.width - leftInset - rightInset, 1),
    height: Math.max(box.height - topInset - bottomInset, 1)
  };
}
function getProjectedCorners(el, sectionRect, renderContext = null) {
  const cs = window.getComputedStyle(el);
  const transform = cs.transform;
  if (!transform || transform === "none") return [];
  let matrix;
  try {
    matrix = new DOMMatrixReadOnly(transform);
  } catch {
    return [];
  }
  const rect = el.getBoundingClientRect();
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  const width = Math.max(
    (el.offsetWidth || parseFloat(cs.width) || rect.width) * ctx.effectiveScaleX,
    1
  );
  const height = Math.max(
    (el.offsetHeight || parseFloat(cs.height) || rect.height) * ctx.effectiveScaleY,
    1
  );
  const originParts = (cs.transformOrigin || "50% 50%").split(/\s+/).slice(0, 2).map((value, index) => {
    if (!value) return index === 0 ? width / 2 : height / 2;
    if (value.endsWith("%")) {
      const pct = parseFloat(value);
      if (!Number.isFinite(pct)) return index === 0 ? width / 2 : height / 2;
      return (index === 0 ? width : height) * pct / 100;
    }
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : index === 0 ? width / 2 : height / 2;
  });
  const originX = originParts[0];
  const originY = originParts[1];
  const relCorners = [
    { x: 0, y: 0 },
    { x: width, y: 0 },
    { x: width, y: height },
    { x: 0, y: height }
  ].map((corner) => {
    const point = matrix.transformPoint(
      new DOMPoint(corner.x - originX, corner.y - originY, 0, 1)
    );
    const w = point.w && Math.abs(point.w) > 1e-6 ? point.w : 1;
    return {
      x: point.x / w + originX,
      y: point.y / w + originY
    };
  });
  const minX = Math.min(...relCorners.map((corner) => corner.x));
  const minY = Math.min(...relCorners.map((corner) => corner.y));
  const pageOriginX = rect.left - minX;
  const pageOriginY = rect.top - minY;
  return relCorners.map((corner) => ({
    x: pageOriginX + corner.x - sectionRect.left,
    y: pageOriginY + corner.y - sectionRect.top
  }));
}
function normalizeInlineText(text) {
  return text.replace(/\s+/g, " ");
}

// runs.js
function _buildTextRun(text, styleEl, linkUrl = null, options = {}) {
  const {
    normalizeWhitespace = true,
    styleOverride = null,
    renderContext = null
  } = options;
  const normalizedText = normalizeWhitespace ? normalizeInlineText(text) : text;
  if (!normalizedText || normalizedText.length === 0) return null;
  return {
    text: normalizedText,
    style: styleOverride || styleToRunStyle(window.getComputedStyle(styleEl), styleEl, renderContext),
    linkUrl
  };
}
function extractInlineRuns(el, options = {}) {
  const {
    normalizeWhitespace = true,
    trimBoundary = true,
    includeRootPseudo = false,
    isStandaloneDecoratedFn = null,
    includeMathPlaceholders = false,
    renderContext = null
  } = options;
  const runs = [];
  const rootContext = renderContext || deriveRenderContext(el);
  function pushRun(text, styleEl, linkUrl = null, styleOverride = null, currentContext = rootContext) {
    const run = _buildTextRun(text, styleEl, linkUrl, {
      normalizeWhitespace,
      styleOverride,
      renderContext: currentContext
    });
    if (run) runs.push(run);
  }
  function pushRootPseudo(pseudo) {
    const pseudoRuns = extractPseudoRuns(el, pseudo, rootContext);
    for (const run of pseudoRuns) {
      pushRun(run.text, el, run.linkUrl, run.style, rootContext);
    }
  }
  function buildMathPlaceholderRun(node, styleEl, linkUrl, currentContext) {
    const placeholderText = _buildMathPlaceholderText(node, styleEl, currentContext);
    if (!placeholderText) return null;
    const style = _hiddenRunStyle(
      styleToRunStyle(
        window.getComputedStyle(styleEl),
        styleEl,
        currentContext
      )
    );
    return {
      text: placeholderText,
      style,
      linkUrl
    };
  }
  function visit(node, styleEl, linkUrl = null, currentContext = rootContext) {
    if (node.nodeType === Node.TEXT_NODE) {
      pushRun(node.textContent || "", styleEl, linkUrl, null, currentContext);
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    const nodeContext = node === el ? currentContext : deriveRenderContext(node, currentContext);
    if (node.tagName === "BR") {
      runs.push({
        text: "\n",
        style: styleToRunStyle(window.getComputedStyle(styleEl), styleEl, currentContext),
        linkUrl
      });
      return;
    }
    if (node.tagName === "IMG" && node.hasAttribute("data-marp-twemoji") && node.alt) {
      pushRun(node.alt, styleEl, linkUrl, null, currentContext);
      return;
    }
    if (includeMathPlaceholders && node.tagName === "MJX-CONTAINER") {
      const placeholderRun = buildMathPlaceholderRun(
        node,
        styleEl,
        linkUrl,
        currentContext
      );
      if (placeholderRun) runs.push(placeholderRun);
      return;
    }
    const decoration = extractDecoration(node, nodeContext);
    if (isStandaloneDecoratedFn && node !== el && isStandaloneDecoratedFn(node, decoration)) {
      const hiddenRuns = extractInlineRuns(node, {
        normalizeWhitespace,
        trimBoundary: false,
        includeRootPseudo: true,
        isStandaloneDecoratedFn: null,
        renderContext: nodeContext
      });
      for (const run of hiddenRuns) {
        runs.push({
          text: run.text,
          style: _hiddenRunStyle(run.style),
          linkUrl: run.linkUrl
        });
      }
      return;
    }
    let nextLinkUrl = linkUrl;
    if (node.tagName === "A" && node.href) {
      nextLinkUrl = node.href;
    }
    for (const child of node.childNodes) {
      visit(child, node, nextLinkUrl, nodeContext);
    }
  }
  if (includeRootPseudo) {
    pushRootPseudo("::before");
  }
  visit(el, el, null, rootContext);
  if (includeRootPseudo) {
    pushRootPseudo("::after");
  }
  return trimBoundary ? trimBoundaryWhitespace(runs) : runs;
}
function extractTextRuns(el, renderContext = null) {
  return extractInlineRuns(el, { renderContext });
}
function extractExactTextRuns(el, renderContext = null) {
  return extractInlineRuns(el, {
    normalizeWhitespace: false,
    trimBoundary: false,
    renderContext
  });
}
function extractTextRunsWithPseudo(el, renderContext = null, includeMathPlaceholders = false) {
  return extractInlineRuns(el, {
    includeRootPseudo: true,
    includeMathPlaceholders,
    renderContext
  });
}
function _hiddenRunStyle(style) {
  return {
    ...style,
    color: "rgba(0, 0, 0, 0)",
    backgroundColor: "transparent"
  };
}
function _buildMathPlaceholderText(node, styleEl, renderContext = null) {
  const box = node.getBoundingClientRect();
  const cs = window.getComputedStyle(styleEl);
  const renderCtx = renderContext || deriveRenderContext(styleEl);
  const fontSizePx = (parseFloat(cs.fontSize) || 16) * ((renderCtx.effectiveScaleX + renderCtx.effectiveScaleY) / 2);
  const canvas = _getMeasurementCanvas();
  const measureCtx = canvas.getContext("2d");
  if (!measureCtx) return "M";
  measureCtx.font = `${cs.fontStyle || "normal"} ${cs.fontWeight || "400"} ${fontSizePx}px ${cs.fontFamily || "Arial"}`;
  const charWidth = Math.max(measureCtx.measureText("M").width, fontSizePx * 0.5, 1);
  const count = Math.max(1, Math.ceil(box.width / charWidth));
  return "M".repeat(count);
}
var _measurementCanvas = null;
function _getMeasurementCanvas() {
  if (_measurementCanvas) return _measurementCanvas;
  _measurementCanvas = document.createElement("canvas");
  return _measurementCanvas;
}
function trimBoundaryWhitespace(runs) {
  const trimmed = runs.map((run) => ({ ...run })).filter((run) => run.text && run.text.length > 0);
  while (trimmed.length > 0 && trimmed[0].text.trim() === "") {
    trimmed.shift();
  }
  while (trimmed.length > 0 && trimmed[trimmed.length - 1].text.trim() === "") {
    trimmed.pop();
  }
  if (trimmed.length === 0) return [];
  trimmed[0].text = trimmed[0].text.replace(/^\s+/, "");
  trimmed[trimmed.length - 1].text = trimmed[trimmed.length - 1].text.replace(/\s+$/, "");
  for (let i = 1; i < trimmed.length; i++) {
    if (trimmed[i - 1].text.endsWith("\n")) {
      trimmed[i].text = trimmed[i].text.replace(/^\s+/, "");
    }
  }
  return trimmed.filter((run) => run.text.length > 0);
}

// paragraphs.js
function _buildParagraph(runs, alignment, metrics, extra = {}) {
  const { trimRuns = true, ...paragraphExtra } = extra;
  const normalizedRuns = trimRuns ? trimBoundaryWhitespace(runs) : runs.map((run) => ({ ...run })).filter((run) => run.text && run.text.length > 0);
  if (normalizedRuns.length === 0) return null;
  return {
    runs: normalizedRuns,
    alignment,
    lineHeightPx: metrics.lineHeightPx,
    spaceBeforePx: metrics.spaceBeforePx,
    spaceAfterPx: metrics.spaceAfterPx,
    listLevel: null,
    listOrdered: false,
    ...paragraphExtra
  };
}
function buildParagraphsFromRuns(runs, alignment, metrics, defaultStyle, extra = {}) {
  const paragraphs = [];
  let currentRuns = [];
  function pushParagraph() {
    const paragraph = _buildParagraph(
      currentRuns.length > 0 ? currentRuns : [{ text: " ", style: defaultStyle, linkUrl: null }],
      alignment,
      {
        lineHeightPx: metrics.lineHeightPx,
        spaceBeforePx: 0,
        spaceAfterPx: 0
      },
      extra
    );
    if (paragraph) paragraphs.push(paragraph);
    currentRuns = [];
  }
  for (const run of runs) {
    const parts = run.text.split("\n");
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].length > 0) {
        currentRuns.push({
          text: parts[i],
          style: run.style,
          linkUrl: run.linkUrl
        });
      }
      if (i < parts.length - 1) {
        pushParagraph();
      }
    }
  }
  if (currentRuns.length > 0 || paragraphs.length === 0) {
    pushParagraph();
  }
  const last = paragraphs[paragraphs.length - 1];
  if (last && last.runs.length === 1 && last.runs[0].text === " " && runs.length > 0 && runs[runs.length - 1].text.endsWith("\n")) {
    paragraphs.pop();
  }
  return paragraphs;
}
function extractParagraphsFromLines(text, style, alignment) {
  const lines = text.split(/\r?\n/).map((line) => line.trimEnd()).filter((line, index, all) => line.length > 0 || all.length === 1 && index === 0);
  return lines.map((line) => ({
    runs: [{ text: line || " ", style, linkUrl: null }],
    alignment,
    lineHeightPx: style.lineHeightPx || null,
    spaceBeforePx: 0,
    spaceAfterPx: 0,
    listLevel: null,
    listOrdered: false
  }));
}
function getParagraphMetrics(el, fallbackCs = null, renderContext = null) {
  const cs = fallbackCs || window.getComputedStyle(el);
  const ctx = renderContext || deriveRenderContext(el, null, cs);
  const lineHeight = parseFloat(cs.lineHeight);
  return {
    lineHeightPx: Number.isFinite(lineHeight) ? lineHeight * ctx.effectiveScaleY : null,
    spaceBeforePx: (parseFloat(cs.marginTop) || 0) * ctx.effectiveScaleY,
    spaceAfterPx: (parseFloat(cs.marginBottom) || 0) * ctx.effectiveScaleY
  };
}

// containers.js
function extractListItemContent(item, listEl, level, currentOrder, renderContext = null) {
  const itemCs = window.getComputedStyle(item);
  const itemContext = renderContext ? deriveRenderContext(item, renderContext, itemCs) : deriveRenderContext(item, null, itemCs);
  const metrics = getParagraphMetrics(item, itemCs, itemContext);
  const runs = [];
  const nestedLists = [];
  for (const node of item.childNodes) {
    if (node.nodeType === Node.TEXT_NODE) {
      const run = _buildTextRun(node.textContent || "", item, null, {
        renderContext: itemContext
      });
      if (run && run.text.trim()) runs.push(run);
      continue;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) continue;
    if (node.tagName === "UL" || node.tagName === "OL") {
      nestedLists.push(node);
      continue;
    }
    const childContext = deriveRenderContext(node, itemContext);
    runs.push(...extractInlineRuns(node, {
      includeRootPseudo: true,
      renderContext: childContext
    }));
  }
  const paragraph = _buildParagraph(
    [
      ...extractPseudoRuns(item, "::before", itemContext),
      ...runs,
      ...extractPseudoRuns(item, "::after", itemContext)
    ],
    resolveHorizontalAlign(itemCs) || resolveHorizontalAlign(window.getComputedStyle(listEl)) || "left",
    metrics,
    {
      listLevel: level,
      listOrdered: listEl.tagName === "OL",
      listStyleType: itemCs.listStyleType || window.getComputedStyle(listEl).listStyleType || null,
      orderNumber: currentOrder
    }
  );
  return { paragraph, nestedLists };
}
function extractParagraphsFromContainer(el, renderContext = null) {
  const cs = window.getComputedStyle(el);
  const containerContext = renderContext || deriveRenderContext(el, null, cs);
  const alignment = resolveHorizontalAlign(cs) || "left";
  const paragraphs = [];
  const containerMetrics = {
    lineHeightPx: getParagraphMetrics(el, cs, containerContext).lineHeightPx,
    spaceBeforePx: 0,
    spaceAfterPx: 0
  };
  function pushParagraph(runs2, metrics = containerMetrics, paragraphAlignment = alignment) {
    const paragraph2 = _buildParagraph(runs2, paragraphAlignment, metrics);
    if (paragraph2) paragraphs.push(paragraph2);
  }
  function pushParagraphFromNode(child) {
    const childContext = deriveRenderContext(child, containerContext);
    const childRuns = extractInlineRuns(child, {
      includeRootPseudo: true,
      renderContext: childContext
    });
    if (childRuns.length === 0) return;
    const metrics = getParagraphMetrics(child, null, childContext);
    pushParagraph(
      childRuns,
      metrics,
      resolveHorizontalAlign(window.getComputedStyle(child)) || alignment
    );
  }
  function buildTextRunFromNode(node, styleEl) {
    const run = _buildTextRun(node.textContent || "", styleEl, null, {
      renderContext: containerContext
    });
    if (!run || !run.text.trim()) return null;
    return run;
  }
  function isInlineLikeElement(child) {
    const display = window.getComputedStyle(child).display;
    return display.startsWith("inline") || display === "contents" || child.tagName === "BR";
  }
  function hasUnsupportedBlockDescendants(child) {
    const tag = child.tagName.toLowerCase();
    if (tag === "table" || tag === "img" || tag === "pre" || tag === "marp-pre" || tag === "blockquote") {
      return true;
    }
    return !!child.querySelector("table, img, pre, marp-pre, blockquote");
  }
  function pushListParagraphs(listEl, level, listContext) {
    const listItems = Array.from(listEl.children).filter((child) => child.tagName === "LI");
    let orderedIndex = listEl.tagName === "OL" ? listEl.start || 1 : 1;
    for (const item of listItems) {
      const currentOrder = listEl.tagName === "OL" ? parseInt(item.value, 10) || orderedIndex : null;
      if (listEl.tagName === "OL") {
        orderedIndex = currentOrder + 1;
      }
      const { paragraph: paragraph2, nestedLists } = extractListItemContent(
        item,
        listEl,
        level,
        currentOrder,
        listContext
      );
      if (paragraph2) paragraphs.push(paragraph2);
      for (const nested of nestedLists) {
        pushListParagraphs(
          nested,
          level + 1,
          deriveRenderContext(nested, listContext)
        );
      }
    }
  }
  let inlineRuns = [];
  function flushInlineParagraph() {
    if (inlineRuns.length === 0) return;
    pushParagraph(inlineRuns);
    inlineRuns = [];
  }
  for (const child of el.childNodes) {
    if (child.nodeType === Node.TEXT_NODE) {
      const run = buildTextRunFromNode(child, el);
      if (run) {
        inlineRuns.push(run);
      }
      continue;
    }
    if (child.nodeType !== Node.ELEMENT_NODE) continue;
    const tag = child.tagName.toLowerCase();
    const childContext = deriveRenderContext(child, containerContext);
    const childDecoration = extractDecoration(child, childContext);
    if (tag === "ul" || tag === "ol") {
      flushInlineParagraph();
      pushListParagraphs(child, 0, childContext);
    } else if (shouldExtractStandaloneDecoratedText(child, childDecoration)) {
      flushInlineParagraph();
    } else if (isInlineLikeElement(child)) {
      if (tag === "br") {
        flushInlineParagraph();
      } else {
        const inlineChildContext = deriveRenderContext(child, containerContext);
        inlineRuns.push(...extractInlineRuns(child, {
          includeRootPseudo: true,
          renderContext: inlineChildContext
        }));
      }
    } else if (!hasUnsupportedBlockDescendants(child)) {
      flushInlineParagraph();
      pushParagraphFromNode(child);
    }
  }
  flushInlineParagraph();
  if (paragraphs.length > 0) {
    const beforeRuns = extractPseudoRuns(el, "::before", containerContext);
    const afterRuns = extractPseudoRuns(el, "::after", containerContext);
    if (beforeRuns.length > 0) {
      paragraphs[0].runs = [...beforeRuns, ...paragraphs[0].runs];
    }
    if (afterRuns.length > 0) {
      paragraphs[paragraphs.length - 1].runs = [
        ...paragraphs[paragraphs.length - 1].runs,
        ...afterRuns
      ];
    }
    return paragraphs;
  }
  if (el.querySelector("blockquote")) {
    return [];
  }
  if (cs.whiteSpace.includes("pre") || el.querySelector("br")) {
    return extractParagraphsFromLines(
      el.innerText,
      styleToRunStyle(cs, el, containerContext),
      alignment
    );
  }
  const runs = extractTextRunsWithPseudo(el, containerContext);
  if (runs.length === 0) return [];
  const scaledMetrics = getParagraphMetrics(el, cs, containerContext);
  const paragraph = _buildParagraph(runs, alignment, scaledMetrics);
  return paragraph ? [paragraph] : [];
}

// classify.js
function shouldExtractStandaloneDecoratedText(el, decoration) {
  if (!hasMeaningfulDecoration(decoration)) return false;
  const tag = (el.localName || el.tagName).toLowerCase();
  if (tag === "code" || tag === "mark") return false;
  if ([
    "section",
    "blockquote",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "img",
    "pre",
    "marp-pre",
    "script",
    "style",
    "link",
    "meta",
    "header",
    "footer"
  ].includes(tag)) {
    return false;
  }
  const display = window.getComputedStyle(el).display;
  if (!display.startsWith("inline")) return false;
  if (el.querySelector("table, img, pre, marp-pre, blockquote, ul, ol")) return false;
  return extractParagraphsFromContainer(el).length > 0;
}
function extractTextRunsWithHiddenDecorated(el, renderContext = null, includeMathPlaceholders = false, extraStandaloneFn = null) {
  return extractInlineRuns(el, {
    renderContext,
    includeMathPlaceholders,
    isStandaloneDecoratedFn: (node, decoration) => shouldExtractStandaloneDecoratedText(node, decoration) || (extraStandaloneFn ? extraStandaloneFn(node) : false)
  });
}

// blocks.js
function isDecoratedBlockContainer(el) {
  const tag = (el.localName || el.tagName).toLowerCase();
  const cs = window.getComputedStyle(el);
  const parentListStyleType = el.parentElement ? (window.getComputedStyle(el.parentElement).listStyleType || "").toLowerCase() : "";
  const isPresentationalListNode = tag === "li" && (cs.display !== "list-item" || parentListStyleType === "none") || (tag === "ul" || tag === "ol") && (cs.listStyleType || "").toLowerCase() === "none";
  if ([
    "section",
    "blockquote",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "img",
    "pre",
    "marp-pre",
    "script",
    "style",
    "link",
    "meta",
    "header",
    "footer"
  ].includes(tag) && !isPresentationalListNode) {
    return false;
  }
  return !cs.display.startsWith("inline");
}
function shouldExtractDecoratedBlock(el, decoration, renderContext = null) {
  if (!hasMeaningfulDecoration(decoration)) return false;
  if (!isDecoratedBlockContainer(el)) return false;
  const paragraphs = extractParagraphsFromContainer(el, renderContext);
  return paragraphs.length > 0 || shouldDecomposeDecoratedBlock(el) || el.children.length === 0;
}
function shouldDecomposeDecoratedBlock(el) {
  const cs = window.getComputedStyle(el);
  const display = (cs.display || "").toLowerCase();
  const flexDirection = (cs.flexDirection || "row").toLowerCase();
  if ((display === "flex" || display === "inline-flex") && flexDirection !== "column" && flexDirection !== "column-reverse" && el.children.length > 1) {
    return true;
  }
  if ((display === "grid" || display === "inline-grid") && el.children.length > 1) {
    return true;
  }
  const hasUnsupportedDescendant = Array.from(el.querySelectorAll("*")).some(
    (node) => !!isUnsupported(node)
  );
  if (hasUnsupportedDescendant) return true;
  const hasDecoratedDescendant = Array.from(el.querySelectorAll("*")).some((node) => {
    const tag = (node.localName || node.tagName).toLowerCase();
    if (["table", "img", "pre", "marp-pre"].includes(tag)) return true;
    const decoration = extractDecoration(node, deriveRenderContext(node));
    return shouldExtractStandaloneDecoratedText(node, decoration) || isDecoratedBlockContainer(node) && hasMeaningfulDecoration(decoration) && (extractParagraphsFromContainer(node, deriveRenderContext(node)).length > 0 || node.children.length === 0);
  });
  if (hasDecoratedDescendant) return true;
  return Array.from(el.children).some(
    (child) => shouldExtractStandaloneDecoratedText(child, extractDecoration(child)) || isDecoratedBlockContainer(child) && hasMeaningfulDecoration(
      extractDecoration(child, deriveRenderContext(child))
    ) || !!isUnsupported(child) || ["table", "img", "pre", "marp-pre"].includes(
      (child.localName || child.tagName).toLowerCase()
    ) || !!child.querySelector("table, img, pre, marp-pre")
  );
}
function extractListItems(listEl, level, renderContext = null) {
  const items = [];
  const listContext = renderContext || deriveRenderContext(listEl);
  let orderedIndex = listEl.tagName === "OL" ? listEl.start || 1 : 1;
  for (const child of listEl.children) {
    if (child.tagName === "LI") {
      const currentOrder = listEl.tagName === "OL" ? parseInt(child.value, 10) || orderedIndex : null;
      if (listEl.tagName === "OL") {
        orderedIndex = currentOrder + 1;
      }
      const { paragraph, nestedLists } = extractListItemContent(
        child,
        listEl,
        level,
        currentOrder,
        listContext
      );
      if (paragraph) {
        items.push({
          runs: paragraph.runs,
          level: paragraph.listLevel,
          isOrdered: paragraph.listOrdered,
          orderNumber: paragraph.orderNumber,
          listStyleType: paragraph.listStyleType,
          alignment: paragraph.alignment,
          lineHeightPx: paragraph.lineHeightPx,
          spaceBeforePx: paragraph.spaceBeforePx,
          spaceAfterPx: paragraph.spaceAfterPx
        });
      }
      for (const nested of nestedLists) {
        const nestedListContext = deriveRenderContext(nested, listContext);
        items.push(...extractListItems(nested, level + 1, nestedListContext));
      }
    }
  }
  return items;
}
function _hasVisibleBackground(backgroundColor, backgroundGradient) {
  if (backgroundGradient && backgroundGradient !== "none") return true;
  const normalized = backgroundColor ? backgroundColor.replace(/\s+/g, "").toLowerCase() : "";
  return !!(normalized && normalized !== "transparent" && normalized !== "rgba(0,0,0,0)");
}
function _hasOverflowClipping(cs) {
  const overflowX = (cs.overflowX || cs.overflow || "visible").toLowerCase();
  const overflowY = (cs.overflowY || cs.overflow || "visible").toLowerCase();
  const clipped = /* @__PURE__ */ new Set(["hidden", "clip"]);
  return clipped.has(overflowX) || clipped.has(overflowY);
}
function _descendantNeedsClipping(el, rootContext) {
  const descendants = el.querySelectorAll("*");
  for (const child of descendants) {
    const childTag = (child.localName || child.tagName).toLowerCase();
    if (["script", "style", "link", "meta"].includes(childTag)) continue;
    const childContext = deriveSubtreeRenderContext(child, el, rootContext);
    const childDecoration = extractDecoration(child, childContext);
    if (_hasVisibleBackground(
      childDecoration.backgroundColor,
      childDecoration.backgroundGradient
    ) || hasMeaningfulDecoration(childDecoration) || ["img", "table", "svg", "canvas", "video", "iframe"].includes(childTag)) {
      return true;
    }
  }
  return false;
}
function _requiresOverflowClipFallback(el, cs) {
  const tag = (el.localName || el.tagName).toLowerCase();
  if (tag === "table") return false;
  if (!_hasOverflowClipping(cs)) return false;
  const radius = parseFloat(cs.borderTopLeftRadius) || 0;
  if (radius <= 0) return false;
  if (!el.children || el.children.length === 0) return false;
  const rootContext = deriveRenderContext(el, null, cs);
  return _descendantNeedsClipping(el, rootContext);
}
function _resolveTableCellBackground(td, tableEl, tableContext) {
  let current = td;
  while (current && tableEl.contains(current)) {
    const currentContext = deriveSubtreeRenderContext(current, tableEl, tableContext);
    const decoration = extractDecoration(current, currentContext);
    if (_hasVisibleBackground(decoration.backgroundColor, decoration.backgroundGradient)) {
      return decoration;
    }
    if (current === tableEl) {
      break;
    }
    current = current.parentElement;
  }
  return null;
}
function extractTable(tableEl, sectionRect, renderContext = null) {
  const rows = [];
  const tableContext = renderContext || deriveRenderContext(tableEl);
  const trs = tableEl.querySelectorAll("tr");
  for (const tr of trs) {
    const rowContext = deriveSubtreeRenderContext(tr, tableEl, tableContext);
    const cells = [];
    const tds = tr.querySelectorAll("th, td");
    for (const td of tds) {
      const cs = window.getComputedStyle(td);
      const cellContext = deriveRenderContext(td, rowContext, cs);
      const rect = td.getBoundingClientRect();
      const cellDecoration = extractDecoration(td, cellContext);
      const effectiveBackground = _resolveTableCellBackground(
        td,
        tableEl,
        tableContext
      );
      cells.push({
        text: td.textContent.trim(),
        runs: extractTextRuns(td, cellContext),
        isHeader: td.tagName === "TH",
        colspan: td.colSpan || 1,
        rowspan: td.rowSpan || 1,
        backgroundColor: effectiveBackground ? effectiveBackground.backgroundColor : "transparent",
        backgroundGradient: effectiveBackground ? effectiveBackground.backgroundGradient : null,
        padding: cellDecoration.padding,
        borderTop: cellDecoration.borderTop,
        borderRight: cellDecoration.borderRight,
        borderBottom: cellDecoration.borderBottom,
        borderLeft: cellDecoration.borderLeft,
        widthPx: rect.width
      });
    }
    rows.push({ cells });
  }
  return rows;
}
function _findSingleImageChild(el) {
  const images = el.querySelectorAll(":scope > img");
  if (images.length !== 1) return null;
  const directChildren = Array.from(el.children);
  if (directChildren.length !== 1) return null;
  const text = Array.from(el.childNodes).filter((node) => node.nodeType === Node.TEXT_NODE).map((node) => node.textContent || "").join("").trim();
  if (text.length > 0) return null;
  return images[0];
}
function isUnsupported(el) {
  const tag = (el.localName || el.tagName).toLowerCase();
  if (["svg", "math", "canvas"].includes(tag)) {
    return {
      reason: "Unsupported element: " + tag,
      tagName: tag,
      svgMarkup: tag === "svg" ? el.outerHTML : null
    };
  }
  const cs = window.getComputedStyle(el);
  const unsupportedStyleReason = getUnsupportedStyleReason(cs);
  if (unsupportedStyleReason) {
    return { reason: unsupportedStyleReason, tagName: tag };
  }
  if (cs.backgroundImage && cs.backgroundImage !== "none" && cs.backgroundImage.includes("gradient") && !cs.backgroundImage.includes("linear-gradient(")) {
    return { reason: "Unsupported gradient background", tagName: tag };
  }
  if (_requiresOverflowClipFallback(el, cs)) {
    return { reason: "Overflow clipping container", tagName: tag };
  }
  return null;
}

// handlers.js
function _normalizeCssColorValue(value) {
  return (value || "").replace(/\s+/g, "").toLowerCase();
}
function _stripContainerBackgroundFromParagraphs(paragraphs, decoration) {
  if (!decoration || !decoration.backgroundColor) return paragraphs;
  const containerBg = _normalizeCssColorValue(decoration.backgroundColor);
  if (!containerBg || containerBg === "transparent" || containerBg === "rgba(0,0,0,0)") {
    return paragraphs;
  }
  return paragraphs.map((paragraph) => ({
    ...paragraph,
    runs: paragraph.runs.map((run) => {
      const runBg = _normalizeCssColorValue(run.style?.backgroundColor);
      if (runBg !== containerBg) return run;
      return {
        ...run,
        style: {
          ...run.style,
          backgroundColor: null
        }
      };
    })
  }));
}
function _isInlineStandaloneUnsupported(el) {
  const tag = (el.localName || el.tagName).toLowerCase();
  if ([
    "section",
    "blockquote",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "img",
    "pre",
    "marp-pre",
    "script",
    "style",
    "link",
    "meta",
    "header",
    "footer"
  ].includes(tag)) {
    return false;
  }
  const display = window.getComputedStyle(el).display;
  if (!display.startsWith("inline")) return false;
  if (el.querySelector("table, img, pre, marp-pre, blockquote, ul, ol")) return false;
  return !!isUnsupported(el);
}
function _collectTopLevelInlineUnsupported(root) {
  const matches = Array.from(root.querySelectorAll("*")).filter(
    (node) => _isInlineStandaloneUnsupported(node)
  );
  return matches.filter(
    (node) => !matches.some(
      (other) => other !== node && other.contains(node)
    )
  );
}
function handleUnsupported(el, slideRect, slideData, unsup) {
  const renderContext = deriveRenderContext(el);
  slideData.elements.push({
    type: "unsupported",
    box: getBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    unsupportedInfo: unsup
  });
}
function handleMath(el, slideRect, slideData, tag) {
  const svg = el.querySelector("svg");
  const renderContext = deriveRenderContext(el);
  slideData.elements.push({
    type: "math",
    box: getBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext),
    unsupportedInfo: {
      reason: "Math expression (MathJax)",
      tagName: tag,
      svgMarkup: svg ? svg.outerHTML : null
    }
  });
}
function handleDecoratedStandalone(el, slideRect, slideData, decoration, renderContext) {
  const cs = window.getComputedStyle(el);
  const paragraphs = _stripContainerBackgroundFromParagraphs(
    extractParagraphsFromContainer(el, renderContext),
    decoration
  );
  slideData.elements.push({
    type: "decorated_block",
    box: getBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    paragraphs,
    decoration,
    verticalAlign: resolveVerticalAlign(cs),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext)
  });
}
function handleImageWithDecoration(el, slideRect, slideData, decoration, singleImageChild, renderContext) {
  const box = getBox(el, slideRect, renderContext);
  const imageContext = deriveRenderContext(singleImageChild, renderContext);
  if (box.width > 0 && box.height > 0) {
    slideData.elements.push({
      type: "image",
      box,
      zIndex: getZIndex(el),
      imageSrc: singleImageChild.src,
      imageNaturalWidthPx: singleImageChild.naturalWidth || null,
      imageNaturalHeightPx: singleImageChild.naturalHeight || null,
      objectFit: window.getComputedStyle(singleImageChild).objectFit || null,
      objectPosition: window.getComputedStyle(singleImageChild).objectPosition || null,
      imageOpacity: imageContext.effectiveOpacity,
      decoration,
      rotationDeg: renderContext.effectiveRotationDeg,
      rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
      rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
      rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
      projectedCorners: getProjectedCorners(el, slideRect, renderContext)
    });
  }
}
function handleDecoratedBlock(el, slideRect, slideData, decoration, renderContext) {
  const cs = window.getComputedStyle(el);
  const decomposeDecoratedBlock = shouldDecomposeDecoratedBlock(el);
  const paragraphs = decomposeDecoratedBlock ? [] : _stripContainerBackgroundFromParagraphs(
    extractParagraphsFromContainer(el, renderContext),
    decoration
  );
  slideData.elements.push({
    type: "decorated_block",
    box: getBox(el, slideRect, renderContext),
    contentBox: getContentBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    paragraphs,
    decoration,
    verticalAlign: resolveVerticalAlign(cs),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext)
  });
  if (decomposeDecoratedBlock) {
    for (const child of el.children) {
      processElement(child, slideRect, slideData, renderContext);
    }
  }
}
function handleHeading(el, slideRect, slideData, tag, renderContext) {
  const level = parseInt(tag[1]);
  slideData.elements.push(
    buildTextElement(el, slideRect, "heading", {
      headingLevel: level,
      runs: extractTextRuns(el, renderContext),
      renderContext
    })
  );
}
function handleParagraph(el, slideRect, slideData, renderContext) {
  if (el.querySelector("img") && !el.textContent.trim()) {
    for (const child of el.children) {
      processElement(child, slideRect, slideData, renderContext);
    }
    return;
  }
  const mathContainers = el.querySelectorAll("mjx-container");
  if (mathContainers.length > 0) {
    const nonMathText = Array.from(el.childNodes).filter((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()).length;
    if (nonMathText === 0 && el.children.length === mathContainers.length) {
      handleMath(el, slideRect, slideData, "mjx-container");
      return;
    }
  }
  const decoratedChildren = Array.from(el.children).filter(
    (child) => shouldExtractStandaloneDecoratedText(
      child,
      extractDecoration(child, deriveRenderContext(child, renderContext))
    )
  );
  const unsupportedInlineChildren = _collectTopLevelInlineUnsupported(el);
  slideData.elements.push(
    buildTextElement(el, slideRect, "paragraph", {
      runs: decoratedChildren.length > 0 ? extractTextRunsWithHiddenDecorated(
        el,
        renderContext,
        mathContainers.length > 0,
        _isInlineStandaloneUnsupported
      ) : unsupportedInlineChildren.length > 0 ? extractTextRunsWithHiddenDecorated(
        el,
        renderContext,
        mathContainers.length > 0,
        _isInlineStandaloneUnsupported
      ) : extractTextRunsWithPseudo(el, renderContext, mathContainers.length > 0),
      renderContext
    })
  );
  for (const mathEl of mathContainers) {
    handleMath(mathEl, slideRect, slideData, "mjx-container");
  }
  for (const child of decoratedChildren) {
    processElement(child, slideRect, slideData, renderContext);
  }
  for (const child of unsupportedInlineChildren) {
    processElement(child, slideRect, slideData, renderContext);
  }
}
function _isLeafTextBlock(el) {
  if (el.children.length > 0) return false;
  return !!el.textContent && el.textContent.trim().length > 0;
}
function _isPresentationalList(el) {
  const cs = window.getComputedStyle(el);
  const listStyleType = (cs.listStyleType || "").toLowerCase();
  if (listStyleType !== "none") return false;
  const items = Array.from(el.children).filter(
    (child) => (child.localName || child.tagName).toLowerCase() === "li"
  );
  const hasPseudoMarkers = items.some((item) => {
    const before = window.getComputedStyle(item, "::before").content;
    const after = window.getComputedStyle(item, "::after").content;
    return [before, after].some(
      (content) => content && content !== "none" && content !== "normal" && content !== '""' && content !== "''"
    );
  });
  return !hasPseudoMarkers;
}
function handleBlockquote(el, slideRect, slideData, decoration, renderContext) {
  const hasDecoration = hasMeaningfulDecoration(decoration);
  const cs = window.getComputedStyle(el);
  const paragraphs = _stripContainerBackgroundFromParagraphs(
    extractParagraphsFromContainer(el, renderContext),
    decoration
  );
  slideData.elements.push({
    type: "blockquote",
    box: getBox(el, slideRect, renderContext),
    contentBox: hasDecoration ? getContentBox(el, slideRect, renderContext) : null,
    zIndex: getZIndex(el),
    paragraphs,
    decoration: hasDecoration ? decoration : null,
    verticalAlign: resolveVerticalAlign(cs),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext)
  });
  for (const child of Array.from(el.children)) {
    if ((child.localName || child.tagName).toLowerCase() === "blockquote") {
      processElement(child, slideRect, slideData, renderContext);
    }
  }
}
function handleList(el, slideRect, slideData, tag, renderContext) {
  slideData.elements.push({
    type: tag === "ul" ? "unordered_list" : "ordered_list",
    box: getBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    listItems: extractListItems(el, 0, renderContext),
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
    projectedCorners: getProjectedCorners(el, slideRect, renderContext)
  });
}
function handleCodeBlock(el, slideRect, slideData, renderContext) {
  const codeEl = el.querySelector("code");
  if (codeEl) {
    const styles = getComputedStyles(el);
    const decoration = extractDecoration(el, renderContext);
    const hasDecoration = hasMeaningfulDecoration(decoration);
    const lang = Array.from(codeEl.classList).find((c) => c.startsWith("language-"));
    const alignment = window.getComputedStyle(codeEl).textAlign || styles.textAlign;
    const metrics = {
      lineHeightPx: parseFloat(styles.lineHeight) ? parseFloat(styles.lineHeight) * renderContext.effectiveScaleY : null,
      spaceBeforePx: (parseFloat(styles.marginTop) || 0) * renderContext.effectiveScaleY,
      spaceAfterPx: (parseFloat(styles.marginBottom) || 0) * renderContext.effectiveScaleY
    };
    slideData.elements.push({
      type: "code_block",
      box: getBox(el, slideRect, renderContext),
      contentBox: hasDecoration ? getContentBox(el, slideRect, renderContext) : null,
      zIndex: getZIndex(el),
      paragraphs: buildParagraphsFromRuns(
        extractExactTextRuns(codeEl, deriveRenderContext(codeEl, renderContext)),
        alignment,
        metrics,
        styleToRunStyle(window.getComputedStyle(codeEl), codeEl, deriveRenderContext(codeEl, renderContext)),
        { trimRuns: false }
      ),
      codeLanguage: lang ? lang.replace("language-", "") : null,
      decoration: hasDecoration ? decoration : null,
      codeBackground: applyOpacityToColor(styles.backgroundColor, renderContext.effectiveOpacity),
      verticalAlign: resolveVerticalAlign(styles),
      rotationDeg: renderContext.effectiveRotationDeg,
      rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
      rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
      rotation3dZDeg: renderContext.effectiveRotation3dZDeg,
      projectedCorners: getProjectedCorners(el, slideRect, renderContext)
    });
    return true;
  }
  return false;
}
function handleImage(el, slideRect, slideData, decoration, renderContext) {
  const box = getBox(el, slideRect, renderContext);
  if (box.width > 0 && box.height > 0) {
    slideData.elements.push({
      type: "image",
      box,
      zIndex: getZIndex(el),
      imageSrc: el.src,
      imageNaturalWidthPx: el.naturalWidth || null,
      imageNaturalHeightPx: el.naturalHeight || null,
      objectFit: window.getComputedStyle(el).objectFit || null,
      objectPosition: window.getComputedStyle(el).objectPosition || null,
      imageOpacity: renderContext.effectiveOpacity,
      decoration: hasMeaningfulDecoration(decoration) ? decoration : null,
      rotationDeg: renderContext.effectiveRotationDeg,
      rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
      rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
      rotation3dZDeg: renderContext.effectiveRotation3dZDeg
    });
  }
}
function handleTable(el, slideRect, slideData, renderContext, decoration) {
  slideData.elements.push({
    type: "table",
    box: getBox(el, slideRect, renderContext),
    zIndex: getZIndex(el),
    tableRows: extractTable(el, slideRect, renderContext),
    decoration: hasMeaningfulDecoration(decoration) ? decoration : null,
    rotationDeg: renderContext.effectiveRotationDeg,
    rotation3dXDeg: renderContext.effectiveRotation3dXDeg,
    rotation3dYDeg: renderContext.effectiveRotation3dYDeg,
    rotation3dZDeg: renderContext.effectiveRotation3dZDeg
  });
}
function processElement(el, slideRect, slideData, parentContext = null) {
  const tag = (el.localName || el.tagName).toLowerCase();
  if (["script", "style", "link", "meta", "header", "footer"].includes(tag)) return;
  const unsup = isUnsupported(el);
  if (unsup) {
    handleUnsupported(el, slideRect, slideData, unsup);
    return;
  }
  if (tag === "mjx-container" || el.classList && el.classList.contains("MathJax")) {
    handleMath(el, slideRect, slideData, tag);
    return;
  }
  const renderContext = deriveRenderContext(el, parentContext);
  slideData.elements.push(...extractBlockPseudoElements(el, slideRect, renderContext));
  const decoration = extractDecoration(el, renderContext);
  if (shouldExtractStandaloneDecoratedText(el, decoration)) {
    handleDecoratedStandalone(el, slideRect, slideData, decoration, renderContext);
    return;
  }
  const singleImageChild = _findSingleImageChild(el);
  if (singleImageChild && hasMeaningfulDecoration(decoration)) {
    handleImageWithDecoration(
      el,
      slideRect,
      slideData,
      decoration,
      singleImageChild,
      renderContext
    );
    return;
  }
  if (shouldExtractDecoratedBlock(el, decoration, renderContext)) {
    handleDecoratedBlock(el, slideRect, slideData, decoration, renderContext);
    return;
  }
  if (/^h[1-6]$/.test(tag)) {
    handleHeading(el, slideRect, slideData, tag, renderContext);
    return;
  }
  if (tag === "p" || tag === "figcaption") {
    handleParagraph(el, slideRect, slideData, renderContext);
    return;
  }
  if (_isLeafTextBlock(el)) {
    handleParagraph(el, slideRect, slideData, renderContext);
    return;
  }
  if (tag === "blockquote") {
    handleBlockquote(el, slideRect, slideData, decoration, renderContext);
    return;
  }
  if (tag === "ul" || tag === "ol") {
    if (_isPresentationalList(el)) {
      for (const child of el.children) {
        processElement(child, slideRect, slideData, renderContext);
      }
      return;
    }
    handleList(el, slideRect, slideData, tag, renderContext);
    return;
  }
  if (tag === "pre" || tag === "marp-pre") {
    if (handleCodeBlock(el, slideRect, slideData, renderContext)) {
      return;
    }
  }
  if (tag === "img") {
    handleImage(el, slideRect, slideData, decoration, renderContext);
    return;
  }
  if (tag === "table") {
    handleTable(el, slideRect, slideData, renderContext, decoration);
    return;
  }
  for (const child of el.children) {
    processElement(child, slideRect, slideData, renderContext);
  }
}

// main.js
function extractSlides() {
  const sections = document.querySelectorAll("section[id]");
  let slideSections;
  if (sections.length === 0) {
    const allSections = document.querySelectorAll("section");
    slideSections = Array.from(allSections).filter((s) => {
      return s.parentElement && (s.parentElement.tagName === "BODY" || s.parentElement.classList.contains("marpit") || s.parentElement.tagName === "DIV");
    });
    if (slideSections.length === 0) slideSections = Array.from(allSections);
  } else {
    slideSections = Array.from(sections);
  }
  const slides = [];
  let slideIndex = 0;
  for (let i = 0; i < slideSections.length; i++) {
    const section = slideSections[i];
    const advBg = section.getAttribute("data-marpit-advanced-background");
    if (advBg === "background" || advBg === "pseudo") {
      continue;
    }
    const sectionRect = section.getBoundingClientRect();
    const slideRoot = section.closest("svg") || section;
    const slideRect = slideRoot.getBoundingClientRect();
    const cs = window.getComputedStyle(section);
    const bgImages = extractBackgroundImages(slideRoot, advBg, section);
    const directives = extractDirectives(section);
    const slideData = {
      width: slideRect.width,
      height: slideRect.height,
      slideNumber: slideIndex++,
      background: {
        color: cs.backgroundColor,
        backgroundGradient: cs.backgroundImage && cs.backgroundImage.includes("gradient(") ? cs.backgroundImage : null,
        images: bgImages
      },
      directives,
      elements: []
    };
    const rootContext = createRenderContext();
    slideData.elements.push(...extractBlockPseudoElements(section, slideRect, rootContext));
    for (const child of section.children) {
      processElement(child, slideRect, slideData, rootContext);
    }
    slides.push(slideData);
  }
  return slides;
}

return extractSlides();
}