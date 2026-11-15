# Early draft upload: what to submit

The organisers will send review insights on **17 Nov 2026** to teams that upload a draft prototype and technical documentation **before the early deadline** (the date was cut off in the text you pasted: check the portal for it). The final deadline is 20 Nov, 22:29 IST.

## What to upload

| Asked for | File or link |
|---|---|
| Technical documentation | `NABD-technical-documentation.pdf` (5 pages, compiled from `NABD-technical-documentation.tex`) |
| Fuller documentation, if the portal takes a second file | `docs/TECHNICAL.md` |
| Prototype link | `https://ammad1h.github.io/NABD/` (fallback: `https://github.com/Ammad1H/NABD`) |
| Prototype file | `NABD-prototype-web.zip` |
| Solution deck | `../NABD-submission-deck.pdf` |

## Getting the link live (about 10 minutes)

1. **Push** with `git push origin main` (a token with the `repo` scope is enough).
2. **Public.** Repository Settings > General > Danger zone > Change visibility > Public. Run `scripts/prepare_public_repo.sh` first if you want the banned-claim scan.
3. **Pages.** Repository Settings > Pages > Build and deployment > Source: **Deploy from a branch**, branch `main`, folder `/ (root)`. The root `index.html` redirects to `web/dist`. After a few minutes, open the link in a private window to confirm it loads without a login.

## Questions to ask the reviewers (also on page 3 of the PDF)

1. Is a positivity forecast the right interface for hospital operations, or should the pilot target admissions directly?
2. How should a pooled model be governed in production (retraining, drift checks, replacing the headline model)?
3. What is the integration path into Abu Dhabi systems for a read-only forecast feed with human approval?
4. Is a locked live test followed by a 12-week shadow pilot the right shape for a first deployment?

## Before you hit upload

- Open the PDF once and read page 2 (evidence table). Every number matches `results/`; the US miss is included on purpose.
- After the 17 Nov feedback, edit `NABD-technical-documentation.tex` and recompile with tectonic or Overleaf.
