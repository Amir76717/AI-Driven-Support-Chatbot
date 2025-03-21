# src/model/finetune_gpt.py
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def prepare_fine_tuning_data(input_file, output_file):
    with open(input_file, 'r') as f:
        qa_pairs = json.load(f)
    
    fine_tuning_data = []
    for pair in qa_pairs:
        fine_tuning_data.append({
            "messages": [
                {"role": "system", "content": "You are a helpful customer support assistant."},
                {"role": "user", "content": pair["input"]},
                {"role": "assistant", "content": pair["output"]}
            ]
        })
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        for item in fine_tuning_data:
            f.write(json.dumps(item) + '\n')

def create_fine_tuned_model():
    # Upload the prepared file
    with open("data/processed/fine_tuning.jsonl", "rb") as f:
        response = openai.File.create(
            file=f,
            purpose="fine-tune"
        )
    file_id = response.id
    
    # Create fine-tuning job
    response = openai.FineTuningJob.create(
        training_file=file_id,
        model="gpt-3.5-turbo"
    )
    job_id = response.id
    
    print(f"Fine-tuning job created with ID: {job_id}")
    return job_id

if __name__ == "__main__":
    prepare_fine_tuning_data('data/processed/qa_pairs.json', 'data/processed/fine_tuning.jsonl')
    job_id = create_fine_tuned_model()