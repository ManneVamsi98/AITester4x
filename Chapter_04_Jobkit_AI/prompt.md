# Resume Tailoring Workflow — Chapter 04 (Jobkit AI)

Reusable prompt + steps for tailoring a resume to multiple job descriptions using the
`resume-tailor` skill.

## What this folder produces

- `output/*.docx` — tailored resumes, one per job posting (working copies with yellow
  highlights for changes and red `[placeholders]` for facts only you can supply).
- `output/specs/*.json` — the resume spec files (input to the build script). **Keep these.**
  The .docx are *rendered outputs*; the .json is the editable source. Without the spec
  you cannot re-run the build, tweak a bullet, or generate a `--clean` (send-ready) copy.

## The prompt that was used

```
This is my skill file: <path to resume-tailor/SKILL.md>
This is my resume: <path to finalresume.md>
Create tailored versions for each of these job postings, applying the skill, and output
them to <Chapter_04_Jobkit_AI>/output with the company name in the filename.

<paste job postings here>
```

## Skill workflow applied (from resume-tailor/SKILL.md)

1. **Read inputs** — resume + each job description.
2. **Extract the JD's real requirements** — must-have skills (gates), responsibilities
   (verbs), seniority signals, domain, recurring vocabulary.
3. **Cross-reference** — verdict per requirement: ✅ match / 🟡 partial / 🙈 absent.
   Never invent skills, tools, metrics, or dates.
4. **Report before writing** — match table + blunt fit estimate shown to the user.
5. **Build** — write one JSON spec per job into `output/specs/`, then render:
   ```bash
   node scripts/build_resume.js output/specs/<Name>_<Company>_<Role>.json   # working copy
   node scripts/build_resume.js output/specs/<Name>_<Company>_<Role>.json --clean  # send-ready
   ```
6. **Deliver** — .docx in `Chapter_04_Jobkit_AI/output/` (or Drive as Google Doc).

## Markup used in the specs

| Markup  | Renders as       | Purpose                                    |
|---------|------------------|--------------------------------------------|
| `==text==` | yellow highlight | a change made for this JD                  |
| `[text]`   | red bold         | a fact only you can supply (blocks --clean)|
| `**text**` | bold             | a metric or term to anchor the eye         |

## To regenerate / create send-ready copies

```bash
cd Chapter_04_Jobkit_AI/Resume_Helper/resume-tailor/scripts
node build_resume.js "E:\AI Tester 4x\AI Tester 4x\Chapter_04_Jobkit_AI\output\specs\Manne_Vamsi_<Company>_<Role>.json" --clean
```

`--clean` strips highlights, drops `note` blocks, and **refuses to build if any
`[placeholder]` remains** — fill or delete brackets first.

## Gotcha when authoring specs

Keep the whole string inside the quotes — do not close the quote after `==` in the middle
of a skill row (e.g. `"==Azure DevOps CI/CD Pipelines==" · Jira` breaks JSON).
