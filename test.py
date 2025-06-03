# 1. Import the Library
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 2. Set the model name
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

# 3. Download and Save the model and tokenizer locally
local_model_path = "./deepseek_r1_model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

# 4. Save the model and tokenizer in the local path
tokenizer.save_pretrained(local_model_path)
model.save_pretrained(local_model_path)

# 5. Print the Model and tokenizer
print(f"Model and tokenizer saved to {local_model_path}")
