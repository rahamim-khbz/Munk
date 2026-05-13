import os
import re

def test_paragraph_splitting_alignment():
    """
    Regression test to ensure that when a Hebrew segment contains multiple inline headers
    (mediumGrey spans), the continuous English translation string is proportionally distributed
    across all resulting sub-blocks rather than dumped entirely into the single longest block.
    """
    target_file = os.path.join("viewer", "Part-2---Chapter-42.html")
    assert os.path.exists(target_file), f"{target_file} not found!"

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all parallel rows belonging to root.text.Part 2..41.2
    # This segment contains Jacob's wrestling, Balaam's ass, Joshua's angel, and the angel from Gilgal.
    matches = re.findall(
        r'<div class="parallel-row"\s+id="row-root\.text\.Part 2\.\.41\.2">\s*<div class="he-cell">.*?</div>\s*<div class="en-cell">(.*?)</div>',
        content,
        re.DOTALL
    )

    assert len(matches) > 0, "No rows found for target segment root.text.Part 2..41.2!"
    
    empty_cells = [i for i, cell in enumerate(matches) if not cell.strip()]
    assert len(empty_cells) == 0, f"Found empty English translation cells for sub-blocks at indices {empty_cells}!"

    print("Regression test passed: English translation is successfully distributed across all sub-blocks.")

if __name__ == "__main__":
    test_paragraph_splitting_alignment()
