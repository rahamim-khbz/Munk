import os

def test_chunked_segment_recombination():
    """
    Regression test to ensure that chunked translation segments (e.g., .sub_0, .sub_1)
    are properly recombined during viewer generation, and do not show up as
    '[Translation Missing]' in the generated HTML.
    """
    # 1. Check fulltext.html
    fulltext_path = os.path.join("viewer", "fulltext.html")
    assert os.path.exists(fulltext_path), "fulltext.html not found!"
    
    with open(fulltext_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    missing_count = html_content.count("[Translation Missing]")
    assert missing_count == 0, f"Found {missing_count} occurrences of '[Translation Missing]' in fulltext.html!"

    # 2. Check Part-1---Chapter-2.html specifically for the known bug
    ch2_path = os.path.join("viewer", "Part-1---Chapter-2.html")
    assert os.path.exists(ch2_path), "Part-1---Chapter-2.html not found!"
    
    with open(ch2_path, 'r', encoding='utf-8') as f:
        ch2_content = f.read()
        
    assert "[Translation Missing]" not in ch2_content, "Chapter 2 still contains missing translation!"
    
    print("Regression test passed: Chunked translation segments are successfully recombined.")

if __name__ == "__main__":
    test_chunked_segment_recombination()
