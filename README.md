# Mall Memory Video

Turn a folder of mall photos into a **slideshow with music** — your images are used **as-is** (no zoom, shake, or color grading). Style presets only control **timing** and **crossfades**, in the spirit of slow documentary mall videos like [The Proper People](https://www.youtube.com/@TheProperPeople).

You supply the **photos** and a **music file** you have rights to use (ambient / instrumental works best).

## Requirements

- Python 3.11+
- [FFmpeg](https://ffmpeg.org/) on your PATH (you already need this for encoding)

## Setup

```bash
cd mall-memory-video
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Desktop UI

```bash
python -m mall_memory
```

Or explicitly:

```bash
python -m mall_memory --gui
```

Pick your photo folder, music file, style preset, and click **Generate video**. Rendering runs in the background with a progress bar and a **Log** panel.

CLI logging (stderr):

```bash
python -m mall_memory -i photos -m music-folder -o out.mp4 -v
python -m mall_memory ... --log-file output/render.log
```

## Command line

```bash
python -m mall_memory ^
  --images "C:\path\to\mall pictures" ^
  --music "C:\path\to\ambient-track.mp3" ^
  --output "output\my-mall-film.mp4"
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--style proper-people` | `proper-people` | Slow holds, longer crossfades |
| `--style neon-mall` | | Slightly faster pacing, shorter crossfades |
| `--sort name` / `date` | `name` | Order slides by filename or photo date |
| `--seconds-per-image` | preset | Override how long each photo stays on screen |
| `--crossfade` | preset | Crossfade length between slides |
| `--width` / `--height` | 1920×1080 | Export resolution |
| `--fps` | 24 | Frame rate |

### Music

See **[docs/MUSIC.md](docs/MUSIC.md)** for:

- **Built-in demo track** (`assets/demo-mall-ambient.mp3`) — synthetic ambient, free to use
- **Free Pixabay** documentary picks
- **[Obras Ocultas](https://soundcloud.com/obras-ocultas)** track picks for Proper People–style urbex ambient

Quick demo:

```bash
python -m mall_memory.demo_music
```

In the UI: **Use demo music** (or **Generate demo track** if the file is missing).

## What it does

1. Loads every image in your folder (jpg, png, webp, …)
2. **Letterboxes** each photo to the export size (no crop, no filters)
3. **Crossfades** between photos (timing preset)
4. Mixes your **music** (one file or a **folder** of tracks played in order) with fade-in/out; repeats the playlist if the slideshow runs longer

## License

MIT — photos and music you add remain yours.
