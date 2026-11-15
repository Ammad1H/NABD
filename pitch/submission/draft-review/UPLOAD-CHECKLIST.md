# Early draft upload: what to submit

The organisers will send review insights on **17 Nov 2026** to teams that upload a draft prototype and technical documentation **before the early deadline** (the date was cut off in the text you pasted: check the portal for it). The final deadline is 20 Nov, 22:29 IST.

## What to upload

| Asked for | File or link | State |
|---|---|---|
| Draft technical documentation | `NABD-technical-documentation-draft.pdf` (3 pages: architecture, models, evidence with status, integrity, assumptions, limitations, how to run, four questions for reviewers) | Ready |
| Fuller documentation, if the portal takes a second file | `docs/TECHNICAL.md` (about 6,000 words) | Ready; refreshed 14 Nov |
| Draft prototype, link | `https://ammad1h.github.io/NABD/` and `https://github.com/Ammad1H/NABD` | **Not live yet**: needs the push, a public repository and Pages (below) |
| Draft prototype, file fallback | `NABD-prototype-web.zip`: unzip and open `index.html` through any web server, or run `python -m http.server` in the folder | Ready |
| Optional: the filled challenge deck | `../NABD-submission-deck.pdf` | Ready; send it too if the portal allows more files |

## Getting the link live (about 10 minutes)

1. **Push.** The last push was rejected because the token lacks the `workflow` scope. On GitHub: Settings > Developer settings > Personal access tokens > open your token > tick `workflow` > Update. Then run `git push origin main` again; nothing else needs retyping.
2. **Public.** Repository Settings > General > Danger zone > Change visibility > Public. Run `scripts/prepare_public_repo.sh` first if you want the banned-claim scan.
3. **Pages.** Repository Settings > Pages > Build and deployment > Source: **GitHub Actions**. The workflow publishes `web/dist` on every push. After a minute, open the link in a private window to confirm it loads without a login.

## Questions to ask the reviewers (also on page 3 of the PDF)

1. Is a positivity forecast the right interface for hospital operations, or should the pilot target admissions directly?
2. How should a pooled model be governed in production (retraining, drift checks, replacing the headline model)?
3. What is the integration path into Abu Dhabi systems for a read-only forecast feed with human approval?
4. Is a locked live test followed by a 12-week shadow pilot the right shape for a first deployment?

## Before you hit upload

- Open the PDF once and read page 2 (evidence table). Every number matches `results/`; the US miss is included on purpose.
- The draft is not the final submission. After the 17 Nov feedback, update `docs/TECHNICAL.md` and rebuild with `python pitch/submission/draft-review/build_techdoc.py`.
