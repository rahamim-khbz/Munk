# Munk Footnote Pipeline: Post-Mortem & Robustness Analysis

## Why the Parallel Pipeline Approach Won
The transition from a synchronous, recursive "rehab" script to the parallel, surgical-splitting pipeline was necessitated by the "Death Spiral" problem common in LLM batch processing.

### 1. Pre-emptive Failure Detection (Surgical Timeouts)
In the synchronous version, a single hung network request or a "stuck" LLM generation would block the entire pipeline. The parallel pipeline uses a non-blocking `wait` loop that monitors the `start_time` of every active thread. By setting a hard 180s threshold, we can cancel and split stalled tasks *before* they consume the entire worker pool or cause a timeout exception.

### 2. Isolation of "Poisonous" Footnotes
Some footnotes contain complex multilingual content (Latin, Hebrew, and French combined) that causes the LLM to hallucinate JSON structures or truncate its output. Parallelism isolates these failures. While one thread handles the complex splitting of a "poison" footnote, other threads continue processing easy batches, maintaining high throughput.

### 3. Non-Recursive Recovery
Recursion in LLM workflows is dangerous because it hides the state of the failure. The pipeline approach uses a flattened task queue (the pool). When a batch fails alignment, it is sliced into two discrete tasks and re-submitted to the pool as first-class citizens. This makes the "Progressive Chunk Slicing" (PCS) strategy much easier to log, debug, and monitor.

### 4. The Gemini Context Advantage (`munk_pipeline_gemini.py`)
While Groq provided raw throughput for the main text, the footnote track was stabilized by the transition to **Gemini 3 Flash Preview** with **Explicit Context Caching**.

- **Scholarly Persona Caching:** By using the `client.caches.create` method, we locked Munk's specific 19th-century scholarly persona and glossary into the model's active memory. This reduced "instruction drift" and ensured that technical terms like *hypostasis* or *intellect* were translated with perfect consistency across 4,000+ notes.
- **Dynamic Character-Based Chunking:** Unlike static batch sizes, the Gemini pipeline used a `dynamic_chunk_dictionary` that aimed for a ~12,000 character "Goldilocks" window. This allowed the model to process 20–30 short notes or 1–2 massive notes in a single request, maximizing token value without hitting the response limit.
- **Tag-Weaving Integration:** The script successfully re-wove `[[t:N]]` markers back into the translation, proving that complex structural preservation is possible even with long-context windows.

This transition was the strategic turning point for the project. While the Groq/Llama-3 architecture was exceptional for the main text's sheer volume, the scholarly complexity and multilingual density of Munk’s footnotes required the "high-IQ" context handling and native JSON output stability that only the Gemini-3-Flash architecture provided.

---

## LLM-to-LLM Engineering Brief
*For future AI agents implementing large-scale JSON translation pipelines.*

### SYSTEM ARCHITECTURE: Progressive Chunk Slicing (PCS)

**Core Objective:** Maintain 100% data integrity and key-value alignment when translating $N$ discrete objects via an LLM.

**Protocol Guidelines:**
1. **Atoms over Streams:** Do not stream large amounts of text. Flatten the JSON into $K$ small, state-independent batches.
2. **The "Goldilocks" Batch Size:** Aim for 3,000–4,500 characters per request. This maximizes token efficiency while staying well within the LLM's "Stable Reasoning Window" for JSON output.
3. **Strict Alignment Validation:** Implement a `len(input_keys) == len(output_keys)` gate immediately after parsing. If the LLM merges two footnotes or drops one, discard the result immediately.
4. **Concurrency Monitoring (The Heartbeat Loop):**
   - Use a `ThreadPoolExecutor` (not `ProcessPoolExecutor` for I/O bound tasks).
   - Implement a polling loop (`wait(timeout=5)`) instead of blocking `as_completed`.
   - **Protocol:** If `currentTime - startTime > T_max`, cancel future, slice chunk in half, and re-queue.
5. **JSON Repair Shims:** LLMs frequently truncate JSON when hitting complexity walls. Use regex-based recovery (closing unclosed quotes/brackets) to salvage partially successful translations before resorting to a split.
6. **Stateless Resumption:** Use a flat JSON checkpoint file. Read `done_ids` on boot and filter the global `todo_list`. This prevents redundant API costs.

### Error Handling Hierarchy:
1. **Retry:** For transient network/rate-limit errors.
2. **Repair:** For simple JSON syntax errors (truncated endings).
3. **Surgical Split:** For alignment errors or generation timeouts.
4. **Log & Skip:** Only for single-item failures that persist after 5+ splits/retries.
