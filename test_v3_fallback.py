
from unittest.mock import MagicMock, patch
from munk_pipeline_v3 import translate_worker
import json

def test_surgical_fallback():
    # Mock the client to fail on large batches but succeed on smaller ones
    with patch('munk_pipeline_v3.client') as mock_client:
        def side_effect(model, contents, config):
            # Parse the content to see how many items are in the chunk
            # The structure is "TRANSLATE THESE SEGMENTS:\n{json_data}"
            json_str = contents.split('\n', 1)[1]
            data = json.loads(json_str)
            if len(data) > 1:
                raise Exception("Chunk too big!")
            # Return a valid response for single items
            mock_res = MagicMock()
            # Return the same key with "translated" text
            mock_res.text = json.dumps({list(data.keys())[0]: "translated"})
            return mock_res

        mock_client.models.generate_content.side_effect = side_effect
        
        chunk = {"p.1": "F1", "p.2": "F2"}
        result = translate_worker(chunk)
        
        print(f"Result: {result}")
        assert result == {"p.1": "translated", "p.2": "translated"}
        print("test_surgical_fallback passed!")

if __name__ == "__main__":
    test_surgical_fallback()
