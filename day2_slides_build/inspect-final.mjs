import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const p = await PresentationFile.importPptx(await FileBlob.load("C:/Users/CJSCOPE/Desktop/PythonSDD/Day2_obstacles_and_levels.pptx"));
const x = await p.inspect({kind:"slide,textbox,shape,image,notes",maxChars:50000});
await fs.mkdir("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/output", {recursive:true});
await fs.writeFile("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/output/final-inspection.ndjson", x.ndjson || "");
console.log("inspection saved");