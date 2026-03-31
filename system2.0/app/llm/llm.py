from transformers import pipeline

# Use SMALL model for stability
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",  # ✅ lightweight & stable
    device=-1  # CPU safe
)

def llm(prompt, max_tokens=256):
    try:
        response = generator(
            prompt[:1500],  # ✅ HARD LIMIT to avoid overflow
            max_new_tokens=max_tokens,
            do_sample=False  # ✅ deterministic output
        )

        return response[0]["generated_text"]

    except Exception as e:
        print(f"LLM ERROR: {e}")
        return ""