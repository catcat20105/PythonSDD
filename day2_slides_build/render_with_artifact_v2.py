from pathlib import Path
from artifact_tool_v2 import Blob, PresentationFile

input_path = Path(r"C:\Users\CJSCOPE\Desktop\PythonSDD\Day2_obstacles_and_levels.pptx")
out_dir = Path(r"C:\Users\CJSCOPE\Desktop\PythonSDD\day2_slides_build\rendered")
out_dir.mkdir(parents=True, exist_ok=True)
presentation = PresentationFile.import_pptx(Blob.load(input_path))
for number, slide in enumerate(presentation.slides.items, 1):
    image = slide.export({"format": "png", "scale": 1})
    image.save(out_dir / f"slide-{number}.png")
    print(f"rendered slide {number}")