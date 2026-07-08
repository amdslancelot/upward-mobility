#!/usr/bin/env bash
# upward — SessionStart activation hook.
# Emits the always-on operating discipline (core.md) as raw stdout, which
# native Claude Code injects into the session context. Detailed rules live in
# the plugin's skills and load on demand — do NOT cat them here.
cat "${CLAUDE_PLUGIN_ROOT}/core.md"
exit 0
