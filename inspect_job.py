import os
import json
from dotenv import load_dotenv
from google import genai
load_dotenv()

client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

BATCH_JOB_FILE = 'batch_job_status.json'
if os.path.exists(BATCH_JOB_FILE):
    with open(BATCH_JOB_FILE, 'r') as f:
        job_info = json.load(f)
    job_name = job_info['job_name']
    job = client.batches.get(name=job_name)
    # Use model_dump to see all fields
    print(json.dumps(job.model_dump(exclude_none=True), indent=2, default=str))
else:
    print("No job file found.")
