# HDMI compatibility patches (MuJoCo-Warp 3.11)

This branch starts at upstream `dbc52e3ea69a63e14026e969cb055e0c3c2f0c83`
and carries the backend changes used by HDMI's Weave training and playback:

- Filter absent mesh variants in both NxN and SAP broad phase, while retaining
  primitive geoms whose mesh ID is normally -1.
- Opt-in bounded CCD thread scratch storage and reuse. Set
  `HDMI_CCD_THREAD_SCRATCH=1` **before importing MuJoCo-Warp**. The default path
  remains upstream behavior.

The branch pins stable MuJoCo 3.11.0 and Warp 1.14.0, and removes the upstream
nightly-only package sources. Its development lockfile also uses those stable
releases. Consumers should pin this Git commit in their project dependencies.

Validation: eight missing-mesh cases plus one mesh-mesh scratch equivalence
case on CPU; HDMI additionally exercises the enabled path on GPU. This is not
an assertion that the full upstream test suite passed. The upstream pre-commit
kernel-analyzer entry references an absent contrib script in this base revision;
that unavailable hook is skipped, while Ruff and formatting checks run.
