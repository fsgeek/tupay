#!/bin/bash
cat >> "$(dirname "$0")/denied.jsonl"; echo >> "$(dirname "$0")/denied.jsonl"
echo '{"decision":"deny","reason":"D1 merge: no tools; answer from the prompt alone."}'
