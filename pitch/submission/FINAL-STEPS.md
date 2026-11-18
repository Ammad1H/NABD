# Final steps before the deadline: 20 Nov 2026, 20:59 GST (22:29 IST)

What changed on 18 Nov is one commit on the branch `judge-pass-18nov`, delivered as `nabd-judge-pass-18nov.bundle` (the build sandbox could not push to GitHub). Everything below needs your laptop, your accounts or another person, so it could not be done from the build sandbox. Do them in this order.

## Today (18 Nov)

1. **Apply the commit and push** (from your NABD folder, on `main`, with the bundle in Downloads):
   ```bash
   git fetch ~/Downloads/nabd-judge-pass-18nov.bundle judge-pass-18nov:judge-pass-18nov
   git log --stat -1 judge-pass-18nov      # review
   git merge --ff-only judge-pass-18nov && pytest -q && git push origin main
   ```
   GitHub Pages redeploys the web page from `main` within a few minutes; open https://ammad1h.github.io/NABD/ in a private window and check the headline reads "one checkable forecast a week".
2. **Anchor everything now (10 min, then wait).** OpenTimestamps needs a few hours to confirm in a Bitcoin block, so stamp today, not on Friday:
   ```bash
   pip install opentimestamps-client
   scripts/anchor_all.sh
   git add anchors docs/lock_* ledger/rounds && git commit -m "Outside anchors" && git push
   ```
   Tomorrow: `for f in $(git ls-files '*.ots'); do ots upgrade "$f"; done; git commit -am "OTS upgrade" && git push`.
   Then, and only then, the words "externally timestamped on ⟨date⟩" may be used (claims ledger B4). Slide 9 still says "Timestamping by an outside service is still to do": change it to "Done ⟨date⟩ (OpenTimestamps and FreeTSA; `anchors/`)" in `pitch/submission/build_deck.py` `s9` and in the PPTX, and re-export the PDF.
3. **Send the quote request** in `pitch/outreach.md` §A4 to two or three Abu Dhabi clinicians or bed managers. One sentence back, with permission, is worth more on criterion 1 than any table.

## 19 Nov

4. **Score the ledger** once WHO has published UAE week 45 (week ending 8 Nov; expected about now on the 7-day lag logged for W44):
   ```bash
   python -m ledger.weekly --fetch --with-pool
   python -m web.build
   git add ledger results/uae/explain web/dist && git commit -m "Ledger: score W45, issue next round" && git push
   ```
   Then anchor the new round (`scripts/anchor_all.sh`). Show the **v1 receipt** (where the 8 Nov forecast landed against WHO's value) in the video and on slide 6, whichever way it fell. Do **not** quote the pooled model's live UAE numbers: `docs/PREREG-LIVE.md` §8 makes interim results descriptive only (claims ledger H13).
5. **Video.** `pitch/submission/NABD-demo-captioned.mp4` is a finished 2:58 captioned walkthrough with a silent track. Either upload it as it is (YouTube, unlisted), or record the v4 voiceover from `pitch/story.md` (324 words; about 2 min 30 s to 2 min 50 s with the pauses the screen needs) and lay it over without re-encoding:
   ```bash
   ffmpeg -i pitch/submission/NABD-demo-captioned.mp4 -i voiceover.m4a -map 0:v -map 1:a -c:v copy -c:a aac -shortest NABD-demo-voiced.mp4
   ```
   A human voice is better. If W45 was scored in step 4, re-run `pitch/video` to pick up the new ledger state.

## 20 Nov (submit by the afternoon, not at 20:59)

6. **Form.** Paste from `pitch/submission/form-answers.md` (summary 1,960 / 2,000 characters; built 1,348 / 1,500). Upload `pitch/submission/NABD-submission-deck.pdf` (16 pages, 0.8 MB). Technical documentation: `pitch/submission/draft-review/NABD-technical-documentation.pdf` (7 pages). Prototype link: https://ammad1h.github.io/NABD/. Video link from step 5.
7. **Last check.** `pytest -q` passes; every manifest verifies (`scripts/anchor_all.sh` step 1); the deck PDF opens; the page loads without a login.

## Files changed for you on 18 Nov
- Deck: `NABD-submission-deck.pptx` and `.pdf` (UAE result on slide 7, new web screenshot on slide 15, test count). The PDF was exported with LibreOffice; re-export from PowerPoint if you prefer its font rendering.
- Technical documentation PDF (UAE row in the results table, abstract, date), prototype zip, web page, form answers, story v4, README.
