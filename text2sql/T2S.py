### Code


# ---------------------------------------------
# ✅ STEP 0: Install Required Packages
# ---------------------------------------------

!pip install -q transformers accelerate
!pip install -q transformers datasets peft accelerate bitsandbytes sentencepiece
!pip install -U bitsandbytes

# ---------------------------------------------
# ✅ STEP 1: Load Base Model in 4-bit (bnb)
# ---------------------------------------------
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

model_id = "XGenerationLab/XiYanSQL-QwenCoder-3B-2504"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=bnb_config
)


# ---------------------------------------------
# ✅ STEP 2: Apply QLoRA with PEFT
# ---------------------------------------------
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # adjust for your model architecture
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ---------------------------------------------
# ✅ STEP 3: Load Processed Complex Spider Prompts
# ---------------------------------------------
import json

with open("/content/complex_spider_train.json") as f:
    train_data = json.load(f)

from datasets import Dataset

train_dataset = Dataset.from_list(train_data)

# ---------------------------------------------
# ✅ STEP 4: Tokenize the Prompts
# ---------------------------------------------
def tokenize(example):
    return tokenizer(
        example["prompt"],
        truncation=True,
        padding="max_length",
        max_length=1024
    )

train_dataset = train_dataset.map(tokenize, batched=True)

# ---------------------------------------------
# ✅ STEP 5: Set TrainingArguments
# ---------------------------------------------
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="/content/qwen-sql-qlora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    logging_steps=10,
    learning_rate=2e-4,
    bf16=False,
    fp16=True,
    save_strategy="epoch",
    report_to="none"
)

# ---------------------------------------------
# ✅ STEP 6: Define Trainer with SQL Accuracy Metrics
# ---------------------------------------------
from transformers import Trainer

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    # Optional: implement SQL-specific metrics later (exec match, etc.)
    return {}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# ---------------------------------------------
# ✅ STEP 7: Train the Model
# ---------------------------------------------
trainer.train()

# ---------------------------------------------
# ✅ STEP 8: Save LoRA-Only Adapter
# ---------------------------------------------
model.save_pretrained("/content/xi-yan-sql-lora-adapter")
tokenizer.save_pretrained("/content/xi-yan-sql-lora-adapter")

print("✅ Training complete. Adapter saved.")
