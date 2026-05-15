
import sys
import os

def test_flatten_simple():
    try:
        from munk_pipeline_v3 import extract_and_flatten
    except ImportError:
        print("ImportError: munk_pipeline_v3 not found (as expected)")
        return
    
    data = {"text": {"Part 1": ["Bonjour", "Monde"]}}
    flat, fns = extract_and_flatten(data)
    
    print(f"Flattened: {flat}")
    assert flat["root.text.Part 1.0"] == "Bonjour"
    assert flat["root.text.Part 1.1"] == "Monde"
    print("test_flatten_simple passed!")

def test_footnote_stripping():
    from munk_pipeline_v3 import extract_and_flatten
    data = {"text": {"Part 1": ["Text <i class=\"footnote\">FN content</i>"]}}
    flat, fns = extract_and_flatten(data)
    
    print(f"Flattened: {flat}")
    print(f"Footnotes: {fns}")
    assert flat["root.text.Part 1.0"] == "Text [[fn:0]]"
    assert fns["fn.0"] == "FN content"
    print("test_footnote_stripping passed!")

def test_chunking():
    from munk_pipeline_v3 import chunk_dictionary
    d = {f"key{i}": "a" * 1000 for i in range(20)}
    chunks = chunk_dictionary(d, max_chars_per_chunk=5000)
    print(f"Created {len(chunks)} chunks")
    assert len(chunks) > 1
    for chunk in chunks:
        size = sum(len(str(k)) + len(str(v)) for k, v in chunk.items())
        assert size <= 5000
    print("test_chunking passed!")

if __name__ == "__main__":
    test_flatten_simple()
    test_footnote_stripping()
    test_chunking()
