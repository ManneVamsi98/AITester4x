Commit all current changes and push them to the remote.

1. Run `git status` to see what changed.
2. Stage all changes with `git add -A`.
3. Review the staged changes (git diff --cached --stat and a quick look at content) to craft an accurate commit message.
4. Commit with a concise conventional-commit style message: `type(scope): subject`, adding a short body only if the change needs explaining. Append the co-author trailer:
   Co-authored-by: CommandCodeBot <noreply@commandcode.ai>
5. Push to the current branch's upstream (`git push`), or the default remote if no upstream is set.
6. Report the commit hash and push result.
