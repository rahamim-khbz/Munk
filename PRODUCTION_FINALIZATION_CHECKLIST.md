# Production Finalization Checklist: Munk Guide Corpus

Follow these steps in exact order to produce the finalized "Gold Standard" corpus.

## Phase 1: Data Completion
- [ ] **Complete Footnote Pass**: Wait for `gemini_rehab_finisher.py` to hit 100% (4,027 total).
- [ ] **Complete Main Text Rehab**: Run `python3 groq_main_text_rehab.py` to fix the 157 low-ratio segments identified in the audit.

## Phase 2: Scholarly Refinement
- [ ] **Mandatory Archaic Cleanup**: Run `python3 fix_archaic_forms.py` one final time.
    - *Purpose*: Removes residual `-eth` endings and archaic adverbs (forsooth, howbeit, peradventure) from the latest Gemini batches.
- [ ] **Verification Audit**: Run `python3 verify_word_counts.py` on the final checkpoints.
    - *Success Metric*: Zero substantive segments below 85% word-count ratio.

## Phase 3: Production Merger
- [ ] **Run Merger**: Execute `python3 merge_production_json.py`.
    - *Output*: Consolidated JSON with re-woven HTML tags.
- [ ] **Viewer Validation**: Open `munk_makbili_viewer.html` and check:
    - Hebrew/Arabic script rendering.
    - Footnote popup functionality.
    - Table of Contents chapter alignment.

## Phase 4: Workspace Cleanup
- [ ] **Archive**: Move all `groq_*`, `gemini_*`, and intermediate `checkpoint_*` files to `archive/`.
- [ ] **Final Backup**: Zip the final JSON corpus and the Viewer.
