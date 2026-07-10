# Assignment 3C — Emotion Classifier + LLM Critic

## What this is

A small end-to-end pipeline:

`Hugging Face dataset (dair-ai/emotion)` → `TF-IDF + Logistic Regression classifier`
→ `model wrapped as an MCP tool` → `Claude (Desktop/Code) calls the tool and
critiques the prediction`, with LIME used as a second, independent
explainability check.

## Files

| File | Purpose |
|---|---|
| `assignment3c_notebook.ipynb` | Load data, train the model, evaluate, LIME explanation, save model, LLM-critic demo via the Claude API |
| `mcp_server.py` | MCP server exposing the trained model as a `predict_emotion` tool |
| `writeup.md` | Reflection write-up template (fill in after running) |
| `emotion_model.joblib`, `label_names.txt` | Produced by the notebook — required by `mcp_server.py` |

## Run order

1. Open `emotion_pipeline.ipynb` in Colab (or locally with Jupyter).
2. Run through Section 5 — this produces `emotion_model.joblib` and `label_names.txt`.
   Download both from Colab into the same folder as `mcp_server.py`.
3. **Either** run Section 6B in-notebook (Claude API call, no MCP config needed —
   fastest way to see the LLM-critic pattern), **or** do the full MCP setup below.

## Full MCP setup (Claude Desktop or Claude Code)

```bash
pip install mcp joblib scikit-learn numpy
```

**Claude Desktop** — edit `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "emotion-model": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop, then in a chat: *"Use predict_emotion on: '...' and tell
me if you agree with the model."*

**Claude Code** — from the project folder:

```bash
claude mcp add emotion-model -- python3 /absolute/path/to/mcp_server.py
```

Then in a Claude Code session, ask it to use the `predict_emotion` tool on
some text and critique the result.

**Test without either** — the MCP Inspector:

```bash
mcp dev mcp_server.py
```

opens a local UI where you can call `predict_emotion` directly and see the
raw tool schema/response.

## Tools used (one-liner)

Kaggle/Hugging Face for the dataset · scikit-learn + LIME for the model and
its local explainability baseline · a custom MCP server to expose the model
as a callable tool · Claude Code / Claude Desktop (and, as a fallback, the
Claude API directly) as the LLM-in-the-loop critic.
