# Getting a public link (about 15 minutes; needs your GitHub login)

State on 15 Nov 2026: the repository https://github.com/Ammad1H/NABD exists but is not publicly visible, and it is behind this laptop (it stops at commit 252f044). The saved GitHub credential on this laptop is rejected, so nothing can be pushed until you sign in again.

1. **Sign in.** Create a personal access token at GitHub > Settings > Developer settings > Personal access tokens (classic, scope `repo` and `workflow`), then run `git push origin main`. When asked, the username is your GitHub username and the password is the token.
2. **Check before going public.** Run `bash scripts/prepare_public_repo.sh` and read its report (secrets, large files, banned wording).
3. **Make the repository public** (Settings > General > Danger zone > Change visibility). Judges need to open it, and free GitHub Pages needs a public repository.
4. **Turn on Pages.** Settings > Pages > Build and deployment > Source: **GitHub Actions**. The workflow `.github/workflows/pages.yml` publishes `web/dist` on every push to `main`. The page appears at https://ammad1h.github.io/NABD/ a minute or two after the push. Open it in a private window to confirm it loads without a login.
5. **Timestamps.** Run `bash scripts/anchor_all.sh`, commit the receipts and push. After that, change the two sentences in `web/src/app.js` that say the ledger is local, rebuild with `python -m web.build`, and push again.
6. **Deck PDF.** If you change `entrant.json`, rebuild: `python pitch/submission/build_deck.py "<official template .pptx>"`, open the result in PowerPoint and use File > Export > PDF.

## Conflict of interest (your declaration, not mine to make)
MBZUAI is one of the challenge's collaborators. The form asks whether a team member "is currently employed by, or contracted to" a collaborator.
- If you are employed by or contracted to MBZUAI in any form (staff, research assistant, paid contract), tick that box.
- If you are a student with no employment or contract, the box may not apply, but the affiliation is still worth disclosing; slide 14 of the deck does so. If unsure, ask the organisers before submitting.
- Tick "None" only if none of the listed situations is true for you.
