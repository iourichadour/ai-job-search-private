## 1. Remove Dead Danish Job Portal Skills

- [ ] 1.1 Delete `.agents/skills/jobbank-search/` directory and verify it no longer exists via `ls -la .agents/skills/`
- [ ] 1.2 Delete `.agents/skills/jobdanmark-search/` directory and verify deletion with `ls -la .agents/skills/`
- [ ] 1.3 Delete `.agents/skills/jobindex-search/` directory and verify deletion with `ls -la .agents/skills/`
- [ ] 1.4 Delete `.agents/skills/jobnet-search/` directory and verify deletion with `ls -la .agents/skills/`

## 2. Clarify `/apply` Command Documentation

- [ ] 2.1 Read `.claude/commands/apply.md` and identify the full documented pipeline (CV drafter, cover letter, LaTeX, PDF compilation)
- [ ] 2.2 Update `.claude/commands/apply.md` with a note documenting the full pipeline explicitly and marking it as potentially superseded by a simpler markdown-resume approach (reference this SCRUM-13 change as clarification of what exists; indicate a followup change will scope `/apply` simplification if desired)
- [ ] 2.3 Verify the updated `.claude/commands/apply.md` clearly documents both the current full implementation AND the documented CLAUDE.md intent, minimizing future confusion

## 3. Verify No Broken References

- [ ] 3.1 Search for any remaining references to the deleted skills (`jobbank-search`, `jobdanmark-search`, `jobindex-search`, `jobnet-search`) via `grep -r "jobbank-search\|jobdanmark-search\|jobindex-search\|jobnet-search" .` and verify no references remain outside deleted directories
- [ ] 3.2 Verify no imports or symlinks to the deleted directories exist via `find . -type l -o -xtype f 2>/dev/null | xargs grep -l "jobbank\|jobdanmark\|jobindex\|jobnet" 2>/dev/null` and confirm output is empty or contains only archive references

## 4. Commit and Close

- [ ] 4.1 Stage the deletions and `.claude/commands/apply.md` update via `git add -A`
- [ ] 4.2 Create a single commit with message: `chore(SCRUM-13): remove dead Danish job-portal scrapers, clarify /apply pipeline` and verify the commit appears in `git log`
- [ ] 4.3 Run `git status` and verify working tree is clean
