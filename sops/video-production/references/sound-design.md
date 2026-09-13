# Sound Design

Complete sound design workflow for video productions — SFX, music beds, mixing, and volume envelopes.

## Sound Categories

| Category | When | Duration | Volume | API |
|----------|------|----------|--------|-----|
| **transition-swoosh** | Scene changes, topic shifts | 1-2s | 30-40% | MMAudio V2 |
| **reveal-impact** | Title reveals, UI elements appear | 0.5-1s | 35-45% | MMAudio V2 |
| **ambient-tech** | Code on screen, typing, demos | 5-15s | 15-20% | MMAudio V2 |
| **quote-accent** | Quote cards, key statements | 1-2s | 25-35% | MMAudio V2 |
| **alert-chime** | Notifications, alerts | 0.5-1s | 30-40% | MMAudio V2 |
| **music-bed** | Section backgrounds | 15-60s | 12-18% | Song Generation |
| **background-track** | Full video underscore | Loop full length | 10-15% | Song Generation |

## Workflow

### 1. Analyze Transcript -> Cue Sheet

Walk through the voiceover transcript and identify 10-20 key moments:

```json
[
  { "id": 0, "category": "background-track", "startTime": 0, "endTime": 463, "volume": 0.12,
    "prompt": "Subtle cinematic ambient background, dark, modern, minimal, gentle pads, no percussion, no vocals, loopable" },
  { "id": 1, "category": "reveal-impact", "startTime": 0, "endTime": 1, "volume": 0.40,
    "prompt": "Soft impact reveal sound, digital, clean, modern, subtle bass thud with shimmer" },
  { "id": 2, "category": "transition-swoosh", "startTime": 35, "endTime": 37, "volume": 0.35,
    "prompt": "Cinematic whoosh transition, subtle, modern, smooth movement sound" }
]
```

### 2. Generate Individual Sounds

**Short SFX** (MMAudio V2):
```bash
curl -X POST "https://api.wavespeed.ai/api/v3/wavespeed-ai/mmaudio-v2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${WAVESPEED_API_KEY}" \
  -d '{
    "prompt": "Cinematic whoosh transition, subtle, modern, dark atmosphere",
    "duration": 2.0,
    "negative_prompt": "speech, vocals, music, loud, harsh"
  }'
```

**Background music** (Song Generation):
```bash
curl -X POST "https://api.wavespeed.ai/api/v3/wavespeed-ai/song-generation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${WAVESPEED_API_KEY}" \
  -d '{
    "lyric": "[inst]",
    "description": "Subtle cinematic ambient background music, dark, modern, minimal, no percussion, instrumental",
    "genre": "Auto"
  }'
```

### 3. Mix with FFmpeg

Combine all tracks with `adelay` for timestamp placement:

```bash
ffmpeg \
  -i background-track.mp3 \
  -i swoosh-0s.mp3 \
  -i impact-35s.mp3 \
  -filter_complex "
    [0]volume=0.12[bg];
    [1]adelay=0|0,volume=0.35[s1];
    [2]adelay=35000|35000,volume=0.40[s2];
    [bg][s1][s2]amix=inputs=3:duration=longest:dropout_transition=0[out]
  " \
  -map "[out]" -ac 2 -ar 44100 -b:a 192k \
  -t 463 -y full-sound-design.mp3
```

### 4. Volume Envelope for Background Music

Shape the background track's volume over time for dynamic feel:

```bash
ffmpeg -i full-score.mp3 \
  -af "
    volume='if(lt(t,2),t/2*1.0,
           if(lt(t,15),1.0,
           if(lt(t,35),1.0-(t-15)/20*0.45,
           if(lt(t,420),0.55,
           if(lt(t,435),0.55+(t-420)/15*0.5,
           if(lt(t,450),1.05,
           if(lt(t,463),1.05-(t-450)/13*1.05,
           0)))))))':eval=frame,
    afade=t=in:d=1.5,
    afade=t=out:st=458:d=5
  " \
  -t 463 -ac 2 -ar 44100 -b:a 192k \
  -y full-score-shaped.mp3
```

**Envelope pattern for most videos**:
- **0-2s**: Fade in
- **2-15s (intro)**: Full volume (1.0) — energy for the hook
- **15-35s**: Ramp down to 0.55 as narration settles
- **35-end-30s (middle)**: Steady 0.55 — low and even under explanations
- **end-30s to end-15s**: Build back up to 1.05 for the recap/ending
- **Last 15s**: Wind down with fade out

## In-Scene Sound (Remotion)

For sounds baked into individual scenes (not the master mix):

```tsx
import { Audio, Sequence, staticFile } from 'remotion';

// Swoosh on section transitions
{sections.slice(1).map((section) => (
  <Sequence key={section.id} from={Math.round(section.startSec * fps)}>
    <Audio src={staticFile('audio/Swoosh.mp3')} volume={0.15} />
  </Sequence>
))}

// Button alert on card entrances
{cards.map((_, i) => (
  <Sequence key={i} from={entranceDelay + i * stagger}>
    <Audio src={staticFile('audio/Button Alert.mp3')} volume={0.15} />
  </Sequence>
))}
```

## Prompt Engineering for Sound

1. **Always include "subtle"** — background sounds, never the focus
2. **Include "modern" and "cinematic"** — professional feel
3. **Specify "no vocals"** for music — avoids distraction
4. **Be concrete** — "soft bass thud with shimmer" > "cool impact"
5. **Add negative prompt** — `"speech, vocals, music, loud, harsh, distorted"`

## Output Structure

```
sound-design/
├── manifest.json              # Cue sheet with all tracks, timings, volumes
├── individual-tracks/         # Each SFX file
│   ├── 00-background-underscore.mp3
│   ├── 01-reveal-impact-0s.mp3
│   └── ...
├── mixed/
│   └── full-sound-design.mp3  # Final mixed output
└── samples/                   # Iterations and experiments
    ├── full-score-v1-final.mp3
    └── full-score-v2-final.mp3
```

## Cost Reference

| Component | API | Est. Cost |
|-----------|-----|-----------|
| 10-15 short SFX | MMAudio V2 | $0.01-0.08 |
| 2-3 ambient beds | MMAudio V2 | $0.03-0.09 |
| 1-2 music tracks | Song Generation | $0.10-0.50 |
| **Total** | | **$0.15-0.70** |
