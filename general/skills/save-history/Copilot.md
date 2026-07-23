# save-history (GitHub Copilot variant)

Use this prompt with GitHub Copilot Chat (`@workspace` or `@terminal`) to save the latest compact summary from a Claude Code session.

---

## How to use

Paste the following into Copilot Chat, filling in the values:

```text
I want to extract the latest compact summary from a Claude Code session jsonl file and save it as markdown.

Session jsonl path: <paste the path here>
Output path: <paste the desired output path here>

Please run the appropriate command below based on what's available in the terminal.
```

---

## Commands to run in terminal

Pick the first one that works on your machine:

### jq (Linux/Mac/Windows with jq installed)

```bash
jq -rn '[inputs | select(.isCompactSummary == true)] | last | .message.content' "<JSONL_PATH>" > "<OUTPUT_PATH>"
```

### node (if Node.js is installed)

```bash
node -e "
const fs = require('fs');
const lines = fs.readFileSync('<JSONL_PATH>', 'utf8').trim().split('\n');
const all = lines.map(l => { try { return JSON.parse(l); } catch(e) { return null; } }).filter(e => e && e.isCompactSummary);
if (all.length) fs.writeFileSync('<OUTPUT_PATH>', all[all.length - 1].message.content);
else console.error('No compact summary found');
"
```

### PowerShell (Windows)

```powershell
$latest = Get-Content "<JSONL_PATH>" | ForEach-Object { try { $_ | ConvertFrom-Json } catch {} } | Where-Object { $_.isCompactSummary } | Select-Object -Last 1
if ($latest) { $latest.message.content | Set-Content -Encoding UTF8 "<OUTPUT_PATH>" } else { Write-Error "No compact summary found" }
```

---

## Where is the Claude Code session jsonl?

> This skill extracts compact summaries from **Claude Code** sessions, not Copilot's own chat history.

Claude Code stores session transcripts at:

| OS        | Path                                                              |
|-----------|-------------------------------------------------------------------|
| Windows   | `%USERPROFILE%\.claude\projects\<slug>\<session-id>.jsonl`        |
| Mac/Linux | `~/.claude/projects/<slug>/<session-id>.jsonl`                    |

The slug is formed by replacing path separators in the project directory path with `-`.

**Find the most recently modified session:**

Bash:

```bash
ls -t ~/.claude/projects/<slug>/*.jsonl | head -1
```

PowerShell:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\projects\<slug>\*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
```

> Tip: The exact path is also printed at the end of every Claude Code compact summary — look for the line starting with "read the full transcript at:"