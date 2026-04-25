# Paint Application Extended (TSIS2) — OPTIMIZED

Fast and responsive drawing application with freehand, shapes, flood fill, and text tools.

## Installation

```bash
pip install pygame
```

## Usage

```bash
python paint.py
```

## Tools & Features

### Drawing Tools
- **Pencil** — Freehand drawing (click & drag)
- **Line** — Straight lines with live preview
- **Rectangle** — Draw rectangles
- **Circle** — Draw circles
- **Square** — Draw perfect squares
- **Right Triangle** — Right-angled triangle
- **Equilateral Triangle** — 3-sided regular polygon
- **Rhombus** — Diamond shape

### Special Tools
- **Bucket** — Flood fill (click to fill closed regions)
- **Text** — Click to place text, type, press Enter to confirm, Escape to cancel
- **Eraser** — Erase with adjustable size
- **Color Picker** — Press `C` to pick color from canvas

### Brush Sizes
- **1** — Small (2 px)
- **2** — Medium (5 px)
- **3** — Large (10 px)

Press 1, 2, or 3 to change brush size instantly.

## Controls

| Key | Action |
|---|---|
| `1`, `2`, `3` | Change brush size |
| `C` | Color picker mode |
| `Ctrl+S` | Save canvas as timestamped PNG |
| **`Ctrl+Z`** | **Undo last action** ✨ |
| `Delete` | Clear entire canvas |
| Click toolbar | Select tool or color |
| `Enter` | Confirm text input |
| `Escape` | Cancel text input |

## Saving & Undo

- **Save**: Press `Ctrl+S` → saves to `~/Pictures/Paint/canvas_YYYYMMDD_HHMMSS.png`
- **Undo**: Press `Ctrl+Z` → restores last state (up to 20 steps)
- **Clear**: Press `Delete` → clears canvas (also saves to undo history)

Files are saved automatically to your Pictures folder.

## Features Implemented

✅ Freehand pencil drawing  
✅ Straight line tool with live preview  
✅ 3 adjustable brush sizes (2, 5, 10 px)  
✅ All shapes respect active brush size  
✅ Flood fill (bucket) tool  
✅ Text placement (click, type, Enter/Escape)  
✅ Color picker (C key)  
✅ Save to PNG with timestamp (Ctrl+S) → `~/Pictures/Paint/`  
✅ **Undo history (up to 20 steps)** ✨  
✅ Clear canvas (Delete key)  
✅ Live preview for all shape tools  
✅ Optimized rendering (no lag)

## Performance Optimizations

- **Dirty flag rendering** — only redraws when something changes
- **Efficient event handling** — minimal processing per frame
- **Smart preview caching** — preview only updates when needed
- Stable 60 FPS even on large canvases

## Notes

- Canvas size: 1010 x 700 px (toolbar is 190 px wide)
- Uses only Pygame built-in functions — no extra libraries
- Flood fill uses BFS to avoid stack overflow on large areas
- Zero lag, instant feedback on all tools
