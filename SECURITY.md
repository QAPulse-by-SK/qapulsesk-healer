# Security policy

## Supported versions

`qapulsesk-healer` is pre-1.0 — only the latest minor release receives security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

Please **do not open a public GitHub issue** for security problems.

Email the maintainer at **hello@skakarh.com** with:

- A clear description of the issue
- Steps to reproduce, if available
- The version (or commit SHA) you tested against
- Any proof-of-concept code or output

You can expect:

- An acknowledgment within 72 hours
- An initial assessment within 7 days
- A fix or mitigation plan within 30 days for confirmed issues

If the issue is confirmed and fixed, you'll be credited in the release notes unless you prefer to remain anonymous.

## What counts as a security issue

- Anything that lets a malicious page source cause the healer to execute arbitrary code in the test process
- Leaks of the Anthropic API key (or any other secret) into logs, error messages, or the heal audit log
- Prompt-injection vectors that could redirect the LLM to attempt clearly harmful locator strategies (e.g. forms that exfiltrate data)
- Supply-chain risks introduced by added dependencies

## What does **not** count as a security issue

- The LLM proposing a wrong but harmless locator — that's a bug, not a vulnerability
- API key exposure caused by the user committing their own `.env` file
- DoS via excessive token usage from a malicious page — bound this with `max_chars` in the snapshot minifier

Thanks for helping keep the QAPulse by SK ecosystem safe.
