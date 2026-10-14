#!/usr/bin/env python3
"""
scripts/setup_subagents.py - Helper to load and inspect translator and verifier subagent prompts.
"""

import os
from typing import Dict

def get_subagent_prompts(base_dir: str = None) -> Dict[str, str]:
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompts_dir = os.path.join(base_dir, "docs", "prompts")
    
    translator_path = os.path.join(prompts_dir, "munk_translator_prompt.md")
    verifier_path = os.path.join(prompts_dir, "munk_verifier_prompt.md")
    
    with open(translator_path, "r", encoding="utf-8") as f:
        translator_prompt = f.read()
    with open(verifier_path, "r", encoding="utf-8") as f:
        verifier_prompt = f.read()
        
    return {
        "munk-translator": translator_prompt,
        "munk-verifier": verifier_prompt
    }

if __name__ == "__main__":
    prompts = get_subagent_prompts()
    print("Loaded subagent roles:")
    for role, text in prompts.items():
        print(f"  - {role} ({len(text)} chars)")
