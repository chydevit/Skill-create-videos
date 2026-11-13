# khmer-memory-doc

A Claude Code skill for respectful **remembrance documentaries** in Khmer with English subtitles, drawn in a soft pencil-and-charcoal "memory drawing" style.

- **Characters:** an elderly survivor tells her grandchild what she lived through, at a memorial. Both are fictional composites.
- **Look:** memories are drawn in grey, the present day in warm colour, and colour returns at the end.
- **Research:** the research comes first and stops for approval. Every fact is checked against two sources.
- **Images:** symbolic imagery replaces violence, and authentic photos appear as old prints in a family album with their licences.
- **Sound:** Khmer narration in locked VoxCPM2 voices, checked with Khmer Whisper, and a sparse tro/khim score.

The worked example is *Democratic Kampuchea 1975–1979: We Remember* (15:18) in `examples/democratic_kampuchea/`.

- Requirements: the [khmer-history-doc](https://github.com/chydevit/animinations-v3) skill installed at `~/.claude/skills/khmer-history-doc` (its render and voice environments, and its map fetcher).
- Start: see `SKILL.md` and `references/workflow.md`.

Images in `examples/democratic_kampuchea/archive/img` are public domain or Creative Commons. Each licence and attribution is in `archive/manifest.json`.
