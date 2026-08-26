import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const p = await PresentationFile.importPptx(await FileBlob.load("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/test-artifact.pptx"));
console.log("slides", p.slides.items.length);
const x = await p.inspect({kind:"slide,textbox,shape",maxChars:3000});
await fs.writeFile("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/test-inspect.json", x.ndjson || "");
console.log("inspect saved");