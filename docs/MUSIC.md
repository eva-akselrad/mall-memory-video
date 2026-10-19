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

## Reference artist: Obras Ocultas

A lot of **Proper People**–style urbex edits use atmospheric beds from **[Obras Ocultas](https://soundcloud.com/obras-ocultas)** (Buenos Aires — *ambientaciones musicales*). Listen before you prompt Suno so you match the **mood**, not a random “creepy” drone:

| Track | Use it as a mood reference for… |
|-------|----------------------------------|
| [Urbex Utopy](https://soundcloud.com/obras-ocultas) | Empty buildings, exploration B-roll, hopeful melancholy |
| [Through glass](https://soundcloud.com/obras-ocultas) | Looking into closed spaces, reflective, glass/skylight light |
| [Limbo](https://soundcloud.com/obras-ocultas) | Liminal corridors, suspended time |
| [Nostalgia](https://soundcloud.com/obras-ocultas) | Sepia memory, old retail, bittersweet |
| [Alaska](https://soundcloud.com/obras-ocultas) | Cold wide pads, distant, cinematic (fans often cite this family of sound) |
| [Intriga y suspenso](https://soundcloud.com/obras-ocultas) | Tension without jump-scares — slow reveal |
| [Recuerdos Sepia](https://open.spotify.com/search/Recuerdos%20Sepia%20Obras%20Ocultas) | Warm faded memory, documentary piano |

**Using the real tracks:** SoundCloud is usually **personal listening** unless the artist licenses you. [The Proper People](https://soundcloud.com/theproperpeople) ask you to **contact them** before reusing music from their channel; same idea applies if you want an Obras Ocultas piece on **YouTube**. For your slideshow, **Suno in this vein** or **Pixabay** keeps you clear; or message the artist for permission.

YouTube: [Obras Ocultas channel](https://www.youtube.com/channel/UClcMRCkDW0H9OWkpV-nwHkg)

---

## Suno prompts (Obras Ocultas–inspired)

Use **Instrumental** / **No vocals**. Aim for **2–4 minutes**; the app loops the track if your slideshow runs longer.

**Style tags to paste at the end of any prompt:** `cinematic ambient, urbex documentary underscore, Buenos Aires film score feel, wide reverb, no drums, no vocals, fade-friendly intro and outro`

### 1 — Urbex Utopy (mall walk — start here)

```text
Instrumental cinematic ambient underscore for urban exploration documentary. Slow evolving synth pads and soft piano, emotional but restrained, sense of wonder in abandoned architecture. 68 BPM, major-minor bittersweet harmony, long hall reverb, subtle low pulse not a beat. Empty 1980s shopping mall at dusk, skylights, tile echoes. In the spirit of Obras Ocultas "Urbex Utopy" — not horror, not EDM. Wide stereo, gentle dynamics, no percussion, no vocals.
```

### 2 — Through glass (food court / storefronts)

```text
Instrumental ambient, looking through dirty glass into dead mall stores. Delicate piano motif, glassy synth textures, light arpeggios like reflections. Melancholy documentary, 62 BPM, lots of space between notes, reverb tail 4+ seconds. Obras Ocultas "Through glass" mood — contemplative, cinematic, no drums, no choir, no vocals.
```

### 3 — Limbo + Nostalgia (sepia slideshow)

```text
Sepia nostalgia instrumental, slow tape-warm pad, muted piano chords, faint analog hiss acceptable. Memory of childhood mall, faded photos, gentle sadness not scary. 58 BPM, minimal melody that repeats and evolves slowly. Obras Ocultas "Limbo" and "Nostalgia" — documentary preservation film, no beats, no vocals.
```

### 4 — Intriga y suspenso (power still on / neon hum)

```text
Suspense ambient for exploration video, slow tension rise without jump scares. Low drone, distant fluorescent buzz texture, sparse piano stabs far apart, minor key. 70 BPM feel but no drum kit — only pulse. Abandoned mall with lights still humming. Obras Ocultas "Intriga y suspenso" — cinematic, dark but controlled, no vocals, no trailer hits.
```

### 5 — Alaska (wide cold atrium)

```text
Cold wide cinematic ambient, large empty atrium, airy pads, slow string-like synth swells, very minimal piano. Isolated, vast, blue-hour light. 64 BPM, film documentary underscore, Obras Ocultas "Alaska" energy — ethereal, no percussion, no vocals, smooth ending for crossfade.
```

### Suno tips

- In **Style of** / description, add: `Obras Ocultas, urbex ambient, documentary underscore` (Suno may not know the name — the paragraphs above matter more).
- If it gets **too horror**: `less dissonance, more melancholy, Proper People documentary not horror film`.
- If it gets **too upbeat**: `even slower, remove drums, more reverb, less melody`.
- Add: `seamless loop friendly`, `mix -14 LUFS feel`.
- Export WAV or MP3 from Suno and point the app at that file.
