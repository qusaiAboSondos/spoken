const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "../.."); // repo root
const ICON = (name, color) => path.join(__dirname, "icons", `${name}_${color}.png`);
const REPORT_IMG = (name) => path.join(ROOT, "report", name);

// ---------- palette ----------
const DARK = "0B2545";      // deep navy - title/section backgrounds
const PRIMARY = "065A82";   // deep blue - headers, primary icon circles
const SECONDARY = "1C7293"; // teal - secondary accents
const LIGHT = "FFFFFF";
const CARD_BG = "EFF5F8";   // faint blue-gray card background
const TEXT_DARK = "12293F";
const TEXT_MUTED = "5B7385";
const GOOD = "2ECC71";      // bona fide / success
const BAD = "E63946";       // spoof / warning
const WARN = "F0A202";      // mid-severity

const FONT_HEAD = "Cambria";
const FONT_BODY = "Calibri";

function iconCircle(slide, { x, y, d, bg, icon, iconColor, padFrac = 0.28 }) {
  slide.addShape("ellipse", { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" } });
  const pad = d * padFrac;
  slide.addImage({ path: ICON(icon, iconColor), x: x + pad / 2, y: y + pad / 2, w: d - pad, h: d - pad });
}

function slideTitle(slide, text, opts = {}) {
  slide.addText(text, {
    x: 0.6, y: 0.4, w: 10.6, h: 0.8,
    fontFace: FONT_HEAD, fontSize: 28, bold: true, color: opts.color || TEXT_DARK,
    align: "left",
  });
}

function kicker(slide, text, color = SECONDARY) {
  slide.addText(text.toUpperCase(), {
    x: 0.6, y: 0.12, w: 8, h: 0.3,
    fontFace: FONT_BODY, fontSize: 12, bold: true, color, charSpacing: 2,
  });
}

function pageNum(slide, n) {
  slide.addText(String(n), {
    x: 12.6, y: 7.05, w: 0.5, h: 0.3, fontFace: FONT_BODY, fontSize: 10, color: TEXT_MUTED, align: "right",
  });
}

// ============================================================

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: FONT_HEAD, bodyFontFace: FONT_BODY };

// ---------- Slide 1: Title ----------
{
  const s = pres.addSlide();
  s.background = { color: DARK };

  // decorative "waveform" bars, bottom of slide
  const barCount = 40;
  const barAreaX = 0, barAreaW = 13.33, baseY = 6.9;
  for (let i = 0; i < barCount; i++) {
    const h = 0.15 + Math.abs(Math.sin(i * 0.7)) * 0.5 + Math.random() * 0.1;
    s.addShape("rect", {
      x: barAreaX + (barAreaW / barCount) * i + 0.04,
      y: baseY - h,
      w: (barAreaW / barCount) - 0.08,
      h,
      fill: { color: SECONDARY, transparency: 40 },
      line: { type: "none" },
    });
  }

  iconCircle(s, { x: 0.9, y: 0.75, d: 0.9, bg: SECONDARY, icon: "mic", iconColor: "FFFFFF" });

  s.addText("Detecting AI-Generated Speech", {
    x: 0.9, y: 2.0, w: 11.5, h: 1.1, fontFace: FONT_HEAD, fontSize: 40, bold: true, color: "FFFFFF",
  });
  s.addText("Using Classical Cepstral & Spectral Features", {
    x: 0.9, y: 2.95, w: 11.5, h: 0.6, fontFace: FONT_BODY, fontSize: 20, color: "CADCFC",
  });
  s.addText("Qusai Abu Sondos   ·   Laith Shadeh   ·   Mohammad Alabed", {
    x: 0.9, y: 4.7, w: 11.5, h: 0.4, fontFace: FONT_BODY, fontSize: 16, color: "FFFFFF",
  });
  s.addText("Spoken Language Processing — Summer 2026  |  Birzeit University", {
    x: 0.9, y: 5.15, w: 11.5, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: "8FB3D9",
  });
  s.addNotes(
    "Intro: we built a system to tell real human speech apart from AI-generated (TTS/voice-conversion) speech, using classical speech-processing features rather than a big neural network."
  );
}

// ---------- Slide 2: The Problem ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Motivation");
  slideTitle(s, "Why This Matters");

  const rows = [
    { icon: "robot", title: "Voice cloning is cheap now", body: "Modern TTS and voice-conversion systems can synthesize a convincing voice from a short reference clip." },
    { icon: "shield", title: "It defeats biometric security", body: "Automatic speaker verification (ASV) systems can be fooled by synthetic or converted speech — a direct spoofing threat." },
    { icon: "warning", title: "It fuels fraud & misinformation", body: "Impersonation calls, fake endorsements, and fabricated audio evidence all rely on the listener not being able to tell." },
  ];
  let y = 1.55;
  for (const r of rows) {
    iconCircle(s, { x: 0.7, y, d: 0.85, bg: PRIMARY, icon: r.icon, iconColor: "FFFFFF" });
    s.addText(r.title, { x: 1.8, y: y - 0.03, w: 10.5, h: 0.4, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: TEXT_DARK });
    s.addText(r.body, { x: 1.8, y: y + 0.38, w: 10.6, h: 0.6, fontFace: FONT_BODY, fontSize: 14, color: TEXT_MUTED });
    y += 1.65;
  }
  pageNum(s, 2);
  s.addNotes("Three reasons this matters: cheap voice cloning, ASV spoofing, and fraud/misinformation risk.");
}

// ---------- Slide 3: Objective ----------
{
  const s = pres.addSlide();
  s.background = { color: PRIMARY };
  iconCircle(s, { x: 0.9, y: 0.7, d: 0.85, bg: "FFFFFF", icon: "question", iconColor: PRIMARY });
  s.addText("Research Question", { x: 0.9, y: 1.75, w: 11.5, h: 0.5, fontFace: FONT_BODY, fontSize: 16, color: "CADCFC", bold: true });
  s.addText(
    "Can classical, hand-crafted speech features still reliably separate real from AI-generated speech — and does that hold up against synthesis systems the model has never seen?",
    { x: 0.9, y: 2.25, w: 11.5, h: 1.6, fontFace: FONT_HEAD, fontSize: 26, italic: true, color: "FFFFFF" }
  );

  const chips = ["Extract MFCC, LFCC & spectral features", "Train SVM and Random Forest classifiers", "Test on known AND unseen attack types"];
  let x = 0.9;
  const cw = 3.85;
  chips.forEach((c) => {
    s.addShape("roundRect", { x, y: 4.6, w: cw, h: 1.3, rectRadius: 0.08, fill: { color: "FFFFFF", transparency: 8 }, line: { type: "none" } });
    s.addText(c, { x: x + 0.25, y: 4.75, w: cw - 0.5, h: 1.0, fontFace: FONT_BODY, fontSize: 14, color: DARK, valign: "middle" });
    x += cw + 0.2;
  });
  pageNum(s, 3);
  s.addNotes("Our research question and three-part approach: features, classifiers, generalization test.");
}

// ---------- Slide 4: Dataset & Protocol ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Data");
  slideTitle(s, "Dataset & Experimental Protocol");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: SECONDARY, icon: "database", iconColor: "FFFFFF" });

  s.addText("ASVspoof2019 Logical Access (LA)  —  official speaker-disjoint train/dev/eval protocol (no data leakage)", {
    x: 0.6, y: 1.35, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 14, color: TEXT_MUTED,
  });

  const cards = [
    { label: "TRAIN", n: "3,000", sub: "1,500/class · 6 known attacks (A01–A06)", color: PRIMARY },
    { label: "DEV", n: "1,000", sub: "500/class · same 6 known attacks", color: SECONDARY },
    { label: "EVAL", n: "1,500", sub: "750/class · 11 UNSEEN attacks (A07–A19)", color: BAD },
  ];
  let x = 0.6;
  const cw = 3.95;
  cards.forEach((c, i) => {
    s.addShape("roundRect", { x, y: 2.1, w: cw, h: 2.9, rectRadius: 0.08, fill: { color: CARD_BG }, line: { type: "none" } });
    s.addText(c.label, { x, y: 2.35, w: cw, h: 0.35, align: "center", fontFace: FONT_BODY, fontSize: 13, bold: true, color: c.color });
    s.addText(c.n, { x, y: 2.7, w: cw, h: 1.0, align: "center", fontFace: FONT_HEAD, fontSize: 44, bold: true, color: TEXT_DARK });
    s.addText(c.sub, { x: x + 0.3, y: 3.85, w: cw - 0.6, h: 0.9, align: "center", fontFace: FONT_BODY, fontSize: 12.5, color: TEXT_MUTED });
    x += cw + 0.15;
  });

  s.addText(
    "Note: obtained via a Kaggle mirror — the official University of Edinburgh DataShare host was unreachable from our development environment.",
    { x: 0.6, y: 5.35, w: 12.1, h: 0.5, fontFace: FONT_BODY, fontSize: 11.5, italic: true, color: TEXT_MUTED }
  );
  pageNum(s, 4);
  s.addNotes("Train/dev share 6 known attacks; eval has 11 completely different, unseen attacks — that's our generalization test.");
}

// ---------- Slide 5: Methodology ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Methodology");
  slideTitle(s, "Feature Extraction & Classification Pipeline");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: SECONDARY, icon: "flask", iconColor: "FFFFFF" });

  s.addImage({ path: REPORT_IMG("pipeline_diagram.png"), x: 0.6, y: 1.35, w: 8.6, h: 3.93 });

  const facts = [
    ["MFCC", "20 coeffs + Δ+ΔΔ, Mel filterbank → 120-D"],
    ["LFCC", "Same, but custom LINEAR filterbank → 120-D"],
    ["Spectral/time", "Centroid, bandwidth, roll-off, flux, ZCR, energy → 12-D"],
    ["Classifiers", "SVM (RBF, calibrated) & Random Forest (300 trees)"],
  ];
  let y = 1.5;
  facts.forEach(([k, v]) => {
    s.addText(k, { x: 9.4, y, w: 3.3, h: 0.35, fontFace: FONT_BODY, fontSize: 13, bold: true, color: PRIMARY });
    s.addText(v, { x: 9.4, y: y + 0.32, w: 3.3, h: 0.7, fontFace: FONT_BODY, fontSize: 11.5, color: TEXT_MUTED });
    y += 1.15;
  });
  pageNum(s, 5);
  s.addNotes("16kHz mono, 25ms window/10ms hop. Three feature families extracted independently then concatenated before classification.");
}

// ---------- Slide 6: Results on known attacks ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Results — Known Attacks (dev)");
  slideTitle(s, "Feature Fusion Wins on Matched Data");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: PRIMARY, icon: "chart", iconColor: "FFFFFF" });

  const cats = ["MFCC+SVM", "LFCC+SVM", "MFCC+RF", "MFCC+Spec+SVM", "All+SVM"];
  const acc = [89.2, 98.8, 89.3, 90.9, 99.5];
  const eer = [8.7, 1.5, 11.3, 7.4, 0.3];

  s.addChart(
    "bar",
    [
      { name: "Accuracy (%)", labels: cats, values: acc },
    ],
    {
      x: 0.6, y: 1.4, w: 7.6, h: 4.6,
      barDir: "col",
      chartColors: [PRIMARY, SECONDARY, PRIMARY, SECONDARY, GOOD],
      valAxisMaxVal: 100, valAxisMinVal: 80,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: TEXT_DARK,
      dataLabelFormatCode: "0.0",
      showLegend: false, showTitle: true, title: "Accuracy on dev set (known attacks)", titleFontSize: 13,
      catAxisLabelFontSize: 10.5, valAxisLabelFontSize: 10, valAxisTitle: "Accuracy (%)",
      catGridLine: { style: "none" }, valGridLine: { color: "E0E6EA", size: 0.75 },
    }
  );

  // side callouts
  s.addShape("roundRect", { x: 8.5, y: 1.4, w: 4.25, h: 2.35, rectRadius: 0.08, fill: { color: CARD_BG }, line: { type: "none" } });
  s.addText("BEST: All features + SVM", { x: 8.75, y: 1.55, w: 3.8, h: 0.4, fontFace: FONT_BODY, fontSize: 13, bold: true, color: PRIMARY });
  s.addText("99.5%", { x: 8.7, y: 1.95, w: 2.2, h: 0.75, fontFace: FONT_HEAD, fontSize: 34, bold: true, color: TEXT_DARK, fit: "shrink" });
  s.addText("accuracy", { x: 8.75, y: 2.72, w: 2.0, h: 0.3, fontFace: FONT_BODY, fontSize: 11, color: TEXT_MUTED });
  s.addText("0.3%", { x: 10.8, y: 1.95, w: 1.8, h: 0.75, fontFace: FONT_HEAD, fontSize: 34, bold: true, color: GOOD, fit: "shrink" });
  s.addText("EER", { x: 10.85, y: 2.72, w: 1.8, h: 0.3, fontFace: FONT_BODY, fontSize: 11, color: TEXT_MUTED });

  s.addText(
    "LFCC alone already beats MFCC alone by a wide margin (98.8% vs. 89.2%) — its linear frequency resolution captures artifacts MFCC's Mel-scale compression smooths over.",
    { x: 8.5, y: 4.0, w: 4.25, h: 2.1, fontFace: FONT_BODY, fontSize: 12.5, color: TEXT_MUTED }
  );
  pageNum(s, 6);
  s.addNotes("On data matching the training distribution, combining all three feature families gives the best result: 99.5% accuracy, 0.3% EER.");
}

// ---------- Slide 7: Generalization ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Results — Generalization (eval)", BAD);
  slideTitle(s, "Accuracy Drops on Unseen Attacks — But Not Equally");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: BAD, icon: "shield", iconColor: "FFFFFF" });

  const cats = ["MFCC+SVM", "LFCC+SVM", "MFCC+RF", "MFCC+Spec+SVM", "All+SVM"];
  const dev = [89.2, 98.8, 89.3, 90.9, 99.5];
  const evalAcc = [89.3, 87.5, 86.1, 90.0, 91.1];

  s.addChart(
    "bar",
    [
      { name: "Dev (known attacks)", labels: cats, values: dev },
      { name: "Eval (unseen attacks)", labels: cats, values: evalAcc },
    ],
    {
      x: 0.6, y: 1.35, w: 12.1, h: 4.1,
      barDir: "col", barGapWidthPct: 40,
      chartColors: [SECONDARY, BAD],
      valAxisMaxVal: 100, valAxisMinVal: 75,
      showValue: true, dataLabelFontSize: 10, dataLabelPosition: "outEnd", dataLabelColor: TEXT_DARK,
      dataLabelFormatCode: "0.0",
      showLegend: true, legendPos: "b", legendFontSize: 11,
      catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, valAxisTitle: "Accuracy (%)",
      catGridLine: { style: "none" }, valGridLine: { color: "E0E6EA", size: 0.75 },
    }
  );

  s.addText(
    "LFCC alone collapses from 98.8% → 87.5% (spoof recall drops from 98.4% → 76.4%) — it partly memorizes known attack artifacts. The full feature combination stays the most robust: 91.1% accuracy / 6.5% EER on completely unseen attacks.",
    { x: 0.6, y: 5.6, w: 12.1, h: 1.1, fontFace: FONT_BODY, fontSize: 13.5, color: TEXT_DARK, align: "center" }
  );
  pageNum(s, 7);
  s.addNotes("The key generalization finding: LFCC looked best on dev but overfits; the fused feature set generalizes best.");
}

// ---------- Slide 8: Per-attack breakdown ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Results — Per-Attack Breakdown", WARN);
  slideTitle(s, "Failures Are Concentrated in Two Attacks");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: WARN, icon: "warning", iconColor: "FFFFFF" });

  const labels = ["A18", "A17", "A12", "A15", "A10", "A14", "bonafide", "A07", "A13", "A11", "A08", "A09", "A16", "A19"];
  const vals = [2.0, 11.6, 58.6, 89.1, 91.3, 96.2, 99.1, 100, 100, 100, 100, 100, 100, 100];
  const colors = vals.map((v) => (v < 70 ? BAD : v < 95 ? WARN : GOOD));

  s.addChart(
    "bar",
    [{ name: "Accuracy (%)", labels, values: vals }],
    {
      x: 0.5, y: 1.35, w: 12.3, h: 4.3,
      barDir: "col",
      chartColors: colors,
      valAxisMaxVal: 100,
      showValue: true, dataLabelFontSize: 9, dataLabelPosition: "outEnd", dataLabelColor: TEXT_DARK,
      dataLabelFormatCode: "0.0",
      showLegend: false,
      catAxisLabelFontSize: 10, catAxisLabelRotate: 30,
      valAxisLabelFontSize: 10, valAxisTitle: "Detection accuracy (%)",
      catGridLine: { style: "none" }, valGridLine: { color: "E0E6EA", size: 0.75 },
    }
  );

  s.addText(
    "Best model (All+SVM) on eval: 7 of 11 unseen attacks detected perfectly, bona fide speech recognized 99.1% of the time — but A17 & A18 (likely advanced voice-conversion systems) evade detection almost entirely.",
    { x: 0.6, y: 5.75, w: 12.1, h: 0.9, fontFace: FONT_BODY, fontSize: 13, color: TEXT_DARK, align: "center" }
  );
  pageNum(s, 8);
  s.addNotes("This is the clearest, most actionable finding: aggregate accuracy hides that 2-3 specific attacks account for almost all failures.");
}

// ---------- Slide 9: Key Findings ----------
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  iconCircle(s, { x: 0.7, y: 0.55, d: 0.8, bg: "FFFFFF", icon: "lightbulb", iconColor: DARK });
  s.addText("Key Findings", { x: 1.75, y: 0.65, w: 8, h: 0.6, fontFace: FONT_HEAD, fontSize: 30, bold: true, color: "FFFFFF" });

  const findings = [
    ["Feature fusion is the most robust choice", "Combining MFCC+LFCC+spectral consistently wins on both known and unseen attacks."],
    ["Single-feature accuracy can be misleading", "LFCC alone tops the dev leaderboard but overfits and drops hardest on unseen attacks."],
    ["Vulnerabilities are specific, not general", "Two unseen voice-conversion attacks (A17, A18) evade classical features almost completely."],
    ["False alarms stay low", "Bona fide speech is correctly recognized ~99% of the time across all experiments."],
  ];
  let y = 1.75;
  findings.forEach(([t, d]) => {
    s.addShape("roundRect", { x: 0.7, y, w: 11.9, h: 1.1, rectRadius: 0.08, fill: { color: "FFFFFF", transparency: 92 }, line: { type: "none" } });
    s.addText(t, { x: 1.0, y: y + 0.08, w: 11.3, h: 0.4, fontFace: FONT_BODY, fontSize: 15, bold: true, color: "FFFFFF" });
    s.addText(d, { x: 1.0, y: y + 0.5, w: 11.3, h: 0.5, fontFace: FONT_BODY, fontSize: 12.5, color: "AFC6DE" });
    y += 1.28;
  });
  pageNum(s, 9);
  s.addNotes("Four takeaways to remember: fusion is robust, single-feature wins can mislead, failures are concentrated, and false-alarm rate is low.");
}

// ---------- Slide 10: Live Demo ----------
{
  const s = pres.addSlide();
  s.background = { color: PRIMARY };
  iconCircle(s, { x: 5.7, y: 0.6, d: 1.0, bg: "FFFFFF", icon: "play", iconColor: PRIMARY });
  s.addText("Live Demonstration", { x: 0.6, y: 1.75, w: 12.1, h: 0.6, fontFace: FONT_HEAD, fontSize: 28, bold: true, color: "FFFFFF", align: "center" });

  const steps = [
    ["1", "Pick a held-out audio clip", "One real (bona fide) and one AI-generated (spoof) recording, unseen during training."],
    ["2", "Run the trained pipeline", "Extract MFCC+LFCC+spectral features → feed to the SVM classifier."],
    ["3", "Show the verdict", "Predicted label + confidence score for each clip, live."],
  ];
  let x = 0.9;
  const cw = 3.8;
  steps.forEach(([n, t, d]) => {
    s.addShape("roundRect", { x, y: 2.7, w: cw, h: 3.3, rectRadius: 0.1, fill: { color: "FFFFFF" }, line: { type: "none" } });
    s.addText(n, { x: x + 0.25, y: 2.9, w: 1, h: 0.8, fontFace: FONT_HEAD, fontSize: 36, bold: true, color: SECONDARY });
    s.addText(t, { x: x + 0.25, y: 3.7, w: cw - 0.5, h: 0.7, fontFace: FONT_BODY, fontSize: 15, bold: true, color: TEXT_DARK });
    s.addText(d, { x: x + 0.25, y: 4.35, w: cw - 0.5, h: 1.4, fontFace: FONT_BODY, fontSize: 12.5, color: TEXT_MUTED });
    x += cw + 0.25;
  });
  pageNum(s, 10);
  s.addNotes("Now switch to the terminal/notebook: run src.evaluate or a small predict script on two held-out clips and show the output live.");
}

// ---------- Slide 11: Conclusion ----------
{
  const s = pres.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "Conclusion & Future Work");
  slideTitle(s, "What We Achieved — and What's Next");
  iconCircle(s, { x: 11.5, y: 0.35, d: 0.7, bg: GOOD, icon: "check", iconColor: "FFFFFF" });

  s.addText("Achieved", { x: 0.6, y: 1.5, w: 5.8, h: 0.4, fontFace: FONT_BODY, fontSize: 15, bold: true, color: GOOD });
  const achieved = [
    "Full classical-feature pipeline: extraction → training → evaluation",
    "99.5% accuracy / 0.3% EER on known attacks",
    "91.1% accuracy / 6.5% EER on 11 unseen attacks",
    "Identified exactly which attacks classical features miss",
  ];
  s.addText(achieved.map((t) => ({ text: t, options: { bullet: { code: "2713" }, breakLine: true, color: TEXT_DARK, fontSize: 13.5 } })), {
    x: 0.6, y: 1.95, w: 5.9, h: 3.6, fontFace: FONT_BODY, valign: "top", paraSpaceAfter: 10,
  });

  s.addText("Future Work", { x: 6.85, y: 1.5, w: 5.8, h: 0.4, fontFace: FONT_BODY, fontSize: 15, bold: true, color: SECONDARY });
  const future = [
    "Cross-dataset test on ASVspoof2021 DF / WaveFake",
    "Add a CNN-on-spectrograms comparison",
    "Feature selection targeted at the A17/A18 failure cases",
    "Scale up from class-balanced subsets to the full corpus",
  ];
  s.addText(future.map((t) => ({ text: t, options: { bullet: { code: "2192" }, breakLine: true, color: TEXT_DARK, fontSize: 13.5 } })), {
    x: 6.85, y: 1.95, w: 5.9, h: 3.6, fontFace: FONT_BODY, valign: "top", paraSpaceAfter: 10,
  });
  pageNum(s, 11);
  s.addNotes("We met the project's objective; main gaps are a couple of specific attack types and untried deep-learning comparisons.");
}

// ---------- Slide 12: Thank you ----------
{
  const s = pres.addSlide();
  s.background = { color: DARK };
  iconCircle(s, { x: 5.92, y: 1.3, d: 1.5, bg: SECONDARY, icon: "users", iconColor: "FFFFFF" });
  s.addText("Thank You", { x: 0.6, y: 3.1, w: 12.1, h: 0.8, fontFace: FONT_HEAD, fontSize: 36, bold: true, color: "FFFFFF", align: "center" });
  s.addText("Questions?", { x: 0.6, y: 3.85, w: 12.1, h: 0.5, fontFace: FONT_BODY, fontSize: 18, color: "CADCFC", align: "center" });
  s.addText("Qusai Abu Sondos   ·   Laith Shadeh   ·   Mohammad Alabed", {
    x: 0.6, y: 4.9, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 14, color: "FFFFFF", align: "center",
  });
  s.addText("Code, data pipeline & full report: github.com/qusaiAboSondos/spoken", {
    x: 0.6, y: 5.3, w: 12.1, h: 0.4, fontFace: FONT_BODY, fontSize: 11, color: "8FB3D9", align: "center",
  });
  pageNum(s, 12);
  s.addNotes("Thanks and open the floor for questions. AI tool usage is fully disclosed in the written report.");
}

const outPath = path.join(ROOT, "report", "Spoken_Presentation.pptx");
pres.writeFile({ fileName: outPath }).then(() => console.log("Wrote", outPath));
