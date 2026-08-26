import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const BUILD_DIR = "C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build";
const OUTPUT_DIR = BUILD_DIR + "/output";
const FINAL_PPTX = "C:/Users/CJSCOPE/Desktop/PythonSDD/Day2_obstacles_and_levels.pptx";
const W = 1280;
const H = 720;
const FONT = "Arial";

const C = {
  white: "#FFFFFF",
  ink: "#111111",
  muted: "#5D6470",
  panel: "#F1F2F4",
  line: "#B8BCC4",
  blue: "#3D8DFF",
  blueLight: "#D9F0FB",
  orange: "#F28C28",
  brick: "#111111",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addShape(slide, geometry, position, fill, line, name, extra) {
  return slide.shapes.add({
    geometry,
    name,
    position,
    fill,
    line,
    ...(extra || {}),
  });
}

function addText(slide, value, position, style, name) {
  const shape = addShape(
    slide,
    "textbox",
    position,
    "none",
    { style: "solid", fill: "none", width: 0 },
    name || "text",
  );
  shape.text = value;
  shape.text.style = {
    color: C.ink,
    fontSize: 18,
    alignment: "left",
    verticalAlignment: "top",
    ...(style || {}),
  };
  return shape;
}

function addRule(slide, left, top, width, color, name) {
  return addShape(
    slide,
    "line",
    { left, top, width, height: 0 },
    "none",
    { style: "solid", fill: color || C.line, width: 2 },
    name || "rule",
  );
}

function addBrickWall(slide, left, top, columns, rows, brickWidth, brickHeight, gap, name) {
  const colCount = columns || 6;
  const rowCount = rows || 3;
  const brickW = brickWidth || 52;
  const brickH = brickHeight || 16;
  const brickGap = gap || 5;
  const wallName = name || "wall";
  for (let row = 0; row < rowCount; row += 1) {
    const offset = row % 2 === 0 ? 0 : (brickW + brickGap) / 2;
    for (let column = 0; column < colCount; column += 1) {
      const x = left + offset + column * (brickW + brickGap);
      addShape(
        slide,
        "rect",
        { left: x, top: top + row * (brickH + brickGap), width: brickW, height: brickH },
        C.brick,
        { style: "solid", fill: C.white, width: 1 },
        wallName + "-brick-" + row + "-" + column,
      );
    }
  }
}

function addBall(slide, left, top, diameter, fill, name) {
  return addShape(
    slide,
    "ellipse",
    { left, top, width: diameter, height: diameter },
    fill,
    { style: "solid", fill, width: 1 },
    name,
  );
}

function addGameBoard(slide, left, top, width, height, obstacleCount, name, options) {
  addShape(
    slide,
    "rect",
    { left, top, width, height },
    (options && options.fill) || C.panel,
    { style: "solid", fill: (options && options.line) || C.line, width: 2 },
    name + "-board",
  );

  const brickWidth = Math.max(24, Math.min(54, (width - 56) / 6 - 6));
  addBrickWall(slide, left + 20, top + 28, 6, 3, brickWidth, 14, 5, name + "-wall");
  addRule(slide, left + 18, top + height - 42, width - 36, C.blue, name + "-floor");
  addShape(
    slide,
    "rect",
    { left: left + width / 2 - 42, top: top + height - 34, width: 84, height: 10 },
    C.blue,
    { style: "solid", fill: C.blue, width: 1 },
    name + "-paddle",
  );
  addBall(slide, left + width / 2 - 8, top + height - 82, 16, C.blue, name + "-ball");

  const obstaclePositions = [
    { x: 0.28, y: 0.52 },
    { x: 0.67, y: 0.63 },
    { x: 0.46, y: 0.43 },
    { x: 0.78, y: 0.35 },
  ];
  for (let index = 0; index < obstacleCount; index += 1) {
    const item = obstaclePositions[index % obstaclePositions.length];
    addBall(
      slide,
      left + width * item.x - 13,
      top + height * item.y - 13,
      26,
      C.orange,
      name + "-obstacle-" + (index + 1),
    );
  }
}

function addEyebrow(slide, value, number) {
  addText(
    slide,
    value,
    { left: 72, top: 42, width: 430, height: 24 },
    { fontSize: 16, bold: true, color: C.muted },
    "slide-" + number + "-eyebrow",
  );
}

function addFooter(slide, number) {
  addText(
    slide,
    "DAY 2  /  " + String(number).padStart(2, "0"),
    { left: 72, top: 672, width: 220, height: 20 },
    { fontSize: 16, bold: true, color: C.muted },
    "slide-" + number + "-footer",
  );
}

function buildCover(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addEyebrow(slide, "PYGAME BREAKOUT GAME", 1);
  addText(
    slide,
    "Obstacles\nand levels",
    { left: 72, top: 148, width: 520, height: 190 },
    { fontSize: 64, bold: true },
    "cover-title",
  );
  addText(
    slide,
    "How the game becomes harder after every cleared brick wall.",
    { left: 72, top: 382, width: 450, height: 70 },
    { fontSize: 24, color: C.muted },
    "cover-subtitle",
  );
  addRule(slide, 72, 500, 180, C.orange, "cover-rule");
  addText(
    slide,
    "Level 1 starts clean.\nEach new level adds one orange obstacle ball.",
    { left: 72, top: 520, width: 450, height: 78 },
    { fontSize: 20 },
    "cover-summary",
  );
  addGameBoard(slide, 670, 132, 500, 444, 2, "cover-game", { fill: "#EDEDED" });
  addText(
    slide,
    "orange = obstacle",
    { left: 828, top: 596, width: 250, height: 26 },
    { fontSize: 18, bold: true, color: C.orange, alignment: "center" },
    "cover-legend",
  );
  addFooter(slide, 1);
  return slide;
}

function buildLevelOne(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addEyebrow(slide, "01  /  STARTING POINT", 2);
  addText(
    slide,
    "Level 1 has no extra obstacles",
    { left: 72, top: 82, width: 780, height: 62 },
    { fontSize: 42, bold: true },
    "level-one-title",
  );
  addText(
    slide,
    "The player only needs to control the paddle and return the ball.",
    { left: 72, top: 164, width: 520, height: 54 },
    { fontSize: 22, color: C.muted },
    "level-one-lead",
  );
  addRule(slide, 72, 258, 520, C.line, "level-one-rule");
  addText(
    slide,
    "What is on screen?",
    { left: 72, top: 284, width: 340, height: 32 },
    { fontSize: 24, bold: true },
    "level-one-question",
  );
  addText(
    slide,
    "• Brick wall\n• Ball\n• Paddle\n• 0 obstacles",
    { left: 72, top: 336, width: 390, height: 180 },
    { fontSize: 22 },
    "level-one-list",
  );
  addText(
    slide,
    "This gives the player a simple first round to learn the controls.",
    { left: 72, top: 566, width: 500, height: 44 },
    { fontSize: 18, color: C.muted },
    "level-one-note",
  );
  addGameBoard(slide, 700, 238, 430, 330, 0, "level-one-game");
  addText(
    slide,
    "LEVEL 1",
    { left: 700, top: 184, width: 430, height: 38 },
    { fontSize: 26, bold: true, color: C.blue, alignment: "center" },
    "level-one-label",
  );
  addText(
    slide,
    "No orange balls yet",
    { left: 700, top: 590, width: 430, height: 28 },
    { fontSize: 18, color: C.muted, alignment: "center" },
    "level-one-caption",
  );
  addFooter(slide, 2);
  return slide;
}

function buildProgression(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addEyebrow(slide, "02  /  DIFFICULTY CURVE", 3);
  addText(
    slide,
    "Every new level adds one obstacle",
    { left: 72, top: 82, width: 820, height: 62 },
    { fontSize: 42, bold: true },
    "progression-title",
  );
  addText(
    slide,
    "The rule is simple: Level N contains N − 1 orange obstacle balls.",
    { left: 72, top: 164, width: 760, height: 38 },
    { fontSize: 22, color: C.muted },
    "progression-lead",
  );

  const boards = [
    { x: 86, level: "LEVEL 1", key: "level-1", count: 0 },
    { x: 440, level: "LEVEL 2", key: "level-2", count: 1 },
    { x: 794, level: "LEVEL 3", key: "level-3", count: 2 },
  ];

  for (const left of [392, 746]) {
    addShape(
      slide,
      "rightArrow",
      { left, top: 372, width: 54, height: 28 },
      C.blueLight,
      { style: "solid", fill: C.blueLight, width: 1 },
      "progression-arrow-" + left,
    );
  }

  for (const item of boards) {
    addText(
      slide,
      item.level,
      { left: item.x, top: 238, width: 260, height: 34 },
      { fontSize: 24, bold: true, alignment: "center" },
      item.key + "-label",
    );
    addGameBoard(slide, item.x, 286, 260, 220, item.count, "progression-" + item.key);
    addText(
      slide,
      String(item.count) + " obstacle" + (item.count === 1 ? "" : "s"),
      { left: item.x, top: 528, width: 260, height: 30 },
      { fontSize: 20, bold: true, color: item.count === 0 ? C.muted : C.orange, alignment: "center" },
      item.key + "-count",
    );
  }
  addText(
    slide,
    "0  →  1  →  2  →  3  →  ...",
    { left: 72, top: 606, width: 1136, height: 34 },
    { fontSize: 24, bold: true, color: C.blue, alignment: "center" },
    "progression-formula",
  );
  addFooter(slide, 3);
  return slide;
}

function buildTransition(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addEyebrow(slide, "03  /  LEVEL-UP MOMENT", 4);
  addText(
    slide,
    "The next level starts only after every brick is gone",
    { left: 72, top: 82, width: 1080, height: 62 },
    { fontSize: 38, bold: true },
    "transition-title",
  );
  addText(
    slide,
    "The game clears the old wall, shows the new level, then rebuilds the board with more obstacles.",
    { left: 72, top: 164, width: 930, height: 50 },
    { fontSize: 22, color: C.muted },
    "transition-lead",
  );

  for (const left of [378, 744]) {
    addShape(
      slide,
      "rightArrow",
      { left, top: 356, width: 70, height: 34 },
      C.blueLight,
      { style: "solid", fill: C.blueLight, width: 1 },
      "transition-arrow-" + left,
    );
  }

  const steps = [
    { x: 112, number: "1", title: "Destroy all bricks", body: "The last brick is hit." },
    { x: 478, number: "2", title: "Show the level", body: "The screen says LEVEL 2." },
    { x: 844, number: "3", title: "Build the next board", body: "New bricks return with 1 obstacle." },
  ];

  for (const step of steps) {
    const numberShape = addShape(
      slide,
      "ellipse",
      { left: step.x, top: 280, width: 82, height: 82 },
      C.blue,
      { style: "solid", fill: C.blue, width: 1 },
      "transition-step-" + step.number,
    );
    numberShape.text = step.number;
    numberShape.text.style = {
      fontSize: 34,
      bold: true,
      color: C.white,
      alignment: "center",
      verticalAlignment: "middle",
    };
    addText(
      slide,
      step.title,
      { left: step.x - 18, top: 392, width: 260, height: 40 },
      { fontSize: 24, bold: true, alignment: "center" },
      "transition-title-" + step.number,
    );
    addText(
      slide,
      step.body,
      { left: step.x - 18, top: 444, width: 260, height: 58 },
      { fontSize: 18, color: C.muted, alignment: "center" },
      "transition-body-" + step.number,
    );
  }

  addRule(slide, 72, 566, 1136, C.orange, "transition-rule");
  addText(
    slide,
    "That is the level loop: clear → announce → rebuild.",
    { left: 72, top: 588, width: 1136, height: 34 },
    { fontSize: 24, bold: true, alignment: "center" },
    "transition-takeaway",
  );
  addFooter(slide, 4);
  return slide;
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  buildCover(presentation);
  console.log("after cover");
  buildLevelOne(presentation);
  console.log("after level one");
  buildProgression(presentation);
  console.log("after progression");
  buildTransition(presentation);
  console.log("after transition");

  console.log("before pptx");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  console.log("Created " + FINAL_PPTX);
  console.log("Slides: " + presentation.slides.items.length);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
