from fastapi import FastAPI, HTTPException
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List
import google.generativeai as genai
import json
import time
import seaborn as sns
import pandas as pd

genai.configure(api_key="AIzaSyCDSadSw6oKpiEZ_-446p3Ngn8n90I8aXs")
model = genai.GenerativeModel("gemini-1.5-flash")

def load_jsonl_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

training_data = load_jsonl_data("jsonl file name")
base_model = 'models/gemini-1.5-flash-001-tuning'

operation = genai.create_tuned_model(
    display_name = "Mercury",
    source_model = base_model,
    epoch_count = 10,
    batch_size =2,
    learning_rate = 0.0001,
    training_data = training_data,
    input_key = 'query',
    output_key = 'response'
)
for status in operation.wait_bar():
    time.sleep(10)

result = operation.result()
print(result)

model = genai.GenerativeModel(model_name='tunedModels name')

snapshots = pd.DataFrame(result.tuning_task.snapshots)
sns.lineplot(data=snapshots, x='epoch', y='mean_loss')

def generate_response(prompt):
    model = genai.GenerativeModel(model_name = result.name)
    response = model.generate_content(prompt)
    return response.text

generate_response('text')