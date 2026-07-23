---
description: Saves the latest compact summary of this session as a markdown file. Use when the user wants to save or export the session history/summary to a file.
argument-hint: [output-path]
allowed-tools: Bash, Read, Write, AskUserQuestion
---

## Instructions

> **If you are GitHub Copilot or any AI assistant other than Claude Code**, read the file at `${CLAUDE_SKILL_DIR}/Copilot.md` for the appropriate instructions and commands to follow instead of the steps below.

Follow these steps in order:

### Step 1 — Find the session jsonl path

The compact summary injected at the start of this session contains the jsonl path at the very end:
> "read the full transcript at: `<path>`"

Extract that absolute path from context. Store it as `JSONL_PATH`.

### Step 2 — Ask for output location

If `$ARGUMENTS` is provided, use it as the output path.
Otherwise ask the user: **"Where would you like to save the history markdown? (e.g. `history.md`)"**

Store the result as `OUTPUT_PATH`.

### Step 3 — Extract and save

Run this in the Bash tool, substituting `JSONL_PATH` and `OUTPUT_PATH`:

```bash
JSONL_PATH="<jsonl_path>"
OUTPUT_PATH="<output_path>"

if command -v jq &>/dev/null; then
  jq -rn '[inputs | select(.isCompactSummary == true)] | last | .message.content' "$JSONL_PATH" > "$OUTPUT_PATH"
elif command -v node &>/dev/null; then
  node -e "
    const fs = require('fs');
    const lines = fs.readFileSync('$JSONL_PATH', 'utf8').trim().split('\n');
    const all = lines.map(l => { try { return JSON.parse(l); } catch(e) { return null; } }).filter(e => e && e.isCompactSummary);
    if (all.length) fs.writeFileSync('$OUTPUT_PATH', all[all.length - 1].message.content);
    else { console.error('No compact summary found'); process.exit(1); }
  "
else
  powershell.exe -Command "
    \$latest = Get-Content '$JSONL_PATH' | ForEach-Object { try { \$_ | ConvertFrom-Json } catch {} } | Where-Object { \$_.isCompactSummary } | Select-Object -Last 1;
    if (\$latest) { \$latest.message.content | Set-Content -Encoding UTF8 '$OUTPUT_PATH' } else { Write-Error 'No compact summary found'; exit 1 }
  "
fi
```

If all commands above fail or are unavailable, fall back to manual extraction:
- Use the Read tool to read `JSONL_PATH` line by line
- Find the last line where `"isCompactSummary":true` appears
- Parse the `message.content` value from that line
- Use the Write tool to save the content to `OUTPUT_PATH`

### Step 4 — Confirm

Tell the user the file was saved and show the full output path.