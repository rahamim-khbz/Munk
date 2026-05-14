import os

def test_spa_output():
    output_path = "Munk Viewer.html"
    assert os.path.exists(output_path), f"Master output file {output_path} not found"
    
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for column selectors bar
    assert 'class="column-selectors-bar"' in content, "Column selectors bar missing"
    assert 'data-col1' in content and 'data-col2' in content, "data-col1/data-col2 attributes missing"
    
    # Check for dynamic visibility CSS rules
    assert 'data-col1="en"' in content, "Dynamic visibility rules for col1 missing"
    assert 'data-col2="makbili"' in content, "Dynamic visibility rules for col2 missing"
    
    # Check for subheading underline styles
    assert 'border-bottom:' in content or 'mediumGrey' in content, "Subheading underline styles missing"
    
    # Check for responsive mobile vertical stacking viewport override
    assert '@media (max-width: 768px)' in content, "Mobile stacking viewport overrides missing"
    
    # Check for section-based hidden chapters
    assert 'class="chapter-section"' in content, "Chapter sections missing"

if __name__ == "__main__":
    test_spa_output()
