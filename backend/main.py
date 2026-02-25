import os
import sys
import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Add current directory to sys.path to import config_loader
sys.path.append(os.path.dirname(__file__))
from config_loader import load_config

# --- Configuration ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT, "config.yaml")
config = load_config(CONFIG_PATH)

# Model paths (local checkpoints preferred, fallback to config model)
FORWARD_MODEL_PATH = os.environ.get("FORWARD_MODEL", os.path.join(ROOT, "outputs", "checkpoints", "t5-small-forward-ep5-lr3e4-64"))
REVERSE_MODEL_PATH = os.environ.get("REVERSE_MODEL", os.path.join(ROOT, "outputs", "checkpoints", "t5-small-reverse-ep5-lr3e4-64"))
FALLBACK_MODEL = config["model"]["name"]

# Global state to hold models and tokenizers
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models and tokenizers once at startup."""
    print("Loading models into memory...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load Forward Model (Slang -> English)
    try:
        path = FORWARD_MODEL_PATH if os.path.isdir(FORWARD_MODEL_PATH) else FALLBACK_MODEL
        models["forward"] = {
            "model": AutoModelForSeq2SeqLM.from_pretrained(path).to(device),
            "tokenizer": AutoTokenizer.from_pretrained(path)
        }
        print(f"Forward model loaded from {path}")
    except Exception as e:
        print(f"Error loading forward model: {e}")

    # Load Reverse Model (English -> Slang)
    try:
        path = REVERSE_MODEL_PATH if os.path.isdir(REVERSE_MODEL_PATH) else FALLBACK_MODEL
        models["reverse"] = {
            "model": AutoModelForSeq2SeqLM.from_pretrained(path).to(device),
            "tokenizer": AutoTokenizer.from_pretrained(path)
        }
        print(f"Reverse model loaded from {path}")
    except Exception as e:
        print(f"Error loading reverse model: {e}")

    yield
    # Cleanup
    models.clear()
    print("Models cleared from memory.")

app = FastAPI(
    title="Cross-Language Meme & Slang Translator API",
    description="Production-ready API for translating internet slang and Hinglish using fine-tuned T5 models.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Schemas ---
class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="The text to translate")
    direction: str = Field("forward", pattern="^(forward|reverse)$", description="Translation direction: 'forward' (Slang -> Std) or 'reverse' (Std -> Slang)")

class TranslationResponse(BaseModel):
    input_text: str
    translated_text: str
    direction: str
    model_used: str

# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API and model status."""
    return {
        "status": "healthy",
        "models_loaded": list(models.keys()),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Main translation endpoint."""
    if request.direction not in models:
        raise HTTPException(status_code=503, detail=f"Model for direction '{request.direction}' is not loaded.")

    model_data = models[request.direction]
    model = model_data["model"]
    tokenizer = model_data["tokenizer"]
    
    gen_cfg = config["generation"]
    model_cfg = config["model"]
    
    try:
        inputs = tokenizer(request.text, return_tensors="pt", truncation=True).input_ids.to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=model_cfg["max_target_length"],
                num_beams=gen_cfg["num_beams"],
                no_repeat_ngram_size=gen_cfg["no_repeat_ngram_size"],
                length_penalty=gen_cfg["length_penalty"],
                temperature=gen_cfg["temperature"],
                top_p=gen_cfg["top_p"],
                repetition_penalty=gen_cfg["repetition_penalty"],
                early_stopping=True
            )
        
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        return TranslationResponse(
            input_text=request.text,
            translated_text=translated_text,
            direction=request.direction,
            model_used=model.config._name_or_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
