#!/usr/bin/env python3
"""Visualize official RHCR KIVA/ASCII map + results/paths.txt.

The source format is determined from Jiaoyang-Li/RHCR, src/States.cpp and
src/BasicSystem.cpp.  No RHCR simulation or planner code is modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PALETTE = [
    "#2074C8", "#D97731", "#1D9B78", "#8A59B7", "#D64B5A",
    "#1590A2", "#A68025", "#DC67A2", "#627BC5", "#738A32",
    "#A33A78", "#BE6B25", "#20605E", "#975648", "#6366F1",
]
TILE = 23
MAP_X = 38
MAP_Y = 81
PANEL_GAP = 24
PANEL_W = 270


def load_font(sz, bold=False):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def read_rhcr_map(path: Path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 5:
        raise ValueError("Invalid RHCR .map: expected size + 3 metadata lines + grid")
    try:
        height, width = (int(x.strip()) for x in lines[0].split(","))
    except Exception as exc:
        raise ValueError("RHCR map starts with 'rows,cols', e.g. '33,46'") from exc
    if height < 1 or width < 1:
        raise ValueError("Grid dimensions must be positive")
    grid = [line.strip() for line in lines[4 : 4 + height]]
    if len(grid) != height or any(len(row) != width for row in grid):
        raise ValueError(f"Grid dimensions differ from header {height}x{width}")
    return grid


def read_rhcr_paths(path: Path, grid):
    lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not lines:
        raise ValueError("paths.txt is empty")
    try:
        n = int(lines[0])
    except ValueError as exc:
        raise ValueError("paths.txt must begin with robot count") from exc
    if n < 1 or len(lines) - 1 < n:
        raise ValueError(f"Expected {n} path lines, found {len(lines) - 1}")
    paths = []
    w = len(grid[0]); h = len(grid)
    for agent_id, line in enumerate(lines[1 : n + 1]):
        records = []
        for token in line.split(";"):
            token = token.strip()
            if not token:
                continue
            parts = token.split(",")
            if len(parts) != 3:
                raise ValueError(f"Agent {agent_id}: expected 'location,orientation,timestep', got {token!r}")
            loc, orient, t = map(int, parts)
            if loc < 0 or loc >= h * w:
                raise ValueError(f"Agent {agent_id}, t={t}: out-of-bounds location {loc}")
            if grid[loc // w][loc % w] == "@":
                raise ValueError(f"Agent {agent_id}, t={t}: position is an obstacle")
            records.append((loc, orient, t))
        if not records or records[0][2] != 0:
            raise ValueError(f"Agent {agent_id}: path must start at t=0")
        for idx, (_, _, t) in enumerate(records):
            if t != idx:
                raise ValueError(f"Agent {agent_id}: nonconsecutive timestep, expected {idx}, got {t}")
        paths.append(records)
    # Use only the interval covered by all agents. A warning protects against silent truncation.
    horizon = min(len(p) - 1 for p in paths)
    if horizon < 1:
        raise ValueError("Not enough trajectory data to animate")
    if len({len(p) for p in paths}) != 1:
        raise ValueError("Agents have different trace lengths; inspect RHCR output before rendering")
    return paths, horizon


def xy(loc, w):
    row, col = divmod(loc, w)
    return MAP_X + col * TILE + TILE // 2, MAP_Y + row * TILE + TILE // 2


def board(grid):
    h, w = len(grid), len(grid[0])
    img_w = MAP_X * 2 + w * TILE + PANEL_GAP + PANEL_W
    img_h = MAP_Y + h * TILE + 60
    im = Image.new("RGB", (img_w, img_h), "#F7F9FC")
    draw = ImageDraw.Draw(im)
    draw.text((MAP_X, 20), "RHCR | Lifelong Multi-Agent Path Finding", font=load_font(24, True), fill="#1A2636")
    draw.text((MAP_X, 53), "Warehouse KIVA map  |  darker squares: shelves  |  circles: robots", font=load_font(12), fill="#536476")
    for r, line in enumerate(grid):
        for c, ch in enumerate(line):
            col = {"@": "#344253", "r": "#D7E8FA", "e": "#FDE7B8"}.get(ch, "#FFFFFF")
            x0 = MAP_X + c * TILE
            y0 = MAP_Y + r * TILE
            draw.rectangle((x0, y0, x0 + TILE - 1, y0 + TILE - 1), fill=col, outline="#D7DCE4")
    return im


def box_text(draw, x, y, title, body):
    draw.text((x, y), title, font=load_font(13, True), fill="#1B3049")
    draw.text((x, y+24), body, font=load_font(15), fill="#516477")


def render_frame(base, grid, paths, t, horizon, title, *, trail=12, overview=False):
    im = base.copy()
    dr = ImageDraw.Draw(im)
    w = len(grid[0]); xpanel = MAP_X + w * TILE + PANEL_GAP
    dr.rectangle((xpanel-7, MAP_Y, im.width-31, im.height-45), fill="#FFFFFF", outline="#E5EAF0", width=1)
    dr.text((xpanel+13, MAP_Y+16), title, font=load_font(17, True), fill="#172537")
    dr.line((xpanel+13, MAP_Y+54, im.width-50, MAP_Y+54), fill="#E1E7F0", width=2)
    box_text(dr, xpanel+13, MAP_Y+72, "ROBOTS", str(len(paths)))
    box_text(dr, xpanel+13, MAP_Y+132, "STEP", f"{t:03d} / {horizon:03d}")
    box_text(dr, xpanel+13, MAP_Y+192, "MAP", f"{len(grid)} x {len(grid[0])}")
    dr.text((xpanel+13, MAP_Y+265), "Robot IDs", font=load_font(13, True), fill="#1B3049")
    for i in range(len(paths)):
        sy = MAP_Y + 295 + i*26
        dr.ellipse((xpanel+13, sy, xpanel+26, sy+13), fill=PALETTE[i % len(PALETTE)])
        dr.text((xpanel+35, sy-2), f"Agent {i}", font=load_font(12), fill="#263344")
    dr.text((MAP_X, im.height-42), "Recorded execution positions. Not a collision/safety certificate.", font=load_font(12), fill="#637589")

    for i, path in enumerate(paths):
        c = PALETTE[i % len(PALETTE)]
        start = 0 if overview else max(0, t-trail)
        points = [xy(path[j][0], w) for j in range(start, t+1)]
        if len(points) >= 2:
            dr.line(points, fill=c, width=3 if overview else 2, joint="curve")
    for i, path in enumerate(paths):
        if overview:
            a = xy(path[0][0], w)
            dr.rectangle((a[0]-5, a[1]-5, a[0]+5,a[1]+5), fill="#FFFFFF", outline=PALETTE[i % len(PALETTE)], width=2)
        px, py = xy(path[t][0], w)
        c = PALETTE[i % len(PALETTE)]
        dr.ellipse((px-10, py-10, px+10, py+10), fill=c, outline="#FFFFFF", width=2)
        num = str(i)
        bbox=dr.textbbox((0, 0),num,font=load_font(11, True))
        dr.text((px-(bbox[2]-bbox[0])/2,py-(bbox[3]-bbox[1])/2-bbox[1]),num,font=load_font(11, True),fill="white")
    progress_y = im.height - 18
    dr.rectangle((MAP_X, progress_y, MAP_X + w*TILE, progress_y+7), fill="#D8E0EA")
    dr.rectangle((MAP_X, progress_y, MAP_X + int(w*TILE*(t/max(1,horizon))), progress_y+7), fill="#64748B")
    return im


def main(argv=None):
    ap=argparse.ArgumentParser(description="RHCR trajectories to PNG and animated GIF")
    ap.add_argument("--map", required=True, type=Path, help="Official RHCR KIVA .map")
    ap.add_argument("--paths", required=True, type=Path, help="Saved RHCR paths.txt")
    ap.add_argument("--title", default="PBS + SIPP | Seed 0")
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    ap.add_argument("--fps", type=int, default=8)
    ap.add_argument("--frame-step", type=int, default=1, help="Use 2 to make a smaller/faster GIF")
    opts=ap.parse_args(argv)
    if not (1 <= opts.fps <= 30 and 1 <= opts.frame_step <= 20):
        ap.error("fps must be 1..30 and frame-step 1..20")
    grid=read_rhcr_map(opts.map)
    paths,horizon=read_rhcr_paths(opts.paths,grid)
    opts.out.mkdir(parents=True, exist_ok=True)
    base=board(grid)
    snap=render_frame(base,grid,paths,horizon,horizon,opts.title,overview=True)
    snap.save(opts.out / "trajectories.png")
    ts=list(range(0,horizon+1,opts.frame_step))
    if ts[-1] != horizon: ts.append(horizon)
    frames=[render_frame(base,grid,paths,t,horizon,opts.title).quantize(colors=128) for t in ts]
    out=opts.out / "animation.gif"
    frames[0].save(out,save_all=True,append_images=frames[1:],duration=round(1000/opts.fps),loop=0,optimize=True,disposal=2)
    print(f"OK: {len(paths)} robots, {horizon} steps, {len(frames)} animation frames")
    print(f"Figure: {opts.out / 'trajectories.png'}")
    print(f"Animation: {out}")


if __name__ == "__main__":
    main()
