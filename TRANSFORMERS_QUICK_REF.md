# Transformer Commands Quick Reference (Cloud API)

## Installation

```bash
# Install minimal dependencies
pip install -r requirements.txt
```

Only installs: discord.py, requests, python-dotenv (~50MB total)

## Setup (One-Time)

### 1. Get Free Hugging Face Token
```
https://huggingface.co/settings/tokens
→ Click "New token"
→ Create with "read" permission
→ Copy token
```

### 2. Configure .env
```env
DISCORD_TOKEN=your_discord_token
HF_API_TOKEN=your_hugging_face_token
```

### 3. Run Bot
```bash
python main.py
```

Done! No downloads, no setup, just works! ⚡

---

## Commands

### 1️⃣ Summarization
```
!summarize [text - min 50 words]
```

**Speed:** 2-5 seconds (first time 30s on free tier)

---

### 2️⃣ Zero-Shot Classification
```
!classify [text] | [label1], [label2], [label3], ...
```

**Speed:** 1-3 seconds

---

### 3️⃣ Mask Filling
```
!mask [text with MASK token]
```

**Speed:** 1-2 seconds

---

## Quick Examples

### Sentiment
```
!classify This movie was awesome! | positive, negative, neutral
```

### Topic
```
!classify Apple releases new iPhone | tech, sports, politics
```

### Masking
```
!mask The capital of France is [MASK]
```

---

## Performance

| Metric | Value |
|--------|-------|
| **Storage** | <1MB (no models!) ✅ |
| **RAM** | 100MB |
| **Setup time** | <1 minute ✅ |
| **First command** | 2-5s (warm) or 30s (cold start) |
| **Speed** | Cloud-based, consistent |
| **Cost** | Free tier available ✅ |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Token not found | Add to `.env` |
| Slow first time | Normal (free tier), try again |
| API error | Check internet, retry |
| Timeout | Server busy, try later |

---

## Key Difference: Cloud vs Local

### Before (Local)
❌ Download 2.8GB models
❌ Use 2.8GB RAM
❌ First run: 30-60s
✅ Fast after warmup

### Now (Cloud)
✅ No downloads
✅ ~100MB RAM
✅ Simple 1-minute setup
✅ Consistent speed
✅ Scalable

---

**Status**: ✅ Cloud API Ready
**Cost**: Free tier works great!
**Storage**: Minimal (<1MB)

