import os

def test_spa_output():
    output_path = "Munk Viewer.html"
    assert os.path.exists(output_path), f"Master output file {output_path} not found"
    
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for container data attributes
    assert 'data-left-col="en"' in content, "data-left-col attribute missing"
    assert 'data-right-col="makbili"' in content, "data-right-col attribute missing"
    
    # Check for TOC drawer column layout panel integration
    assert 'id="select-left-col"' in content and 'id="select-right-col"' in content, "Left/Right column dropdowns missing"
    
    # Check for new symmetrical cell wrapper classes
    assert 'class="left-cell"' in content and 'class="right-cell"' in content, "Symmetrical cell containers missing"
    
    # Check for pure CSS visibility rules targeting left/right cell spans
    assert '.left-cell .variant-en' in content, "Pure CSS visibility rules for variant-en missing"
    assert '.right-cell .variant-makbili' in content, "Pure CSS visibility rules for variant-makbili missing"
    
    # Check for JS mutual exclusion coordination function
    assert 'function updateColumnSelectors()' in content, "updateColumnSelectors JS logic missing"
    
    # Check for responsive mobile vertical stacking viewport override with soft divider
    assert '@media (max-width: 768px)' in content, "Mobile stacking viewport overrides missing"
    assert '.right-cell {' in content and 'border-top:' in content, "Mobile view right-cell soft line divider rule missing"

if __name__ == "__main__":
    test_spa_output()
