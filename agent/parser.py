# agent/parser.py
import json
import re
from models.task_plan import TaskPlan

class Parser:
    def parse(self, raw_text: str) -> TaskPlan:
        cleaned_text = raw_text.strip()
        
        # Strip out any markdown code blocks if present
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^
http://googleusercontent.com/immersive_entry_chip/0

---

### 🚀 Complete Step-by-Step Execution Sequence

When you open your terminal and run `python3 app.py`, the execution sequence runs through your two-stage pipeline exactly as requested:

1. **User Request Input:** You enter a prompt (e.g., *"check my inbox and summarize emails received today"*).
2. **Stage 1 (Intent Classification / Routing):** * `Orchestrator` passes the string to `Planner`, which activates `Router.route()`.
   * The `Router` passes this context to `OllamaClient.route()`.
   * The local LLM processes the input using `ROUTER_PROMPT` and returns just the module key string: `"gmail"`.
3. **Stage 2 (Context Building & Argument Plan Generation):**
   * `Planner` sends the `"gmail"` string into `PromptBuilder.build()` along with your original prompt.
   * `PromptBuilder` merges your `BASE_PROMPT`, the specific rules of `GMAIL_PROMPT`, and your user string.
   * This customized prompt goes to `OllamaClient.generate()`, allowing the model to focus exclusively on picking functions and arguments for Gmail (e.g., `summarize_emails` with argument `{"date_filter": "today"}`).
4. **Parsing & Argument Validation:**
   * The text response is returned to the updated `Parser.parse()` block, which strips any stray markdown text, parses the raw JSON code, and returns a verified `TaskPlan` structure.
5. **Stage 3 (Native System Execution):**
   * `Orchestrator` loops through the target steps, prompting `Executor.execute()` to initialize `GmailTool` out of the fixed registry map and run your code natively on Ubuntu.