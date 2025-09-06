# RpPanel

Cog for Red-DiscordBot providing a base for a roleplay (RP) panel.

## Current features (v0.1.0)

- Hybrid command group: `rppanel`
- `rppanel ping` checks status
- `rppanel version` shows version
- `rppanel toggle` enable/disable per guild (admin or Manage Server required)
- Panel instances with arbitrary stats:
   - `rppanel create <id> [title]`
   - `rppanel delete <id>`
   - `rppanel set <id> <label> <value>`
   - `rppanel remove <id> <label>`
   - `rppanel show <id>` (embed output)
   - `rppanel list`

## Installation

1. Add the repo to your bot:
   `[p]repo add joanjuan-cogs <YOUR_REPO_GIT_URL>`
2. Install the cog:
   `[p]cog install joanjuan-cogs rppanel`
3. Load the cog:
   `[p]load rppanel`

## Quick use

Examples:

`[p]rppanel create char1 "Warrior A"`
`[p]rppanel set char1 HP 120/150`
`[p]rppanel set char1 Status Poisoned`
`[p]rppanel show char1`

## User data

This cog stores no persistent user data (`red_delete_data_for_user` is a no-op).

## Extend

You can add subcommands under the `rppanel` group to manage channels, roles, forms, etc.

## License

MIT
