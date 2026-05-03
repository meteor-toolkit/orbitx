"""orbitx.utils._matchups.animate_matchups - animation of satellite matchups"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from orbitx.deps import lazy_cartopy
from orbitx.utils._constants import CM

if TYPE_CHECKING:
    from orbitx.matchups import Matchups


def animate_matchups(
    matchups: "Matchups",
    trail_length: int = 15,
    step: int = 6,
    interval: Optional[int] = None,
    projection=None,
    start_time: Optional[np.datetime64] = None,
    end_time: Optional[np.datetime64] = None,
    duration: Optional[float] = None,
    lat_limit: Optional[float] = None,
    show_events: bool = True,
):
    """Animate satellite orbits with progressive matchup discovery.

    :param matchups: The Matchups object to animate.
    :param trail_length: Trailing orbit positions shown per satellite. Defaults to 15.
    :param step: Subsample every N orbit time steps (higher = faster playback). Defaults to 6.
    :param interval: Milliseconds between frames. Mutually exclusive with ``duration``. Defaults to 50 ms if neither is given.
    :param projection: Cartopy projection. Defaults to ``ccrs.PlateCarree()``.
    :param start_time: Start of the animated time window. Defaults to the start of the orbit.
    :param end_time: End of the animated time window. Defaults to the end of the orbit.
    :param duration: Desired total video length in seconds. Mutually exclusive with ``interval``.
    :param lat_limit: If given, the map is clipped symmetrically to ±``lat_limit`` degrees latitude, trimming the poles from view.
    :param show_events: Whether to draw event bounding boxes when their stop time is reached. Defaults to True.
    :return: Call ``.save()`` to export or display inline in a notebook with ``IPython.display.HTML(anim.to_jshtml())``.
    :rtype: matplotlib.animation.FuncAnimation
    """
    from matplotlib.animation import FuncAnimation
    ccrs, cfeature = lazy_cartopy()

    if duration is not None and interval is not None:
        raise ValueError("Specify either 'duration' or 'interval', not both.")

    if projection is None:
        projection = ccrs.PlateCarree()

    orbit = matchups.orbit
    orbit_times = orbit.orbits["time_datetime"].values   # (time,)
    orbit_lats = orbit.orbits["lat"].values              # (time, satellite)
    orbit_lons = orbit.orbits["lon"].values
    n_sats = orbit_lats.shape[1]

    # Restrict to the requested time window
    time_mask = np.ones(len(orbit_times), dtype=bool)
    if start_time is not None:
        time_mask &= orbit_times >= start_time
    if end_time is not None:
        time_mask &= orbit_times <= end_time
    valid_indices = np.where(time_mask)[0]
    if len(valid_indices) == 0:
        raise ValueError(
            "No orbit time points fall within the requested start_time/end_time window."
        )

    events = matchups.events

    # Per-satellite sets of matchup times for trail darkening
    matchup_time_sets = []
    for sat_i in range(n_sats):
        sat_name = orbit.satellite_shortname[sat_i]
        if sat_name in matchups.matchups["satellite"].values:
            mt = set(
                matchups.matchups["time_datetime"]
                .sel(satellite=sat_name)
                .values.tolist()
            )
        else:
            mt = set()
        matchup_time_sets.append(mt)

    fig = plt.figure(figsize=(16 * CM, 9 * CM), dpi=150)
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax.coastlines(linewidth=0.4)
    ax.add_feature(cfeature.LAND, facecolor="lightgrey")
    if lat_limit is not None:
        ax.set_extent([-180, 180, -lat_limit, lat_limit], crs=ccrs.PlateCarree())
    else:
        ax.set_global()

    sat_colors = [plt.cm.tab10(i) for i in range(n_sats)]

    # Fading trail — updated every frame
    trail_artists = [
        ax.scatter([], [], s=20, transform=ccrs.PlateCarree(), zorder=5)
        for _ in range(n_sats)
    ]
    # Persistent matchup dots — accumulate as the animation progresses
    matchup_dot_artists = [
        ax.scatter(
            [], [], s=20, transform=ccrs.PlateCarree(), zorder=6,
            color=tuple(c * 0.4 for c in sat_colors[i][:3]),
            edgecolors="none",
        )
        for i in range(n_sats)
    ]
    # Current-position dot — updated every frame
    head_artists = [
        ax.scatter(
            [], [], s=60, color=sat_colors[i],
            transform=ccrs.PlateCarree(), zorder=7,
            edgecolors="white", linewidths=0.5,
        )
        for i in range(n_sats)
    ]

    # Precompute orbit indices that are matchup positions, per satellite
    matchup_orbit_indices = []
    for sat_i in range(n_sats):
        indices = np.array(
            [ti for ti in range(len(orbit_times))
             if orbit_times[ti].item() in matchup_time_sets[sat_i]],
            dtype=int,
        )
        matchup_orbit_indices.append(indices)

    ax.legend(
        handles=[
            Line2D(
                [0], [0], marker="o", color="w",
                markerfacecolor=sat_colors[i], markersize=6,
                label=orbit.satellite_name[i],
            )
            for i in range(n_sats)
        ],
        loc="lower right",
        fontsize=5,
    )

    time_text = ax.text(
        0.01, 0.99, "", transform=ax.transAxes, fontsize=5, va="top",
        color="white",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.6),
    )

    # Pre-create event bounding box outlines, hidden (alpha=0) until their stop_time.
    # Outline-only (no fill) so points are never obscured; Line2D respects zorder reliably.
    event_patches = []
    if show_events:
        for event in events:
            if not event["crosses_antimeridian"]:
                min_lon, min_lat, max_lon, max_lat = event["bbox"]
                line, = ax.plot(
                    [min_lon, max_lon, max_lon, min_lon, min_lon],
                    [min_lat, min_lat, max_lat, max_lat, min_lat],
                    transform=ccrs.PlateCarree(),
                    color="grey", linewidth=1.5, alpha=0, zorder=8,
                )
                event_patches.append(line)
            else:
                event_patches.append(None)

    seen_events: set = set()

    def update(frame_i):
        for sat_i in range(n_sats):
            start = max(0, frame_i - trail_length)
            t_lons = orbit_lons[start:frame_i, sat_i]
            t_lats = orbit_lats[start:frame_i, sat_i]
            if len(t_lons) > 0:
                trail_times = orbit_times[start:frame_i]
                is_matchup = np.array(
                    [t.item() in matchup_time_sets[sat_i] for t in trail_times]
                )
                base_rgb = np.array(sat_colors[sat_i][:3])
                colors_rgb = np.where(
                    is_matchup[:, None], base_rgb * 0.4, base_rgb
                )
                normal_alphas = np.linspace(0.05, 0.55, len(t_lons))
                alphas = np.where(is_matchup, 0.9, normal_alphas)
                sizes = np.where(is_matchup, 25.0, np.linspace(3, 18, len(t_lons)))
                rgba = np.column_stack([colors_rgb, alphas])
                trail_artists[sat_i].set_offsets(np.c_[t_lons, t_lats])
                trail_artists[sat_i].set_facecolor(rgba)
                trail_artists[sat_i].set_sizes(sizes)
                trail_artists[sat_i].set_edgecolor("none")
            head_artists[sat_i].set_offsets(
                [[orbit_lons[frame_i, sat_i], orbit_lats[frame_i, sat_i]]]
            )

            # Update persistent matchup dots for all positions reached so far
            mi = matchup_orbit_indices[sat_i]
            visible = mi[mi <= frame_i]
            if len(visible) > 0:
                matchup_dot_artists[sat_i].set_offsets(
                    np.c_[orbit_lons[visible, sat_i], orbit_lats[visible, sat_i]]
                )
                matchup_dot_artists[sat_i].set_sizes(np.full(len(visible), 20.0))

        current_time = orbit_times[frame_i]
        time_text.set_text(str(current_time)[:16].replace("T", "  "))

        # Reveal event boxes once their stop_time is reached
        if show_events:
            for ei, event in enumerate(events):
                if ei not in seen_events and event["stop_time"] <= current_time:
                    seen_events.add(ei)
                    if event_patches[ei] is not None:
                        event_patches[ei].set_alpha(1.0)

    frames = valid_indices[::step]
    if duration is not None:
        computed_interval = max(10, int(duration * 1000 / len(frames)))
    else:
        computed_interval = interval if interval is not None else 50

    return FuncAnimation(
        fig, update,
        frames=frames,
        interval=computed_interval,
        blit=False,
    )


if __name__ == "__main__":
    pass
