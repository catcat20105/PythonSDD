export async function resolve(specifier, context, nextResolve) {
  if (specifier === "skia-canvas") {
    return { url: "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/artifact_tool_v2/bin/node_modules/skia-canvas/lib/index.mjs", format: "module", shortCircuit: true };
  }
  if (specifier === "@oai/walnut/wasm/dotnet.js") {
    return { url: "file:///C:/Users/CJSCOPE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/artifact_tool_v2/bin/node_modules/@oai/walnut/wasm/dotnet.js", format: "module", shortCircuit: true };
  }
  return nextResolve(specifier, context);
}