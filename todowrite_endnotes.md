# Subagent-Driven Development Task Tracker

## Plan: Munk's Endnotes Integration

- [x] **Task 1: Endnotes Structure Verification Setup**
  - [x] Write failing test `test_endnotes_structure.py`
  - [x] Verify test fails (RED)
  - [x] Commit verification script
- [x] **Task 2: Implement Endnotes Volume I Data File**
  - [x] Transcribe and merge 16 paired segments into `endnotes_vol1.json`
  - [x] Verify test asserts Vol 2 missing (Vol 1 passes)
  - [x] Commit `endnotes_vol1.json`
- [x] **Task 3: Implement Endnotes Volume II Data File**
  - [x] Transcribe and merge aligned segments into `endnotes_vol2.json`
  - [x] Verify test asserts Vol 3 missing (Vol 2 passes)
  - [x] Commit `endnotes_vol2.json`
- [x] **Task 4: Implement Endnotes Volume III Data File**
  - [x] Transcribe and merge aligned segments into `endnotes_vol3.json`
  - [x] Verify test passes completely (GREEN)
  - [x] Commit `endnotes_vol3.json`
- [x] **Task 5: Pipeline Integration & Table of Contents Rendering**
  - [x] Modify `build_full_viewer.py` to ingest files and inject TOC banner
  - [x] Execute site generator to produce multi-page static bundle
  - [x] Commit pipeline changes
