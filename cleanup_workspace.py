
import os
import shutil

def cleanup():
    print("=== Munk Workspace Optimization & Cleanup ===")
    
    # Define directories
    dirs = ["archive", "core_scripts", "docs/plans"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 1. Core Scripts (Keep in root or move to core_scripts)
    # We'll keep the main production tools in root for now as requested by user's terminal commands
    # but we will move obsolete/experimental ones to archive.
    
    to_archive = [
        "api_test.py", "check_first_batch.py", "cleanup_french.py", 
        "count_fn.py", "debug_fn_id.py", "debug_matches.py", 
        "diag.py", "diag2.py", "diag3.py", "diag_async.py", "diag_sync.py",
        "identify_fail.py", "inspect_job.py", "llama_rehab_test.py",
        "patch_batch_215.py", "patch_chapter_19.py", "pilot_groq_chapter2.py",
        "seed_checkpoint.py", "test_async_pipeline.py", "test_threaded_pipeline.py",
        "test_v3_fallback.py", "test_v3_flattener.py", "test_v3_reconstruction.py",
        "translate_maqbili.py", "validate_json_iterative.py", "verify_word_counts.py",
        "requests.jsonl"
    ]
    
    # Error files
    for f in os.listdir("."):
        if f.startswith("error_") and f.endswith(".json"):
            to_archive.append(f)
            
    print(f"  [Action] Archiving {len(to_archive)} experimental/obsolete files...")
    
    moved_count = 0
    for f in to_archive:
        if os.path.exists(f):
            try:
                shutil.move(f, os.path.join("archive", f))
                moved_count += 1
            except Exception as e:
                print(f"    [Error] Could not move {f}: {e}")
                
    print(f"  [Success] Moved {moved_count} files to archive/.")

if __name__ == "__main__":
    cleanup()
