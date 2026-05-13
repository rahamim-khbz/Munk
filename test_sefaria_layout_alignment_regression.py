import os
import re

def test_sefaria_layout_alignment_regression():
    """
    Regression test verifying that generated Sefaria native parallel layout pages
    maintain pure 1:1 block level alignment without cell splitting anomalies.
    """
    directory = "viewer_sefaria_part1"
    assert os.path.exists(directory), f"Target directory {directory} missing"
    
    files = [f for f in os.listdir(directory) if f.endswith('.html') and f != 'index.html']
    assert len(files) > 0, "No generated chapter files found for testing"
    
    total_rows_checked = 0
    for filename in files:
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
            content = f.read()
            
        # Count rows
        rows = content.split('<div class="parallel-row"')
        for row in rows[1:]:
            total_rows_checked += 1
            he_cells = re.findall(r'<div class="he-cell">', row)
            en_cells = re.findall(r'<div class="en-cell">', row)
            
            # Assert exact 1:1 structural grid setup inside every single row
            assert len(he_cells) == 1, f"File {filename} row contains {len(he_cells)} he-cells instead of exactly 1"
            assert len(en_cells) == 1, f"File {filename} row contains {len(en_cells)} en-cells instead of exactly 1"
            
    print(f"Regression verification complete: {total_rows_checked} individual parallel rows across {len(files)} files strictly adhere to 1:1 layout parity.")

if __name__ == "__main__":
    test_sefaria_layout_alignment_regression()
