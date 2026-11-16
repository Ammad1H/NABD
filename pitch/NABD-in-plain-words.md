# NABD in plain words

A short guide for telling the story. No statistics background needed. Every number here comes from the project's result files.

## What NABD is, in one breath

NABD (نبض, "pulse") tells a hospital or a public-health officer how bad RSV and flu are likely to be in the UAE over the next three weeks, how sure it is, and what to do about it. A person always makes the final call.

- **RSV** is a common winter virus. It is the main reason babies end up in hospital with breathing trouble.
- **Influenza** is the flu.

## The problem

Every Monday in winter, someone in a hospital decides how many beds and nurses to prepare for the next few weeks. Today they guess from two things: last week's numbers, and what happened last year.

That guess is risky, because the timing and shape of UAE seasons change from year to year. One year flu peaked in October. The year before it peaked in February, after a five-month plateau.

The cost is real. One Abu Dhabi hospital (Tawam) admitted 2,189 children aged five or under with RSV in five years. In Dubai insurance data, 22% of under-twos with RSV went to hospital, and almost none of them had a known risk factor. These are ordinary families.

## Why the obvious solution does not work

The obvious idea is: take the UAE's past data and train a model on it.

The UAE's public record only starts in 2022. That is four winters. Four examples are not enough for a model to learn what a season looks like.

This was tested, not assumed. A model trained only on the UAE's record did no better than simply saying "next week will look like last week". It was a tie.

## The idea: "the pool"

Think of two doctors.

- The first has worked four winters in one clinic.
- The second has seen hundreds of winters in 46 countries. They have never worked in your clinic, but they know how a flu season usually rises, peaks and fades.

Give the second doctor your last few weeks of numbers, and they will read your season better than the first.

That is the pool. NABD trains **one model on the WHO records of 46 countries**, then applies it to a country with little history. The country brings its recent weeks. The model brings the experience. The project calls this **borrowed strength**.

So when you see these words:

| Word | Meaning |
|---|---|
| Pooled model, NABD-Pool | The model that learned from 46 countries together |
| Own-record model | A model that learned from one country's data only |
| "Repeat last week" | The simplest possible forecast: next week equals last week |

## How do we know it works?

It was tested like a sealed exam.

1. The test plan was written down and locked before any test data were downloaded.
2. The model was finished and locked before a single row of test data was opened.
3. The test used **18 countries whose data had not been opened**, not the 46 the model learned from.
4. It was scored once. No second attempts.

The result:

- **23% less forecast error** than each country's own-record model.
- **Better in 18 out of 18 countries.**
- **38% less error where the country had little history.** That is the UAE's situation.
- It also beat "repeat last week" in all 18 countries, by 12%.

A second check: a large general-purpose AI forecasting model from Amazon (Chronos-2), used as it comes, scored about the same as NABD's small model. Two different methods agreeing is a good sign that the gain is real.

## What the user sees each week

One card, in Arabic and English:

- A chart of where RSV and flu are heading, shown as a range, not a single line.
- The chance of crossing each "pressure" level.
- One proposed action for each role (hospital operations, public-health duty officer, occupational health).
- An approval step. A named person approves, changes or dismisses the action and gives a reason. That decision is saved in a chained log: each entry carries the fingerprint of the one before, so an edit anywhere shows up.

Nothing is sent out without a human.

## The sealed envelope (the "ledger")

Anyone can claim their forecast was right after the fact. NABD does not allow itself that.

Every week, the forecast is saved and given a digital fingerprint (a "hash") **before** WHO publishes the real number. If even one digit of the forecast were changed later, the fingerprint would no longer match. Anyone can check this on the web page with one button.

It is like putting your prediction in a sealed, dated envelope before the match is played.

The UAE test itself is also locked in advance. It runs all this winter and is judged once, on or after 15 April 2027.

## What is unusual about it

These are the points people tend to remember.

1. **It is built for a country with almost no data.** Most forecasting tools need a long history. NABD is designed for the place that does not have one, and gains the most exactly there (38%).
2. **18 out of 18.** Not better on average. Better in every single test country.
3. **It shows its losses.** In the US it set itself a bar against the CDC's combined forecast and missed it. That result is on the page next to the wins. Very few entries will show a failed test.
4. **It ties its own hands.** Plans are locked before data. Forecasts are sealed before the answer exists. The UAE test is locked before its first data point.
5. **Small and open.** The model runs in seconds on a laptop. Every forecast can be traced back to its inputs. It matched a 120-million-parameter model.
6. **A person decides.** The system proposes; a named human approves.
7. **No personal data.** Only weekly totals. Patient-level fields are rejected automatically.

As far as the research for this project found, there is no public RSV or flu forecast for the UAE today.

## What NABD does not claim

Know these before a judge asks. Saying them yourself builds trust.

- **There is no UAE proof for the pooled model yet.** The 18-country result is strong evidence that the method works for short-record countries. The UAE's own proof can only come from this winter's sealed test. Until it reports, the official weekly forecast still comes from the own-record model, and the pooled model runs beside it as the challenger.
- **It does not warn earlier that a wave is starting.** It forecasts how high and how long.
- **It forecasts lab test results** (the share of samples that test positive), not hospital beds directly. Turning that into beds needs a hospital's own counts, which is what the pilot is for.
- **For staffing decisions, it is not clearly better than "repeat last week".** It is better than the own-record model and much better than planning from last year's pattern.
- **No hospital has used it.** It is a working prototype on public data.
- **Zero weeks are scored on the live ledger so far**, because WHO has not yet published the first target week.
- **The seals are not yet independently dated.** Until the repository is public and the fingerprints are stamped by an outside timestamp service, the dates are the project's own word. Do not say "published" or "cannot be rewritten" before that is done.

## If a judge goes through the six requirements

The challenge brief lists six things. Here is the honest answer for each, in one line. The page has a section called "The brief" that shows the same.

| They ask for | Your answer |
|---|---|
| Several kinds of signal | Partly. Today it reads lab results and testing volume. School breaks and Ramadan were tried and did not help, and that is reported. Hospital counts come with the pilot. |
| Explainable detection | Partly. Every forecast shows exactly which input pushed it up or down and by how much. It cannot say which emirate, because WHO data are national. |
| A clear action and a named role | Yes. One action per role, a named person approves, and the decision is logged. |
| Privacy | Partly. Only weekly totals; anything about a person is rejected; small counts are hidden. Logins per role are not built yet. |
| Proof it works in operation | Yes. Tested as an alert on 36 past seasons: it caught 80% of surge weeks two weeks ahead, and 58% of its calls were needed. Repeating last week caught a little more (84%) but wasted more calls. |
| Health impact | Not measured yet. That is what the twelve-week hospital pilot is for. |

## The ask

One hospital. Twelve weeks. Weekly totals only. Shadow mode, meaning NABD runs quietly beside normal practice and changes nothing in patient care. The pass mark is set in advance. If NABD misses it, the hospital walks away.

## The story in 30 seconds

"Every Monday, someone in an Abu Dhabi hospital decides how many beds to prepare for sick children. They guess from last week and last year, but UAE seasons change timing and shape from year to year. The UAE has only four winters of data, too few for any model to learn from. So NABD learns from 46 other countries and brings that experience here. On 18 countries it had never seen, it cut forecast error by 23%, and it won in all 18. Every forecast is sealed before the real number comes out, and the tests it lost are shown next to the ones it won. It needs one hospital and twelve weeks to prove itself here."

## Three numbers to remember

- **2,189** children admitted with RSV at one Abu Dhabi hospital in five years.
- **23%** less forecast error, **38%** where data are short.
- **18 of 18** countries.

## Words you may hear

| Word | Plain meaning |
|---|---|
| Sentinel data | Numbers from a fixed set of clinics and labs that report to WHO every week |
| WHO FluNet | WHO's public database of those weekly numbers |
| Forecast error | How far the forecast was from what happened. Lower is better |
| 0.767 | The pooled model's error divided by the own-record model's error. Below 1 means better; 0.767 means 23% less |
| 95% interval (0.681 to 0.832) | The range the true value very likely sits in. All of it is below 1, so the win is not luck |
| Pre-registered | The test rules were written and locked before seeing the data |
| Post hoc | An analysis added afterwards. Useful, but weaker evidence, and labelled as such |
| Held-out countries | Countries kept aside for the test, never used for training |
| Hash | A digital fingerprint of a file. Change the file and the fingerprint changes |
| Ledger | The list of sealed weekly forecasts with their fingerprints |
| Foundation model | A very large AI model trained on huge amounts of general data |
| Shadow pilot | A trial that runs alongside normal work without affecting care |
