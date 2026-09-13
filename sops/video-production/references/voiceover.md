# Voiceover Generation

Using Eleven Labs for AI narration and voiceover production.

## When to Use

- Generating narration from a script
- Creating placeholder voiceover for timing
- Producing final voiceover for videos without human narrator

## Eleven Labs Integration

### API Setup

```bash
export ELEVEN_LABS_API_KEY="your-key-here"
```

### Text-to-Speech

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -H "xi-api-key: ${ELEVEN_LABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your script text here",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75,
      "style": 0.3,
      "use_speaker_boost": true
    }
  }' \
  --output voiceover.mp3
```

### Voice Selection

Choose a voice that matches the brand personality:

| Brand Tone | Voice Style | Stability | Similarity | Style |
|------------|-------------|-----------|------------|-------|
| Professional/tech | Calm, clear, authoritative | 0.5 | 0.75 | 0.3 |
| Friendly/casual | Warm, conversational | 0.4 | 0.7 | 0.5 |
| Energetic/marketing | Dynamic, enthusiastic | 0.3 | 0.8 | 0.7 |
| Tutorial/educational | Patient, measured | 0.6 | 0.75 | 0.2 |

### Voice Cloning (Professional Narrator)

If using a human narrator for some content and AI for the rest:

1. Record 3-5 minutes of clean reference audio
2. Create a voice clone via Eleven Labs dashboard
3. Use the cloned voice_id for consistency

## Script Preparation

### From Transcript to Clean Script

Raw transcripts (from Descript or other tools) need cleanup:

1. **Remove filler words**: "um", "uh", "like", "you know"
2. **Remove false starts**: Lines marked with `~strikethrough~`
3. **Consolidate takes**: Use the final take for each section
4. **Add pauses**: Use `...` or `<break time="0.5s"/>` for natural pacing
5. **Mark emphasis**: Capitalize or tag words that need emphasis

### Script Timing

Map script sections to video timeline:

```markdown
[00:00:00] If you work in marketing or sales, you're tracking competitors...
[00:00:35] Right now, this all lives in someone's head...
[00:01:00] I'm pasting in my first prompt...
```

This timing map drives:
- Scene durations in Root.tsx
- HighlightedPrompt section timing
- Sound cue placement
- Volume envelope shaping

## Remotion Integration

### Embedding Voiceover in Compositions

```tsx
import { Audio, staticFile } from 'remotion';

export const MyScene: React.FC = () => (
  <AbsoluteFill>
    <Audio src={staticFile('audio/voiceover-section1.mp3')} />
    {/* Scene content */}
  </AbsoluteFill>
);
```

### Full Video Assembly

For final delivery, voiceover is typically mixed externally (in Descript, DaVinci Resolve, or FFmpeg) alongside:
- Rendered scene clips
- Background music track
- Sound effects

```bash
# Combine voiceover + music + video
ffmpeg -i video.mp4 -i voiceover.mp3 -i music.mp3 \
  -filter_complex "[1]volume=1.0[vo];[2]volume=0.12[bg];[vo][bg]amix=inputs=2[audio]" \
  -map 0:v -map "[audio]" -c:v copy -c:a aac \
  -y final-output.mp4
```

## Workflow with Human Narrator

When the video uses a human narrator (recommended for quality):

1. **Write the script** from the video concept
2. **Record** with human narrator
3. **Edit in Descript** — cut filler, tighten pacing
4. **Export transcript** with timestamps
5. **Use timestamps** to drive scene durations and animation timing
6. **Generate title cards** in Remotion synced to the transcript
7. **Render scenes** and import into video editor
8. **Layer** voiceover + scenes + screencasts + music in final edit

## Tips

- **Voiceover drives everything** — record/generate it first, then time scenes to it
- **Leave breathing room** — don't pack scenes edge-to-edge with narration
- **Scene overlap** — title cards can start 0.5-1s before the voiceover mentions the topic
- **Music ducking** — lower background music by 40-50% during narration vs. transitions
