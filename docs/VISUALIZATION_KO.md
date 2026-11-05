# RHCR Visualizations (seed 0)

This is an independent visualization/plot add-on for the official RHCR repository (not LoRR/PlanViz).
Official origin: https://github.com/Jiaoyang-Li/RHCR

The official RHCR repository has no ready-to-run counterpart of LoRR PlanViz. Its BasicSystem.cpp writes `paths.txt` as n agents followed by one line per agent, with states in `location,orientation,timestep;` form (confirmed against States.cpp). Its KIVA .map has 4 header lines (size, endpoint count, home-station count, max time) followed by ASCII grid lines. These scripts render these saved artifacts without rerunning the simulator.

## Windows instructions

1. Extract this ZIP *into* `%USERPROFILE%\projects\rhcr-benchmark` preserving `scripts/` and `docs/`. It should NOT be extracted into `rhcr-official`.
2. In Anaconda Prompt (the existing `lorr-viz` environment already has Pillow & matplotlib):

```bat
conda activate lorr-viz
cd %USERPROFILE%\projects\rhcr-benchmark
python -m pip install -r requirements-viz.txt
python scripts\plot_comparison.py --csv summary_seed0.csv --out figures\comparison_seed0
python scripts\visualize_rhcr.py --map "%USERPROFILE%\projects\rhcr-official\maps\kiva.map" --paths results\pbs_sipp_seed0\paths.txt --title "PBS + SIPP | Seed 0" --out figures\pbs_sipp_seed0
```

To render the other two:

```bat
python scripts\visualize_rhcr.py --map "%USERPROFILE%\projects\rhcr-official\maps\kiva.map" --paths results\pbs_astar_seed0\paths.txt --title "PBS + A* | Seed 0" --out figures\pbs_astar_seed0
python scripts\visualize_rhcr.py --map "%USERPROFILE%\projects\rhcr-official\maps\kiva.map" --paths results\ecbs_sipp_seed0\paths.txt --title "ECBS + SIPP | Seed 0" --out figures\ecbs_sipp_seed0
```

## Output

- `figures/comparison_seed0/completed_goals.png`, `mean_planning_time_ms.png`, `max_planning_time_ms.png`
- `figures/pbs_sipp_seed0/trajectories.png` and `animation.gif` (similarly for each method)

Animated GIF is an animated image and can be opened in a browser. For a conventional MP4 for presentations, you can screen-record the animation with Snipping Tool or convert GIF using FFmpeg (`ffmpeg -i animation.gif -movflags +faststart -pix_fmt yuv420p animation.mp4`) if installed. Some FFmpeg builds need an even-sized frame, which the renderer uses.

## Meaning/limitations

- These are the **recorded** executed positions, not real robot dynamics and not a 3D simulation.
- The figures show **seed 0 only**; difference is not a statistically validated performance result.
- `Goals` are RHCR KIVA goal visits, not LoRR MAPD two-errand task completions.
- The existing `config.txt` omits low-level choice and ECBS suboptimal bound. Preserve command lines separately in README when publishing.
- `paths.txt` file states are expected to have consecutive timestamps 0,1,...,H for every agent; script explicitly validates rather than silently inventing missing steps.
- To analyze waiting and deadlock rigorously, additional metrics and validation are required; this visualization alone is not evidence of freedom from deadlocks.
