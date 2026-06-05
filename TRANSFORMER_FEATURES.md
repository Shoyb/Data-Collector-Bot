# Transformer NLP Features (Cloud API)

## Overview

The bot uses **Hugging Face Inference API** for AI/ML capabilities. No local model downloads needed - everything runs on HF cloud servers!

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This only installs: discord.py, requests, python-dotenv (~50MB)

### 2. Get Hugging Face API Token

**Free setup (3 options):**

**Option A: Free Inference API (Recommended)**
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Create token with "read" permission
4. Copy the token

**Option B: Free tier with rate limits**
- Same as Option A, slightly slower

**Option C: Paid tier**
- Unlimited requests
- Faster responses
- Optional but not needed

### 3. Configure Bot

Create/edit `.env` file:
```env
DISCORD_TOKEN=your_discord_token_here
HF_API_TOKEN=your_hugging_face_token_here
```

### 4. Run Bot
```bash
python main.py
```

Done! No model downloads, no waiting, just ready to use! ⚡

---

## Features

### 1. **Text Summarization**
Summarizes long text using BART model on cloud.

**Command:**
```
!summarize [your text here]
```

**Speed:** ~2-5 seconds (cloud API)
**Requirements:** 50+ words

---

### 2. **Zero-Shot Classification**
Classifies text without training data.

**Command:**
```
!classify [text] | [label1], [label2], [label3], ...
```

**Speed:** ~1-3 seconds

---

### 3. **Mask Filling (Cloze Test)**
Predicts masked words using BERT.

**Command:**
```
!mask [text with [MASK]]
```

**Speed:** ~1-2 seconds

---

## Performance

| Aspect | Details |
|--------|---------|
| **Model download** | None! Uses cloud API |
| **Local storage** | <1MB (only code) |
| **Memory usage** | ~100MB (bot only) |
| **Startup time** | <1 second |
| **First command** | 2-5 seconds |
| **Subsequent commands** | 1-3 seconds |
| **Internet** | Required |
| **Cost** | Free tier available |

---

## Cost

### Free Tier
- ✅ Unlimited requests
- ✅ All features
- ⚠️ ~30 second inference time (model warming)
- Fair for hobbyists

### Paid Tier ($9/month)
- ✅ Faster inference (1-3 seconds)
- ✅ Priority queue
- Better for production

Both work fine! Start with free, upgrade if needed.

---

## Troubleshooting

### "HF_API_TOKEN not found"
- **Solution**: Add `HF_API_TOKEN=your_token` to `.env` file

### Command is very slow (30s+)
- **Cause**: Free tier with model warming
- **Solution**: Wait, then try again (should be 2-5s after first run)

### "Unauthorized" error
- **Cause**: Invalid or expired token
- **Solution**: Check token in `.env`, regenerate if needed

### "API Error" on specific command
- **Cause**: HF API temporarily down
- **Solution**: Try again in a few seconds

### Models not responding
- **Cause**: Network issue or API overload
- **Solution**: Check internet, try again later, or upgrade to paid tier

---

## Advantages Over Local

| Aspect | Local | Cloud |
|--------|-------|-------|
| **Initial download** | 30-60s, 2.8GB | None ✅ |
| **Storage** | 2.8GB | <1MB ✅ |
| **Memory** | 2.8GB when active | 100MB ✅ |
| **Speed** | 1-5s after warmup | 1-5s always |
| **Internet** | Not needed | Required ✅ |
| **Setup** | Complex | Simple ✅ |
| **Scalability** | Limited | Unlimited ✅ |

---

## Examples

### Summarization
```
!summarize Artificial intelligence is transforming industries worldwide. Machine learning models are becoming more sophisticated. They are used in healthcare, finance, transportation, and many other sectors. These advancements raise important ethical questions.
```

**Output:**
```
Summary:
AI is transforming industries and being used in healthcare, finance, and transportation, while raising ethical questions.
```

### Classification
```
!classify This product is amazing! I love it! | positive, negative, neutral
```

**Output:**
```
Classification Result:
Top Match: positive (94.23%)

All Scores:
  • positive: 94.23%
  • neutral: 5.12%
  • negative: 0.65%
```

### Masking
```
!mask The capital of France is [MASK]
```

**Output:**
```
1. paris (89.23%)
2. lyon (2.34%)
3. marseille (1.45%)
4. bordeaux (0.82%)
5. toulouse (0.61%)
```

---

## API Limitations

### Free Tier
- 30-60 second warmup on first request
- 2-5 second response on subsequent requests
- Fair use policy (don't spam)

### Paid Tier
- <1 second consistent response
- Priority access
- No warmup delays

---

## Advanced Usage

### Directly call API
```python
from core.transformers_nlp import transformer_models

# Summarize
result = transformer_models.summarize("Your text here")

# Classify
result = transformer_models.zero_shot_classify(
    "Your text",
    ["label1", "label2", "label3"]
)

# Mask
result = transformer_models.fill_mask("Text with [MASK]")
```

---

## Resources

- [Get Free API Token](https://huggingface.co/settings/tokens)
- [Hugging Face Inference API](https://huggingface.co/inference-api)
- [BART Model](https://huggingface.co/facebook/bart-large-cnn)
- [BERT Model](https://huggingface.co/bert-base-uncased)

---

**Status**: ✅ Cloud API Ready
**No Downloads**: ✅ Pure cloud inference
**Lightweight**: ✅ <1MB storage needed

