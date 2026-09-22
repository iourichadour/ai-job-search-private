## 1. Remove Dead Danish Job Portal Skills

- [x] 1.1 Delete `.agents/skills/jobbank-search/` directory and verify it no longer exists via `ls -la .agents/skills/`
- [x] 1.2 Delete `.agents/skills/jobdanmark-search/` directory and verify deletion with `ls -la .agents/skills/`
- [x] 1.3 Delete `.agents/skills/jobindex-search/` directory and verify deletion with `ls -la .agents/skills/`
- [x] 1.4 Delete `.agents/skills/jobnet-search/` directory and verify deletion with `ls -la .agents/skills/`

## 2. Clarify `/apply` Command Documentation

- [x] 2.1 Read `.claude/commands/apply.md` and identify the full documented pipeline (CV drafter, cover letter, LaTeX, PDF compilation)
- [x] 2.2 Update `.claude/commands/apply.md` with a note documenting the full pipeline explicitly and marking it as potentially superseded by a simpler markdown-resume approach (reference this SCRUM-17 change as clarification of what exists; indicate a followup change will scope `/apply` simplification if desired)
- [x] 2.3 Verify the updated `.claude/commands/apply.md` clearly documents both the current full implementation AND the documented CLAUDE.md intent, minimizing future confusion

## 3. Verify No Broken References

- [x] 3.1 Search for any remaining references to the deleted skills (`jobbank-search`, `jobdanmark-search`, `jobindex-search`, `jobnet-search`) via `grep -r "jobbank-search\|jobdanmark-search\|jobindex-search\|jobnet-search" .` and verify no references remain outside deleted directories
- [x] 3.2 Verify no imports or symlinks to the deleted directories exist via `find . -type l -o -xtype f 2>/dev/null | xargs grep -l "jobbank\|jobdanmark\|jobindex\|jobnet" 2>/dev/null` and confirm output is empty or contains only archive references

## 4. Rewrite README.md

- [x] 4.1 Replace the outdated workflow diagram (Danish portal scraping) with current workflow (Gmail alerts → agent evaluation → application)
- [x] 4.2 Remove all references to Danish job portals (Jobindex, Jobnet, Akademikernes Jobbank)
- [x] 4.3 Remove Bun and LaTeX from Prerequisites (or mark as optional/legacy)
- [x] 4.4 Add brief description of actual workflow: "Fetch jobs from Gmail alerts, evaluate with AI agents, apply to high-fit roles"
- [x] 4.5 Preserve MIT license attribution to Mads Lorentzen per LICENSE file
- [x] 4.6 Verify README renders correctly in markdown preview

## 5. Update SETUP.md

- [x] 5.1 Remove Bun installation section (no longer needed for Danish job portal CLIs)
- [x] 5.2 Remove LaTeX setup section or mark it as optional/legacy for the old `/apply` pipeline
- [x] 5.3 Update Prerequisites to focus on Claude Code and Python setup only
- [x] 5.4 Add or update section on Gmail OAuth configuration if required by fetch_inbox workflow
- [x] 5.5 Verify SETUP.md aligns with actual current setup requirements

## 6. Commit and Close

- [ ] 6.1 Stage all changes (deletions, doc updates) via `git add -A`
- [ ] 6.2 Create a single commit with message: `chore(SCRUM-17): remove dead Danish job-portal scrapers, clarify /apply, rewrite docs` and verify the commit appears in `git log`
- [ ] 6.3 Run `git status` and verify working tree is clean
