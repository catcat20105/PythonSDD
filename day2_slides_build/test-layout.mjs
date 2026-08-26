import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const p = await PresentationFile.importPptx(await FileBlob.load("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/test-artifact.pptx"));
console.log("slides", p.slides.items.length);
const layout = await p.slides.items[0].export({format:"layout"});
await fs.writeFile("C:/Users/CJSCOPE/Desktop/PythonSDD/day2_slides_build/test-layout.json", await layout.text());
console.log("layout saved");