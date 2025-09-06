# RPPanel

Base cog for a role-play utilities panel with both prefix and slash commands.

## Commands

Prefix:
- `[p]rppanel ping` (simple latency)
- `[p]rppanel create <name>`
- `[p]rppanel delete <name>`
- `[p]rppanel list`

Slash (after syncing):
- `/rppanel ping` (ephemeral latency)
- `/rppanel create name:<name>`
- `/rppanel delete name:<name>`
- `/rppanel list`

The slash response is ephemeral (only you see it); remove `ephemeral=True` in code to change.

## Installation

1. Add the repo if not already:
   `[p]repo add joanjuan-cogs https://github.com/JoanJuan10/joanjuan-cogs`
2. Install:
   `[p]cog install joanjuan-cogs rppanel`
3. Load:
   `[p]load rppanel`
4. Sync slash (global):
   `[p]slash sync`  (may take up to 1h globally; for faster server-specific sync below)
   
   Single server (run inside target guild):
   `[p]slash sync guild`
5. Test:
   - Prefix: `[p]rppanel ping`
   - Slash: `/rppanel ping` (you may need to refresh Discord with Ctrl+R)

## Notes
- Stores no persistent user data.
- On reload the cog removes commands to prevent duplicates.
- If you change slash structure, run `[p]slash sync guild` again.
- Instances are stored per guild using Red's Config under a dictionary keyed by lowercase name.
