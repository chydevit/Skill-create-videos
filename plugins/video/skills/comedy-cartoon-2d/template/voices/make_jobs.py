"""Write build/vox/jobs.json (input for the VoxCPM2 worker) from voices/lines.json.

Locked voices go to voices/<who>.wav (designed once from the voice's English description + sample line);
every line is cloned from its character's locked clip into build/vox/<line_id>.wav.
Existing files are skipped by the worker, so delete a clip to regenerate it.
"""
import json
import os

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f"{P}/voices/lines.json"))
jobs = {"voices": [], "lines": []}
for vid, v in d.get("voices", {}).items():
    if v.get("engine", "voxcpm") != "voxcpm":
        continue
    jobs["voices"].append({"voice_id": vid, "design": v["design"], "sample_text": v["sample"],
                           "out_wav": f"{P}/voices/{vid}.wav", "seed": v.get("seed", 1234)})
for lid, line in d.get("lines", {}).items():
    who, text = line[0], (line[3] if len(line) > 3 and line[3] else line[1])  # optional 4th field: spoken text (respelling)
    v = d["voices"][who]
    if v.get("engine", "voxcpm") != "voxcpm":
        continue
    jobs["lines"].append({"id": lid, "text": text, "ref_wav": f"{P}/voices/{who}.wav", "ref_text": v["sample"],
                          "out_wav": f"{P}/build/vox/{lid}.wav", "seed": d.get("seeds", {}).get(lid, 7),
                          "clone_mode": v.get("clone_mode", "ref")})
os.makedirs(f"{P}/build/vox", exist_ok=True)
json.dump(jobs, open(f"{P}/build/vox/jobs.json", "w"), ensure_ascii=False, indent=1)
todo = sum(not os.path.exists(x["out_wav"]) for x in jobs["voices"] + jobs["lines"])
print(f"{len(jobs['voices'])} voices, {len(jobs['lines'])} lines, {todo} to synthesise")
