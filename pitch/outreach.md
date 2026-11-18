# Outreach drafts (do NOT send automatically; the author sends these personally)

**Rules:**
- Fill ⟨…⟩ before sending. Each email body is under 150 words (counted).
- Use public contact routes only. Confirm names and affiliations on the source page the day you send.
- Never imply an endorsement that hasn't been given.

---

## A1. Letter of interest: the Tawam RSV study team (UAEU, Department of Pediatrics)

**Who and why:**
- The study is Alamiri H.A., … Narchi H., Alsuwaidi A.R., *RSV seasonality in the UAE: a five-year study at a tertiary care hospital, 2018–2022*, J Infect Public Health 2025;18(12):103007. It is our burden anchor (2,189 admissions) and is directly about seasonality.
- The UAEU publication record lists the units as the Department of Pediatrics and the Institute of Public Health. Its citation metadata gives a contact address for Dr Ahmed R. Alsuwaidi: https://research.uaeu.ac.ae/en/publications/epidemiological-characterization-and-seasonality-of-respiratory-s/
- **Check the journal page for the designated corresponding author before sending, and write to that person.** Otherwise use the UAEU research contact page (https://research.uaeu.ac.ae/en/contact/index/).

**Subject:** Your Tawam RSV seasonality study, and a 12-week shadow forecast test

Dear Dr Alsuwaidi,

Your 2025 paper on RSV seasonality at Tawam Hospital is the anchor for our Future Health Challenge entry. NABD is an open forecasting tool I am building at MBZUAI as a solo entrant. It turns WHO FluNet UAE data into probabilistic RSV and flu forecasts up to three weeks ahead, with every forecast hashed before its outcome exists.

We'd value either of two small things:
1. Thirty minutes of your team's view on whether our forecast card and action playbook make clinical sense. We'd credit you only with permission.
2. A non-binding line of interest in a 12-week shadow test after the Challenge, on aggregate weekly paediatric RSV counts. Shadow means no decisions depend on it, and no patient-level data is involved.

A two-page summary is attached. The prototype is due 20 November.

With thanks,
⟨Name⟩, MBZUAI · ⟨phone⟩ · ⟨repo link, once public⟩

---

## A2. The same request to a SEHA/SSMC/SKMC paediatric ED or bed-management lead

**Subject:** 12-week shadow test of RSV/flu forecasts (aggregate counts only)

Dear Dr ⟨Name⟩,

I am building NABD, as a solo entrant from MBZUAI, for the Future Health Digital Innovation Challenge. Each week NABD gives the probability that RSV or flu activity crosses a pressure threshold in each of the next weeks, and which way it is heading. A named person approves any action.

Our ask is small: a one-paragraph, non-binding note saying your department would consider a 12-week shadow test after the Challenge, on aggregate weekly counts. Forecasts would be produced and scored, but no decisions would depend on them. No data moves now.

Published Abu Dhabi data shows the scale. Tawam recorded 2,189 RSV admissions in children aged five and under in 2018–2022, and positivity varied widely by year (the period includes the pandemic years).

Could I send a two-page summary, or take 15 minutes of your time?

With thanks,
⟨Name⟩, MBZUAI · ⟨phone⟩

---

## A3. MBZUAI-affiliated clinician or faculty

**Subject:** Quick favour: clinical sanity-check of a Future Health entry's action playbook

Dear Dr ⟨Name⟩,

I'm an MBZUAI student entering the Future Health Digital Innovation Challenge (Statement 06). Our project, NABD, produces probabilistic RSV and flu forecasts for the UAE from WHO FluNet data, and reports coverage and failures openly. In a test on three Gulf countries, with the plan locked before their data were downloaded, it beat last-week carry-forward for influenza. In the US it missed the bar we set against the CDC ensemble, and we report that too.

Two optional asks:
1. 20 minutes to sanity-check our one-page action playbook (rostering, beds, advisories). We'd credit you only with permission.
2. An introduction to a paediatrics or bed-management lead who might consider a post-Challenge shadow test.

The prototype is due 20 November.

Thank you,
⟨Name⟩ · ⟨programme⟩

---

## A4. 48-hour quote request (18–20 Nov 2026): one sentence from a clinician or bed manager

**Who.** A paediatric, emergency, infection-control or bed-management lead at an Abu Dhabi hospital (SEHA, SSMC, Cleveland Clinic Abu Dhabi, Tawam, Danat Al Emarat, NMC, Burjeel), reached by LinkedIn message, WhatsApp or email. **Prefer someone outside MBZUAI:** the deck's conflict-of-interest slide says no MBZUAI staff member contributed to or reviewed NABD; a quote from MBZUAI staff would make that sentence untrue, so change slide 14 (`pitch/submission/entrant.json`, `coi_paragraphs`) first if you use one.

**Message (LinkedIn or WhatsApp, 91 words):**

> Dear Dr ⟨Name⟩, I'm an MBZUAI student entering the Future Health challenge (DoH Abu Dhabi, deadline 20 Nov). My entry, NABD, forecasts UAE RSV and flu test positivity about two to three weeks ahead, with ranges, from WHO data: ⟨https://ammad1h.github.io/NABD/⟩. One question, answerable in a sentence: would a weekly heads-up like this change any staffing, bed or cohorting decision you make in the respiratory season, and if so which? May I quote your answer with your name and role (or role only)? A "no, because…" is equally useful. Thank you, Ammad

**If you get a quote:** paste it, with the person's permission and wording exactly as given, into (1) the README under "Why it matters", (2) deck slide 5 under "Who benefits" (`pitch/submission/build_deck.py`, `s5`), and (3) the form summary in place of the sentence "An off-the-shelf foundation model (Chronos-2) lands level with it on the held-out test." (re-run `python pitch/submission/count.py`; the limit is 2,000 characters). Add a claims-ledger row (status V, source: "personal communication, ⟨date⟩"). Never edit the wording, and never imply that the person or their hospital endorses NABD.

---

## B. Playbook review: ADPHC / DoH communicable-disease surveillance

**Who and why:**
- The role is surveillance and outbreak response at DoH Abu Dhabi / ADPHC. DoH's Director of Surveillance and Outbreak Response, Dr Mahra Alhosani, gave the public season update in Sep 2026 ([S7], `research/positioning-sources.md`).
- **Send only through official public channels:** the DoH (doh.gov.ae) or ADPHC website contact forms, or a referral via MBZUAI's partnerships office. No private addresses.

**Subject:** Request: review of a one-page respiratory forecast playbook (Future Health Challenge entry)

Dear Dr Alhosani (or the Communicable Diseases Surveillance team),

I am building NABD at MBZUAI, as a solo entrant, for the Future Health Digital Innovation Challenge. It is a forecast layer for seasonal RSV and influenza, designed to sit alongside Tableegh and UMOC rather than replace them. Each forecast tier maps to a proposed action for a named role, such as an ADPHC duty officer or a hospital bed manager, and a person must approve, modify or dismiss it with a logged reason.

Would your team review the one-page playbook (attached) and flag anything operationally wrong? A two-line reply is plenty. We'll say "reviewed by a public-health professional" only with your permission. Until then it stays marked "illustrative".

Ideally by 17 November, if possible.

Respectfully,
⟨Name⟩, MBZUAI · ⟨contact⟩

---

## C. LinkedIn / X post: forecast ledger. Post ONLY after the repo is public and the manifest is anchored

> Our first **NABD** forecast round for UAE RSV and flu positivity is now public. It was hashed before the outcome existed and timestamped with ⟨OpenTimestamps/Zenodo⟩.
> 🔒 Merkle root: `⟨root⟩` · 📂 ⟨public repo URL⟩ (commit `⟨short-sha⟩`)
> We'll score every round against WHO FluNet as data arrives, misses included.
> Built by a solo entrant at MBZUAI for the #FutureHealth Digital Innovation Challenge (Statement 06). Data: WHO FluNet (public-health, non-commercial use) · CDC FluSight hub.

X/short version (≤280 characters):
> NABD forecast round for UAE RSV + flu, hashed before the outcomes exist and anchored ⟨date⟩. Merkle root `⟨first 16⟩…` · ⟨repo⟩. We'll score every round, misses included. #FutureHealth

---

**Measured body word counts:** A1 140 · A2 143 · A3 126 · B 125 (whitespace tokens, salutation to sign-off; recount after filling the ⟨…⟩).
