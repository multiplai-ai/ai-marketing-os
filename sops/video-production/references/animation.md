# Animation Patterns

Spring physics, timing, and motion recipes for Remotion video production.

## Core Principle: Springs, Not Easings

In Remotion, use `spring()` for all entrance/exit animations. Springs feel organic and are deterministic (same result every render). Avoid CSS transitions — they don't work in frame-by-frame rendering.

```tsx
import { spring, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const entrance = spring({
  frame,
  fps,
  delay: 10,
  config: { damping: 20, stiffness: 80 },
});

const opacity = interpolate(entrance, [0, 1], [0, 1]);
const y = interpolate(entrance, [0, 1], [30, 0]);
```

## Spring Presets

| Feel | damping | stiffness | mass | Use Case |
|------|---------|-----------|------|----------|
| **Gentle** | 20 | 80 | 1.0 | Text reveals, titles |
| **Snappy** | 200 | 100 | 1.0 | Quick pops, badges |
| **Punchy** | 14 | 60 | 1.1 | Cards slamming in, impacts |
| **Bouncy** | 10 | 100 | 1.0 | Playful elements, emojis |
| **Smooth** | 30 | 50 | 1.0 | Slow fades, background elements |
| **Heavy** | 16 | 70 | 1.2 | Large cards, panels |

## Entrance Patterns

### Fade + Slide Up (most common)
```tsx
const opacity = interpolate(entrance, [0, 1], [0, 1]);
const y = interpolate(entrance, [0, 1], [30, 0]);
// transform: `translateY(${y}px)`, opacity
```

### Scale Pop
```tsx
const scale = interpolate(entrance, [0, 1], [0.8, 1]);
const opacity = interpolate(entrance, [0, 1], [0, 1]);
// transform: `scale(${scale})`, opacity
```

### Fly-In from Direction
```tsx
const x = interpolate(entrance, [0, 1], [fromX, 0]);
const y = interpolate(entrance, [0, 1], [fromY, 0]);
const rotate = interpolate(entrance, [0, 1], [initialRotate * 3, restRotate]);
const scale = interpolate(entrance, [0, 1], [0.6, 1]);
// transform: `translate(${x}px, ${y}px) rotate(${rotate}deg) scale(${scale})`
```

### Scatter Exit
```tsx
import { Easing } from 'remotion';

const scatterProgress = interpolate(
  frame,
  [scatterStart, scatterStart + 45],  // ~1.5s
  [0, 1],
  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) }
);
const scatterX = scatterProgress * exitX * 2;
const scatterY = scatterProgress * exitY * 2;
const scatterRotate = scatterProgress * exitRotate * 3;
const scatterOpacity = 1 - scatterProgress;
```

## Staggered Timing

### Constant Stagger
Elements appear with equal spacing:
```tsx
const delay = baseDelay + index * staggerFrames;
// Typical: 10 + i * 5 for bullets
// Typical: 12 + i * 17 for cards
```

### Accelerating Stagger
Earlier items get more time, later items come faster:
```tsx
const delay = baseDelay + Math.pow(index, 0.7) * staggerFrames;
```

### Section-Based Stagger
Tied to voiceover timing (seconds, not frames):
```tsx
const delay = sectionStartSec * fps;
```

## Idle Float / Breathing

For elements that have landed and need subtle life:

```tsx
const t = frame / fps;
const floatY = Math.sin(t * 1.2 + index * 2) * 6;
const floatX = Math.cos(t * 0.8 + index * 3) * 4;
// Add to transform after entrance is complete
```

For background elements:
```tsx
const scale = 1 + Math.sin(t * 0.3) * 0.15;
const opacity = baseOpacity + Math.sin(t * 0.2 + phaseOffset) * 0.08;
```

**Important**: Use `transformOrigin` anchored to element center. No lateral drift for backgrounds.

## Highlight Walking

For HighlightedPrompt — timed section focus:

```tsx
const highlightIn = spring({
  frame: Math.max(0, frame - section.startSec * fps),
  fps,
  config: { damping: 20, stiffness: 80 },
});
const highlightOut = frame > section.endSec * fps
  ? spring({
      frame: frame - section.endSec * fps,
      fps,
      config: { damping: 20, stiffness: 80 },
    })
  : 0;

const highlight = Math.max(0, highlightIn - highlightOut);
const textOpacity = interpolate(highlight, [0, 1], [0.2, 1]);  // Dim inactive
const barOpacity = interpolate(highlight, [0, 1], [0, 0.8]);   // Show gradient bar
```

## Speed Adjustment

To slow down an animation by X%:

```tsx
// Original: delay 12 + i * 17
// 70% speed = multiply delays by 1/0.7 ≈ 1.43
const delay = Math.round((12 + i * 17) / 0.7);

// Also reduce stiffness and increase mass for heavier feel
config: { damping: 14, stiffness: 60 * 0.7, mass: 1.1 / 0.7 }
```

## Focus/Dim State Transitions

For comparing two elements (side-by-side cards):

```tsx
// Timeline interpolation (not spring — we want exact frame control)
const focusPhase = interpolate(
  frame,
  [startFrame, startFrame + 20],
  [0, 1],
  { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
);

// Focused card
const focusedScale = 1 + focusPhase * 0.05;
const focusedOpacity = 1;

// Dimmed card
const dimmedScale = 1 - focusPhase * 0.05;
const dimmedOpacity = 1 - focusPhase * 0.6;
const dimmedBlur = focusPhase * 4;  // filter: blur(${dimmedBlur}px)
```

## Sound Sync Pattern

Add sound effects at animation trigger points:

```tsx
import { Audio, Sequence, staticFile } from 'remotion';

// Sound on each staggered entrance
{items.map((_, i) => (
  <Sequence key={i} from={entranceDelay + i * stagger}>
    <Audio src={staticFile('audio/effect.mp3')} volume={0.15} />
  </Sequence>
))}

// Sound on section transitions
{sections.slice(1).map((section) => (
  <Sequence key={section.id} from={Math.round(section.startSec * fps)}>
    <Audio src={staticFile('audio/Swoosh.mp3')} volume={0.15} />
  </Sequence>
))}
```

## GPU Performance

Always add to animated elements:
```tsx
style={{
  willChange: 'transform, opacity',
  // Use transform for position/scale/rotation (GPU-accelerated)
  // Avoid animating: width, height, padding, margin (triggers layout)
}}
```

For blur animations, also add `filter` to willChange:
```tsx
willChange: 'transform, opacity, filter',
```

## Common Pitfalls

1. **Don't use CSS `transition`** — doesn't work in Remotion's frame-by-frame renderer
2. **Don't animate layout properties** — use `transform: translate()` instead of `top/left`
3. **Clamp extrapolation** when using `interpolate` with frame ranges:
   ```tsx
   { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
   ```
4. **Use `Math.round()` on frame calculations** — fractional frames cause jitter
5. **Smart quotes break JSX** — use `"What's"` not `'What's'`
