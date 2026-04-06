# =============================================================================
# models.py — GPU management and Qwen model interfaces
# =============================================================================
# Load/unload Qwen models and send prompts. No models loaded at import time.
#
# Location: E:\Data\gsoto\analytical\models.py
# Usage:    from models import load_qwen_text, ask_qwen_text
# =============================================================================


# Module-level references (set by load functions)
qwen_model = None
qwen_tokenizer = None
qwen_processor = None


# =============================================================================
# MODEL LOADING
# =============================================================================

def load_qwen_text(model_id='Qwen/Qwen2.5-7B-Instruct'):
    """
    Load Qwen2.5-7B-Instruct (text-only).
    Takes ~30s, uses ~14 GB VRAM.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    global qwen_model, qwen_tokenizer

    print(f"Loading {model_id}...")
    t0 = __import__('time').time()

    qwen_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map='cuda:0',
        trust_remote_code=True,
    )
    qwen_tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True,
    )

    elapsed = __import__('time').time() - t0
    vram = torch.cuda.memory_allocated() / 1024**3
    print(f"✓ Text model loaded in {elapsed:.0f}s — VRAM: {vram:.1f} GB")
    return qwen_model, qwen_tokenizer


def load_qwen_vlm(model_id='Qwen/Qwen2.5-VL-7B-Instruct'):
    """
    Load Qwen2.5-VL-7B-Instruct (vision-language).
    Takes ~30s, uses ~14 GB VRAM.
    """
    import torch
    from transformers import AutoModelForVision2Seq, AutoProcessor

    global qwen_model, qwen_processor

    print(f"Loading {model_id}...")
    qwen_model = AutoModelForVision2Seq.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map='cuda:0',
        trust_remote_code=True,
    )
    qwen_processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
    print(f"✓ VLM loaded — VRAM: {torch.cuda.memory_allocated()/1024**3:.1f} GB")
    return qwen_model, qwen_processor


def free_gpu_memory():
    """Delete model from GPU and clear CUDA cache."""
    import torch, gc
    global qwen_model, qwen_tokenizer, qwen_processor

    qwen_model = None
    qwen_tokenizer = None
    qwen_processor = None

    gc.collect()
    torch.cuda.empty_cache()
    print(f"VRAM after cleanup: {torch.cuda.memory_allocated()/1024**3:.1f} GB")


def gpu_status():
    """Print current GPU memory usage."""
    import torch
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_properties(0)
        total_gb = gpu.total_mem / 1024**3
        alloc_gb = torch.cuda.memory_allocated(0) / 1024**3
        reserved_gb = torch.cuda.memory_reserved(0) / 1024**3
        free_gb = total_gb - reserved_gb
        print(f"GPU: {gpu.name}")
        print(f"Total: {total_gb:.1f} GB | Allocated: {alloc_gb:.1f} GB | "
              f"Reserved: {reserved_gb:.1f} GB | Free: {free_gb:.1f} GB")
    else:
        print("⚠ No CUDA GPU detected")


# =============================================================================
# QWEN TEXT INTERFACE
# =============================================================================

def ask_qwen_text(question: str, max_tokens: int = 4000) -> str:
    """Send a text prompt to Qwen and return the response."""
    import torch

    messages = [{"role": "user", "content": [{"type": "text", "text": question}]}]

    text = qwen_tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = qwen_tokenizer(text, return_tensors="pt", padding=True).to("cuda")

    n_tokens = inputs.input_ids.shape[1]
    if n_tokens > 6000:
        print(f"    ⚠ Long input ({n_tokens} tokens)")

    torch.cuda.empty_cache()
    with torch.no_grad():
        output_ids = qwen_model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)

    generated = [o[len(i):] for i, o in zip(inputs.input_ids, output_ids)]
    response = qwen_tokenizer.batch_decode(generated, skip_special_tokens=True)[0]

    del inputs, output_ids, generated
    torch.cuda.empty_cache()
    return response


# =============================================================================
# QWEN VLM INTERFACE
# =============================================================================

def ask_vlm(image, prompt, max_tokens=3000):
    """Send one page image to VLM. Returns raw text."""
    import torch
    from qwen_vl_utils import process_vision_info

    messages = [{"role": "user", "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": prompt}
    ]}]
    text = qwen_processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = qwen_processor(
        text=[text], images=image_inputs, videos=video_inputs,
        padding=True, return_tensors="pt"
    ).to("cuda:0")

    with torch.no_grad():
        out = qwen_model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)

    response = qwen_processor.batch_decode(
        [o[len(i):] for i, o in zip(inputs.input_ids, out)],
        skip_special_tokens=True
    )[0]

    del inputs, out
    torch.cuda.empty_cache()
    return response