# Agent Rules for fzportproxy

These rules apply to any agent working on the `fzportproxy` project.

## Critical Requirements

1. **Changelog Maintenance**:
   - For every modification, addition, or deletion in this codebase, the agent **MUST** document the changes in [CHANGELOG.md](file:///E:/fzportproxy/fzportproxy/CHANGELOG.md).
   - Ensure the description is clear and highlights what was changed, added, or removed.

2. **Documentation Maintenance**:
   - The [README.md](file:///E:/fzportproxy/fzportproxy/README.md) **MUST** be reviewed and updated to reflect any changes in dependencies, installation steps, compilation instructions, or features.

3. **UAC Elevation**:
   - Any code executed or compiled must account for Administrator/UAC elevation since this project interacts with system network configurations (`netsh interface portproxy`, Firewall, and `hosts` file).
