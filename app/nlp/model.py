import os

from app.config import SYSTEM_PROMPT

MODE = os.getenv("MODEL_MODE", "templated").lower()
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
MAX_NEW = int(os.getenv("MAX_NEW_TOKENS", "160"))
TEMP = float(os.getenv("TEMPERATURE", "0.7"))

def _read_system_prompt():
    try:
        with open(SYSTEM_PROMPT, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "You are a helpful, concise assistant."

class GenModel:
    def __init__(self):
        self.system = _read_system_prompt()
        self.mode = MODE
        self.pipe = None

        if self.mode == "hf":
            try:
                # Try to load HF model; if torch/weights unavailable, fall back gracefully.
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                tok = AutoTokenizer.from_pretrained(HF_MODEL_ID, use_fast=True)
                mdl = AutoModelForCausalLM.from_pretrained(HF_MODEL_ID)
                self.pipe = pipeline("text-generation", model=mdl, tokenizer=tok)
            except Exception as e:
                # Fallback: templated mode
                print(f"[model] HF init failed ({e}). Falling back to templated mode.")
                self.mode = "templated"
                self.pipe = None

    def generate_turn(self, base_text: str, rag_snippets: list[str], name: str) -> str:
        # Always substitute name in base_text
        base_text = (base_text or "").replace("{name}", name).strip()

        facts = ""
        if rag_snippets:
            facts = "Полезные факты:\n" + "\n".join(f"• {s}" for s in rag_snippets)

        # Templated path (default & fallback)
        if self.mode != "hf" or self.pipe is None:
            composed = f"{base_text}"
            if facts:
                composed += f"\n\n{facts}"
            return composed.strip()

        # HF path
        prompt = (
            f"{self.system}\n\n"
            f"User name: {name}\n"
            f"Base text (keep key info, 4-6 sentences):\n{base_text}\n\n"
            f"Facts to incorporate faithfully (bullet points allowed at the end):\n{facts}\n\n"
            f"Write in the same language as the base text. No markdown headings."
        )
        out = self.pipe(
            prompt,
            max_new_tokens=MAX_NEW,
            do_sample=True, temperature=TEMP,
            eos_token_id=self.pipe.tokenizer.eos_token_id,
            pad_token_id=self.pipe.tokenizer.eos_token_id,
        )[0]["generated_text"]
        return out[len(prompt):].strip() if out.startswith(prompt) else out.strip()
