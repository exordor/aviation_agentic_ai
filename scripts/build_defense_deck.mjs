#!/usr/bin/env node

import fs from "node:fs";
import fsp from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = process.cwd();

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) {
      throw new Error(`Unexpected argument: ${key}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      args[key.slice(2)] = true;
      continue;
    }
    args[key.slice(2)] = value;
    index += 1;
  }
  return args;
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return {};
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function findPresentationBuilder() {
  if (process.env.PRESENTATIONS_SKILL_DIR) {
    const candidate = path.join(
      process.env.PRESENTATIONS_SKILL_DIR,
      "scripts",
      "build_artifact_deck.mjs",
    );
    if (fs.existsSync(candidate)) return candidate;
  }
  const base = path.join(
    os.homedir(),
    ".codex",
    "plugins",
    "cache",
    "openai-primary-runtime",
    "presentations",
  );
  if (!fs.existsSync(base)) {
    throw new Error(`Presentations runtime not found: ${base}`);
  }
  const versions = fs.readdirSync(base).sort().reverse();
  for (const version of versions) {
    const candidate = path.join(
      base,
      version,
      "skills",
      "presentations",
      "scripts",
      "build_artifact_deck.mjs",
    );
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error("Could not locate Presentations build_artifact_deck.mjs.");
}

function valueAt(object, keys, fallback = "TBD") {
  let current = object;
  for (const key of keys) {
    if (!current || typeof current !== "object" || !(key in current)) return fallback;
    current = current[key];
  }
  return current;
}

function chartDataForSlide(slideNumber, reports) {
  if (slideNumber === 6) {
    const ranking = reports.chunking.ranking || [];
    return ranking.map((item) => ({
      label: item.strategy,
      value: item.mrr_at_5,
      note: `Recall@5 ${item.recall_at_5}`,
    }));
  }
  if (slideNumber === 7) {
    const structure = reports.structureHybrid.aggregate || {};
    return ["vector", "graph", "hybrid"].map((mode) => ({
      label: mode,
      value: valueAt(structure, [mode, "retrieval", "recall_at_5"], 0),
      note: `KG ${valueAt(structure, [mode, "kg_evidence", "evidence_coverage"], 0)}`,
    }));
  }
  if (slideNumber === 8) {
    const experiments = reports.evidenceEval.experiments || {};
    return [
      {
        label: "fixed hybrid",
        value: valueAt(
          experiments,
          ["fixed_window", "aggregate", "hybrid", "answer_support_distribution", "supported"],
          0,
        ),
        note: "supported answers",
      },
      {
        label: "structure hybrid",
        value: valueAt(
          experiments,
          ["structure_aware", "aggregate", "hybrid", "answer_support_distribution", "supported"],
          0,
        ),
        note: "supported answers",
      },
    ];
  }
  return [];
}

function extraDataForSlide(slideNumber, reports) {
  if (slideNumber === 6) {
    const strategies = reports.chunking.strategies || {};
    return {
      fixedWindow: strategies.fixed_window?.aggregate?.chunking || {},
      structureAware: strategies.structure_aware?.aggregate?.chunking || {},
    };
  }
  if (slideNumber === 7) {
    const structure = reports.structureHybrid.aggregate || {};
    return {
      modes: ["vector", "graph", "hybrid"].map((mode) => ({
        mode,
        recall: valueAt(structure, [mode, "retrieval", "recall_at_5"], 0),
        kgCoverage: valueAt(structure, [mode, "kg_evidence", "evidence_coverage"], 0),
        mrr: valueAt(structure, [mode, "retrieval", "mrr_at_5"], 0),
      })),
    };
  }
  if (slideNumber === 8) {
    const experiments = reports.evidenceEval.experiments || {};
    return {
      fixed: valueAt(experiments, ["fixed_window", "aggregate", "hybrid"], {}),
      structure: valueAt(experiments, ["structure_aware", "aggregate", "hybrid"], {}),
    };
  }
  return {};
}

function loadReports() {
  return {
    chunking: readJson(path.join(ROOT, "reports", "stages", "chunking_comparison.json")),
    structureHybrid: readJson(path.join(ROOT, "reports", "stages", "hybrid_rag_structure_aware.json")),
    evidenceEval: readJson(path.join(ROOT, "reports", "stages", "evidence_level_evaluation.json")),
  };
}

function absoluteVisualPath(visual) {
  if (!visual || !String(visual).match(/\.(svg|png|jpg|jpeg|webp)$/i)) return undefined;
  const candidate = path.resolve(ROOT, visual);
  return fs.existsSync(candidate) ? candidate : undefined;
}

function safeName(value) {
  return String(value).replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase();
}

function displayMetricValue(value) {
  if (value === "structure_aware") return "struct";
  if (value === "fixed_window") return "fixed";
  if (value === "sentence_recursive") return "sent";
  if (value === "semantic_meta_like") return "semantic";
  return value;
}

function jsString(value) {
  return JSON.stringify(value);
}

async function writeTheme(slidesDir) {
  const theme = `
export const COLORS = {
  bg: "#ffffff",
  ink: "#12324a",
  muted: "#64748b",
  soft: "#e8eef5",
  panel: "#f8fafc",
  line: "#d8e2ee",
  accent: "#2e75b6",
  accent2: "#1f4e79",
  warn: "#f8d77a",
};

export function rect(slide, ctx, x, y, w, h, fill, line = ctx.line("#00000000", 0), radius = "rect") {
  return ctx.addShape(slide, { left: x, top: y, width: w, height: h, fill, line, geometry: radius });
}

export function text(slide, ctx, value, x, y, w, h, options = {}) {
  return ctx.addText(slide, {
    text: String(value ?? ""),
    left: x,
    top: y,
    width: w,
    height: h,
    fontSize: options.size ?? 24,
    color: options.color ?? COLORS.ink,
    bold: Boolean(options.bold),
    typeface: options.face ?? "Arial",
    align: options.align ?? "left",
    valign: options.valign ?? "top",
    fill: options.fill ?? "#00000000",
    line: options.line ?? ctx.line("#00000000", 0),
    insets: options.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
  });
}

export function wrap(value, maxChars = 72, maxLines = 3) {
  const words = String(value || "").replace(/\\s+/g, " ").trim().split(" ").filter(Boolean);
  const lines = [];
  let line = "";
  for (const word of words) {
    const next = line ? line + " " + word : word;
    if (next.length > maxChars && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  const clipped = lines.slice(0, maxLines);
  if (lines.length > maxLines) clipped[maxLines - 1] = clipped[maxLines - 1].replace(/[,. ]+$/, "") + "...";
  return clipped.join("\\n");
}

export function sourceLine(sources, max = 3) {
  const list = (sources || []).slice(0, max).join(" · ");
  return list || "local evidence pack";
}

export function title(slide, ctx, value) {
  text(slide, ctx, wrap(value, 72, 2), 58, 42, 1040, 70, { size: 28, bold: true, color: COLORS.ink });
  rect(slide, ctx, 58, 126, 1164, 2, COLORS.line);
}

export function footer(slide, ctx, slideNumber, sources) {
  text(slide, ctx, "Source: " + sourceLine(sources), 58, 674, 1020, 22, { size: 12, color: COLORS.muted });
  text(slide, ctx, String(slideNumber).padStart(2, "0"), 1168, 674, 54, 22, { size: 12, color: COLORS.muted, align: "right" });
}

export function bullets(slide, ctx, items, x, y, w) {
  items.slice(0, 4).forEach((item, index) => {
    const yy = y + index * 74;
    rect(slide, ctx, x, yy + 6, 8, 8, index === 0 ? COLORS.accent : COLORS.accent2);
    text(slide, ctx, wrap(item, 56, 3), x + 24, yy, w - 24, 60, { size: 17, color: COLORS.ink });
  });
}

export function proofPanel(slide, ctx, slideData) {
  rect(slide, ctx, 688, 178, 520, 358, COLORS.panel, ctx.line(COLORS.line, 2));
  text(slide, ctx, slideData.role.toUpperCase(), 720, 210, 430, 24, { size: 13, bold: true, color: COLORS.accent });
  text(slide, ctx, wrap(slideData.claim, 42, 6), 720, 260, 430, 180, { size: 25, bold: true, color: COLORS.ink });
  text(slide, ctx, wrap(slideData.speaker_note, 62, 3), 720, 452, 430, 54, { size: 14, color: COLORS.muted });
}

export function metricCards(slide, ctx, cards) {
  cards.slice(0, 4).forEach((card, index) => {
    const x = 82 + index * 286;
    rect(slide, ctx, x, 548, 240, 82, COLORS.panel, ctx.line(COLORS.line, 2));
    const value = String(card.value);
    text(slide, ctx, value, x + 20, 566, 88, 34, { size: value.length > 5 ? 19 : 26, bold: true, color: COLORS.accent2 });
    text(slide, ctx, card.label, x + 112, 566, 100, 22, { size: 13, bold: true, color: COLORS.ink });
    text(slide, ctx, card.note, x + 112, 594, 100, 20, { size: 11, color: COLORS.muted });
  });
}

export function barChart(slide, ctx, data) {
  rect(slide, ctx, 96, 188, 584, 350, COLORS.panel, ctx.line(COLORS.line, 2));
  const values = data.map((d) => Number(d.value) || 0);
  const max = Math.max(1, ...values);
  data.slice(0, 4).forEach((item, index) => {
    const y = 242 + index * 64;
    const width = Math.max(8, (Number(item.value) || 0) / max * 360);
    text(slide, ctx, item.label, 128, y - 2, 150, 24, { size: 14, bold: true, color: COLORS.ink });
    rect(slide, ctx, 296, y, 360, 18, "#e2e8f0");
    rect(slide, ctx, 296, y, width, 18, index === 0 ? COLORS.accent : COLORS.accent2);
    text(slide, ctx, String(item.value), 610, y - 4, 48, 24, { size: 13, color: COLORS.muted, align: "right" });
    text(slide, ctx, item.note, 296, y + 26, 220, 18, { size: 11, color: COLORS.muted });
  });
}

export function chip(slide, ctx, label, x, y, w, options = {}) {
  rect(slide, ctx, x, y, w, 34, options.fill ?? "#ffffffcc", ctx.line(options.line ?? COLORS.line, 1), "roundRect");
  text(slide, ctx, label, x + 12, y + 8, w - 24, 16, { size: options.size ?? 12, bold: Boolean(options.bold), color: options.color ?? COLORS.ink, align: "center" });
}

export function metricBar(slide, ctx, label, value, x, y, w, color = COLORS.accent) {
  text(slide, ctx, label, x, y, 120, 20, { size: 13, bold: true, color: COLORS.ink });
  rect(slide, ctx, x + 136, y + 2, w, 14, "#e2e8f0", ctx.line("#00000000", 0), "roundRect");
  rect(slide, ctx, x + 136, y + 2, Math.max(6, Number(value || 0) * w), 14, color, ctx.line("#00000000", 0), "roundRect");
  text(slide, ctx, String(value), x + 146 + w, y - 1, 48, 18, { size: 12, color: COLORS.muted });
}

export function statCard(slide, ctx, value, label, x, y, w = 142) {
  rect(slide, ctx, x, y, w, 92, "#ffffff", ctx.line(COLORS.line, 1), "roundRect");
  text(slide, ctx, String(value), x + 16, y + 12, w - 32, 26, { size: 22, bold: true, color: COLORS.accent2 });
  text(slide, ctx, label, x + 16, y + 42, w - 32, 32, { size: 11, color: COLORS.muted });
}

export async function visualOrPanel(slide, ctx, slideData) {
  if (slideData.visualPath) {
    await ctx.addImage(slide, {
      path: slideData.visualPath,
      left: 706,
      top: 182,
      width: 456,
      height: 304,
      fit: "contain",
      alt: slideData.visual,
    });
    text(slide, ctx, wrap(slideData.claim, 54, 3), 716, 512, 440, 64, { size: 17, bold: true, color: COLORS.ink });
    return;
  }
  proofPanel(slide, ctx, slideData);
}
`;
  await fsp.writeFile(path.join(slidesDir, "theme.mjs"), theme, "utf8");
}

function slideModule(slide, metricsCards) {
  const exportName = `slide${String(slide.slide_number).padStart(2, "0")}`;
  return `
import { COLORS, barChart, bullets, chip, footer, metricBar, metricCards, rect, statCard, text, title, visualOrPanel, wrap } from "./theme.mjs";

const slideData = ${jsString(slide)};
const metricData = ${jsString(metricsCards)};

export async function ${exportName}(presentation, ctx) {
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, 1280, 720, COLORS.bg);
  if (slideData.slide_number === 1) {
    rect(slide, ctx, 0, 0, 1280, 720, "#f8fafc");
    rect(slide, ctx, 58, 58, 4, 76, COLORS.accent2);
    text(slide, ctx, "Aviation Agentic AI", 84, 58, 420, 26, { size: 15, bold: true, color: COLORS.accent2 });
    text(slide, ctx, wrap(slideData.title, 32, 4), 84, 142, 520, 250, { size: 39, bold: true, color: COLORS.ink });
    text(slide, ctx, wrap(slideData.claim, 58, 3), 84, 430, 500, 88, { size: 21, color: COLORS.muted });
    if (slideData.visualPath) {
      await ctx.addImage(slide, { path: slideData.visualPath, left: 666, top: 118, width: 520, height: 346, fit: "contain", alt: "AI-generated project cover visual" });
    }
    metricCards(slide, ctx, metricData);
    footer(slide, ctx, slideData.slide_number, slideData.evidence_sources);
    return slide;
  }
  title(slide, ctx, slideData.title);
  if (slideData.slide_number === 3) {
    if (slideData.visualPath) {
      await ctx.addImage(slide, { path: slideData.visualPath, left: 74, top: 150, width: 1132, height: 372, fit: "contain", alt: "AI-generated pipeline hero visual" });
    }
    ["PDF", "Chunks", "Ontology", "KG", "Chroma", "Grounded answer"].forEach((label, index) => {
      chip(slide, ctx, label, 112 + index * 174, 548, 132, { bold: index === 5, line: index === 5 ? COLORS.accent : COLORS.line });
    });
    text(slide, ctx, wrap(slideData.claim, 84, 2), 154, 604, 972, 42, { size: 18, color: COLORS.ink, align: "center" });
    footer(slide, ctx, slideData.slide_number, slideData.evidence_sources);
    return slide;
  }
  if (slideData.slide_number === 4) {
    const modules = [
      ["Core", "Document · SourceChunk · Evidence"],
      ["Atmosphere", "Air · Pressure · Density · Temperature"],
      ["Aircraft/Airfoil", "Aircraft · Wing · AirfoilSurface"],
      ["Aerodynamics", "Lift · Drag · AOA · Vortex"],
      ["Physics/Relations", "Newton · Bernoulli · Cause/Outcome"],
    ];
    modules.forEach((item, index) => {
      const x = 88 + (index % 3) * 372;
      const y = index < 3 ? 186 : 382;
      rect(slide, ctx, x, y, 306, 118, "#ffffff", ctx.line(index === 0 ? COLORS.accent : COLORS.line, 2), "roundRect");
      text(slide, ctx, item[0], x + 22, y + 24, 250, 24, { size: 20, bold: true, color: COLORS.accent2 });
      text(slide, ctx, item[1], x + 22, y + 62, 250, 34, { size: 13, color: COLORS.muted });
    });
    rect(slide, ctx, 458, 536, 364, 98, "#f8fafc", ctx.line(COLORS.line, 1), "roundRect");
    text(slide, ctx, "Extraction relations", 484, 552, 312, 18, { size: 13, bold: true, color: COLORS.accent });
    text(slide, ctx, "affects · causes · appliesTo · supportedByEvidence", 484, 578, 312, 36, { size: 14, color: COLORS.ink, align: "center" });
    footer(slide, ctx, slideData.slide_number, slideData.evidence_sources);
    return slide;
  }
  if (slideData.slide_number === 5) {
    rect(slide, ctx, 82, 174, 474, 396, "#ffffff", ctx.line(COLORS.line, 2), "roundRect");
    text(slide, ctx, "Validated triple example", 112, 204, 390, 22, { size: 14, bold: true, color: COLORS.accent });
    text(slide, ctx, "AngleOfAttack", 112, 260, 150, 26, { size: 20, bold: true, color: COLORS.ink });
    text(slide, ctx, "affects", 292, 263, 76, 20, { size: 15, color: COLORS.accent, align: "center" });
    text(slide, ctx, "Lift", 398, 260, 92, 26, { size: 20, bold: true, color: COLORS.ink });
    rect(slide, ctx, 112, 326, 382, 92, "#f8fafc", ctx.line(COLORS.line, 1), "roundRect");
    text(slide, ctx, "Every triple must keep chunk_id, page, evidence text, and ontology-supported property.", 134, 350, 340, 44, { size: 16, color: COLORS.ink });
    statCard(slide, ctx, "172", "fixed-window triples", 112, 452);
    statCard(slide, ctx, "448", "structure-aware triples", 282, 452);
    if (slideData.visualPath) {
      await ctx.addImage(slide, { path: slideData.visualPath, left: 616, top: 172, width: 560, height: 374, fit: "contain", alt: "AI-generated KG evidence visual" });
    }
    footer(slide, ctx, slideData.slide_number, slideData.evidence_sources);
    return slide;
  }
  if (slideData.chartData && slideData.chartData.length) {
    barChart(slide, ctx, slideData.chartData);
    if (slideData.slide_number === 6) {
      statCard(slide, ctx, slideData.extraData?.fixedWindow?.chunk_count ?? "35", "fixed chunks", 744, 218);
      statCard(slide, ctx, slideData.extraData?.structureAware?.chunk_count ?? "267", "structure chunks", 914, 218);
      statCard(slide, ctx, slideData.extraData?.structureAware?.boundary_preservation_rate ?? "1.0", "boundary rate", 1084, 218);
      text(slide, ctx, "Why it wins", 744, 334, 240, 22, { size: 15, bold: true, color: COLORS.accent });
      bullets(slide, ctx, [
        "Preserves handbook headings, lists, and page-local sections.",
        "Ties source-page Recall@5 while placing evidence higher.",
        "Higher chunk count is a cost tradeoff, not a model win by itself.",
      ], 744, 372, 424);
    } else if (slideData.slide_number === 7) {
      rect(slide, ctx, 724, 198, 430, 390, "#ffffff", ctx.line(COLORS.line, 2), "roundRect");
      text(slide, ctx, "Layered interpretation", 754, 224, 330, 22, { size: 15, bold: true, color: COLORS.accent });
      (slideData.extraData?.modes || []).forEach((row, index) => {
        const y = 286 + index * 76;
        text(slide, ctx, row.mode, 754, y - 24, 76, 20, { size: 14, bold: true, color: COLORS.ink });
        metricBar(slide, ctx, "page Recall", row.recall, 754, y, 170, COLORS.accent);
        metricBar(slide, ctx, "KG coverage", row.kgCoverage, 754, y + 30, 170, COLORS.accent2);
      });
      text(slide, ctx, wrap("GraphRAG value is structured evidence coverage; page Recall is only one retrieval layer.", 54, 3), 754, 504, 340, 56, { size: 14, color: COLORS.muted });
    } else if (slideData.slide_number === 8) {
      statCard(slide, ctx, slideData.extraData?.fixed?.answer_support_distribution?.supported ?? "7", "fixed supported / 10", 744, 222);
      statCard(slide, ctx, slideData.extraData?.structure?.answer_support_distribution?.supported ?? "9", "structure supported / 10", 914, 222);
      statCard(slide, ctx, slideData.extraData?.structure?.citation_validity ?? "1.0", "citation validity", 1084, 222);
      text(slide, ctx, wrap(slideData.claim, 58, 3), 744, 340, 424, 80, { size: 22, bold: true, color: COLORS.ink });
      text(slide, ctx, "Denominator: 10 boundary CQs; support labels are evidence-level, not a single mixed score.", 744, 454, 424, 52, { size: 14, color: COLORS.muted });
    } else {
      bullets(slide, ctx, [slideData.claim, slideData.speaker_note], 724, 210, 420);
    }
  } else if (slideData.slide_number === 9) {
    if (slideData.visualPath) {
      await ctx.addImage(slide, { path: slideData.visualPath, left: 70, top: 156, width: 780, height: 486, fit: "contain", alt: "AI-generated web demo mockup" });
    }
    text(slide, ctx, "Demo explanation surface", 892, 200, 250, 24, { size: 16, bold: true, color: COLORS.accent });
    bullets(slide, ctx, [
      "Question list selects the CQ and default structure-aware strategy.",
      "Answer panel stays grounded in retrieved evidence.",
      "Right rail exposes chunks, triples, and question-scoped graph evidence.",
      "Live query remains disabled by default for reproducibility.",
    ], 892, 246, 292);
  } else if (slideData.slide_number === 10) {
    const items = [
      ["Evaluation", "Coarse source_page labels must become chunk/span evidence labels."],
      ["Data scope", "PHAK Chapter 4 is stable; procedure/emergency sources need shared metadata schema."],
      ["KG extraction", "Structure-aware chunks improve evidence, but extraction cost rises with chunk count."],
      ["Safety", "Advisory boundary must stay visible in report, prompt, and demo UI."],
    ];
    items.forEach((item, index) => {
      const x = 82 + index * 292;
      rect(slide, ctx, x, 190, 244, 324, "#ffffff", ctx.line(COLORS.line, 2), "roundRect");
      text(slide, ctx, item[0], x + 24, 222, 196, 24, { size: 18, bold: true, color: COLORS.accent2 });
      text(slide, ctx, wrap(item[1], 28, 7), x + 24, 278, 196, 158, { size: 16, color: COLORS.ink });
    });
    text(slide, ctx, wrap(slideData.claim, 78, 2), 124, 548, 1032, 44, { size: 19, color: COLORS.muted, align: "center" });
  } else if (slideData.slide_number === 11) {
    rect(slide, ctx, 142, 186, 996, 284, "#f8fafc", ctx.line(COLORS.accent, 2), "roundRect");
    text(slide, ctx, wrap(slideData.claim, 62, 4), 198, 246, 884, 132, { size: 32, bold: true, color: COLORS.ink, align: "center", valign: "middle" });
    text(slide, ctx, "This boundary is part of the system design, not presentation fine print.", 292, 506, 696, 26, { size: 18, color: COLORS.muted, align: "center" });
  } else if (slideData.slide_number === 12) {
    const checks = ["Ontology purpose", "KG deliverable", "Chunking tradeoff", "GraphRAG evidence value", "Reproducible commands"];
    checks.forEach((label, index) => {
      const y = 184 + index * 72;
      rect(slide, ctx, 182, y, 34, 34, COLORS.accent, ctx.line("#00000000", 0), "roundRect");
      text(slide, ctx, "✓", 188, y + 2, 24, 28, { size: 18, bold: true, color: "#ffffff", align: "center" });
      text(slide, ctx, label, 242, y + 2, 360, 28, { size: 23, bold: true, color: COLORS.ink });
      text(slide, ctx, "linked to source artifacts and metrics", 664, y + 7, 360, 22, { size: 15, color: COLORS.muted });
    });
    text(slide, ctx, wrap(slideData.claim, 76, 2), 178, 574, 924, 48, { size: 20, color: COLORS.accent2, align: "center" });
  } else if (slideData.slide_number === 13) {
    const refs = [
      "curated ontology TTL",
      "KG JSONL/TTL",
      "chunking comparison",
      "hybrid RAG reports",
      "evidence-level evaluation",
      "web demo readiness",
      "project report",
      "defense notes",
    ];
    refs.forEach((label, index) => {
      const x = 104 + (index % 4) * 276;
      const y = 190 + Math.floor(index / 4) * 154;
      rect(slide, ctx, x, y, 228, 118, "#ffffff", ctx.line(COLORS.line, 2), "roundRect");
      text(slide, ctx, label, x + 20, y + 20, 188, 38, { size: 15, bold: true, color: COLORS.ink });
      text(slide, ctx, "See stage index and final sources JSON", x + 20, y + 66, 188, 34, { size: 12, color: COLORS.muted });
    });
  } else {
    bullets(slide, ctx, [slideData.claim, slideData.speaker_note], 82, 208, 520);
    await visualOrPanel(slide, ctx, slideData);
  }
  footer(slide, ctx, slideData.slide_number, slideData.evidence_sources);
  return slide;
}
`;
}

async function writeSlides(outline, workspace, reports) {
  const slidesDir = path.join(workspace, "slides");
  ensureDir(slidesDir);
  await writeTheme(slidesDir);
  const metricsCards = [
    { value: displayMetricValue(outline.metrics_snapshot?.chunking?.best_strategy || "TBD"), label: "chunking", note: "best strategy" },
    { value: outline.metrics_snapshot?.hybrid_rag?.structure_hybrid_recall_at_5 ?? "TBD", label: "hybrid", note: "Recall@5" },
    { value: outline.metrics_snapshot?.hybrid_rag?.structure_hybrid_kg_coverage ?? "TBD", label: "KG", note: "coverage" },
    { value: outline.metrics_snapshot?.hybrid_rag?.structure_supported_answers ?? "TBD", label: "answers", note: "supported" },
  ];
  for (const slide of outline.slides) {
    const visualPath = absoluteVisualPath(slide.visual);
    const enriched = {
      ...slide,
      visualPath,
      chartData: chartDataForSlide(slide.slide_number, reports),
      extraData: extraDataForSlide(slide.slide_number, reports),
    };
    const fileName = `slide-${String(slide.slide_number).padStart(2, "0")}.mjs`;
    await fsp.writeFile(
      path.join(slidesDir, fileName),
      slideModule(enriched, metricsCards),
      "utf8",
    );
  }
  return slidesDir;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const outlinePath = path.resolve(args.outline || "reports/final/aviation_graphrag_defense_deck_sources.json");
  const outputPath = path.resolve(args.out || "reports/final/aviation_graphrag_defense_deck.pptx");
  const workspace = path.resolve(
    args.workspace || path.join("outputs", "manual-defense-deck", "presentations", "aviation-graphrag-defense"),
  );
  const outline = readJson(outlinePath);
  if (!Array.isArray(outline.slides) || outline.slides.length === 0) {
    throw new Error(`Deck outline has no slides: ${outlinePath}`);
  }
  const reports = loadReports();
  ensureDir(workspace);
  const slidesDir = await writeSlides(outline, workspace, reports);
  const builder = findPresentationBuilder();
  const previewDir = path.join(workspace, "preview");
  const layoutDir = path.join(workspace, "layout");
  const qaDir = path.join(workspace, "qa");
  ensureDir(qaDir);
  const result = spawnSync(
    "node",
    [
      builder,
      "--slides-dir",
      slidesDir,
      "--out",
      outputPath,
      "--preview-dir",
      previewDir,
      "--layout-dir",
      layoutDir,
      "--contact-sheet",
      path.join(qaDir, "contact-sheet.png"),
      "--manifest",
      path.join(qaDir, "artifact-build-manifest.json"),
      "--slide-count",
      String(outline.slides.length),
      "--scale",
      "1",
    ],
    {
      cwd: ROOT,
      encoding: "utf8",
      env: { ...process.env, PYTHON: process.env.PYTHON || "python3" },
    },
  );
  if (result.status !== 0) {
    throw new Error([result.stdout, result.stderr].filter(Boolean).join("\\n"));
  }
  const manifest = JSON.parse(result.stdout);
  console.log(JSON.stringify({
    output: outputPath,
    workspace,
    slideCount: manifest.slideCount,
    contactSheet: manifest.contactSheet,
    previewDir: manifest.previewDir,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
