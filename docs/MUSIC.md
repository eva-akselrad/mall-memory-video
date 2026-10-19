# Music for your mall video

## Built-in demo track (free, yours to use)

The repo includes a **synthetic** ambient bed — no samples, no copyright claims:

```bash
python -m mall_memory.demo_music
```

Default file: `assets/demo-mall-ambient.mp3` (~2.5 min). In the **desktop UI**, click **Use demo music**.

Regenerate a longer bed for big slideshows:

```bash
python -m mall_memory.demo_music --seconds 300 -o assets/demo-mall-ambient.mp3
```

---

## Free downloads (documentary / ambient)

Pixabay tracks work well under their [Content License](https://pixabay.com/service/license/) (check current terms for your use case):

| Track | Vibe | Link |
|-------|------|------|
| The Documentary Ambient Piano | Sparse piano, reflective | https://pixabay.com/music/solo-piano-the-documentary-ambient-piano-159128/ |
| Documentary_Tidal | Piano + atmosphere, cinematic | https://pixabay.com/music/ambient-documentary-tidal-11052/ |
| Mystery Atmosphere Ambient Documentary | Quiet, slightly eerie | https://pixabay.com/music/solo-piano-mystery-atmosphere-ambient-documentary-380714/ |

Browse more: https://pixabay.com/music/search/documentary%20ambient/

---

## Suno prompts (copy-paste)

Use **Instrumental** / **No vocals**. Aim for **2–4 minutes**; the app loops the track if your slideshow runs longer.

### 1 — Proper People mall walk (recommended)

```text
Instrumental only, no vocals, no drums. Slow documentary ambient for abandoned 1980s shopping mall exploration. Sparse felt piano, long reverb, distant synth pad, subtle neon-tinged atmosphere. 65 BPM, meditative, cinematic, slightly melancholy but not horror. Think empty food court at dusk, skylights, echoing tile corridors. Gentle fade-friendly intro and outro. High quality, wide stereo, no sudden hits.
```

### 2 — Liminal / HVAC hum

```text
Instrumental drone ambient, no beats. Empty retail liminal space, soft mall HVAC hum texture, very slow evolving analog synth chords in D minor. Minimal piano notes far in the background. Urban exploration B-roll music, tense but calm, 60 BPM. Lots of space, reverb tail, no percussion, no voice.
```

### 3 — Nostalgic neon (slightly brighter)

```text
Instrumental synthwave-adjacent documentary score, no vocals. Nostalgic 1989 mall memories, warm analog pads, soft arpeggio like distant arcade, restrained and slow not energetic. 72 BPM, cinematic exploration vlog, bittersweet, clean mix, no heavy bass drops.
```

### 4 — Piano-only elegy

```text
Solo piano instrumental, slow rubato, empty architecture documentary. Minor key, simple motif, heavy hall reverb, silence between phrases. Abandoned place preservation film, emotional but understated, 55 BPM, no other instruments.
```

### Suno tips

- Add: `seamless loop friendly`, `no vocals`, `royalty-free style`, `mix -14 LUFS feel`.
- If it gets too upbeat, regenerate with: `even slower, remove drums, more reverb, less melody`.
- Export WAV or MP3 from Suno and point the app at that file.
