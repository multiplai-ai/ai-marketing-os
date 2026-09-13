# Rendering

Remotion rendering workflows — single scenes, batch rendering, chunk rendering for long scenes, and final delivery.

## Output location convention

Resolve working and final destinations from the consumer's project instructions.
Keep raw renders and sensitive footage out of Git when required. Deliver a durable
link, editable source and export manifest; a temporary local path is not a handoff.

## Single Scene Render

```bash
npx remotion render src/index.ts "S01-Intro" "out/<project-name>/S01-Intro.mp4" \
  --width 1920 --height 1080
```

## Batch Render

```bash
for id in S01-Intro S02-Content S03-Scenario S04-Tip; do
  npx remotion render src/index.ts "$id" "out/<project-name>/${id}.mp4" \
    --width 1920 --height 1080
done
```

## Chunk Rendering (Long Scenes)

Scenes over ~45s may hit `delayRender()` timeout (28s default). Render in 15-second chunks and concatenate.

```bash
# 60s scene at 30fps = 1800 frames
# Render in 450-frame (15s) chunks
npx remotion render src/index.ts "BG-Gradient" "out/part1.mp4" --frames=0-449 --timeout=60000
npx remotion render src/index.ts "BG-Gradient" "out/part2.mp4" --frames=450-899 --timeout=60000
npx remotion render src/index.ts "BG-Gradient" "out/part3.mp4" --frames=900-1349 --timeout=60000
npx remotion render src/index.ts "BG-Gradient" "out/part4.mp4" --frames=1350-1799 --timeout=60000

# Concatenate
cat > /tmp/concat.txt << EOF
file 'out/part1.mp4'
file 'out/part2.mp4'
file 'out/part3.mp4'
file 'out/part4.mp4'
EOF

ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy "out/my-video/BG-Gradient.mp4"

# Cleanup
rm out/part*.mp4 /tmp/concat.txt
```

## Render Quality Settings

### Full HD (Standard)
```bash
--width 1920 --height 1080
```

### 4K (High Quality)
```bash
--width 3840 --height 2160
```

### Preview (Fast)
```bash
--width 960 --height 540 --quality 50
```

## Codec Options

```bash
# H.264 (default, widest compatibility)
--codec h264

# ProRes (lossless, for editing workflows)
--codec prores --prores-profile 4444

# VP9/WebM (web delivery)
--codec vp8
```

## Concurrency

Remotion renders frames in parallel. Default is usually fine, but for complex scenes:

```bash
# Reduce concurrency if running out of memory
--concurrency 2

# Increase for simple scenes on powerful machines
--concurrency 8
```

## Common Issues

### delayRender Timeout
**Error**: `delayRender() was called but not cleared after 28000ms`
**Fix**: Use `--timeout=60000` or chunk render

### Out of Memory
**Error**: Heap out of memory
**Fix**: Reduce `--concurrency` or add `--gl=angle` (macOS)

### Black Frames
**Cause**: Component not rendering on first frame
**Fix**: Check that all `spring()` delays account for frame 0

### Missing Assets
**Error**: `Could not find file`
**Fix**: Ensure assets are in `public/` and referenced via `staticFile()`

## Verification After Render

```bash
# Check output file
ffprobe -v quiet -show_entries format=duration,bit_rate -of default=noprint_wrappers=1 out/my-video/S01-Intro.mp4

# Quick preview
ffplay -autoexit out/my-video/S01-Intro.mp4
```

## Final Delivery

For the complete video assembly (not individual title cards):

```bash
# Combine rendered scenes with voiceover and music
ffmpeg \
  -i "screencast-footage.mp4" \
  -i "voiceover.mp3" \
  -i "full-score.mp3" \
  -filter_complex "
    [1]volume=1.0[vo];
    [2]volume=0.12[bg];
    [vo][bg]amix=inputs=2[audio]
  " \
  -map 0:v -map "[audio]" \
  -c:v copy -c:a aac -b:a 192k \
  -y "final-video.mp4"
```

For more complex assembly with multiple video tracks, use a video editor (DaVinci Resolve, Premiere, Descript) and import the Remotion renders as overlays.

## Studio (Development)

For previewing and iterating during development:

```bash
npm start
# Opens Remotion Studio at http://localhost:3000
# Scrub through scenes, adjust timing, see changes live
```
