# VSL stage contracts

Every stage JSON includes `schema_version: 1`, `stage`, and `dependencies` emitted
by `prepare`. Add the fields below without discarding dependencies. Unknown facts
remain null, open evidence requirements remain visible. Arrays require unique IDs.
Add `local_sources` entries with `path` and `sha256` for business, voice and other
local inputs. Paths may be absolute or relative to the run directory. Changed
source bytes block evaluation until the agent rereads the source and revises.

| Stage | Required content | Evaluation |
| --- | --- | --- |
| methods | `videos`: id, url, transcript_path, sha256; `requirements`: id, video_id, timestamp, rule, kind (editorial, research, empirical), application; `holds` | One or more distinct video IDs; exact transcript hash and video metadata; actual timestamp exists; each video represented; all requirement fields populated |
| research | `sources`: id, url, observed_on, excerpt; `quotes`: id, source_id, text, audience_fit, bias, category; `coverage`: forums, amazon_reviews, competitor_google_reviews, each status and note; `holds` | Quotes are exact substrings of observed excerpts; duplicate quotes rejected; at least three distinct source URLs; source dates and evidence limits required; unavailable surfaces stay holds |
| halo | `insights`: id, category (pain, fear, desire, objection, failed_alternative, messaging), interpretation, quote_ids, limitation; `holds` | All six categories; every insight has resolvable evidence; two source URLs for the lead messaging insight or hold |
| offer | `name`, `promise`, `cta`, `qualification`, `exclusions`, `deliverables`, `commercial`: pricing_model, price or normal_price/discounted_price, turnaround, approval_ref; `hooks`: id, angle, text, insight_ids; `test_plan`, `holds` | Five distinct named angles; evidence IDs resolve; CTA and fit rules explicit; undefined required commercial fields stay holds; fixed price positive, discounted price below supported normal price, free offer has no conflicting prices |
| script | `speaker`, `language`, `claims`: id, type (canon, proposal, illustration, inference, result), source_ref, statement; `sections`: id, purpose, text, claim_ids, requirement_ids; `alternate_hooks`: id, text; `coverage`: requirement_id, section_ids, disposition (addressed, adapted, deferred), rationale; `review`: human_writing, voice, format, each outcome, evidence, limits; `holds` | Complete nonempty sections; one CTA section; claims and method IDs resolve; all editorial requirements mapped; three opening options including main; results require proof; deferred/adapted methods retain rationale and holds; language/placeholder/risk scans are advisory guardrails |
| shots | `shots`: id, section_id, mode, visual, on_screen, assets, asset_status, production_note; `holds` | Exactly one or more shots for every script section; no orphan sections; production modes bounded; missing assets remain holds |

The evaluator checks structure and traceability, not whether a cited source
logically proves a claim. A reviewer must inspect claim entailment, quote context,
source authenticity, method coverage and visual honesty. String matching cannot
certify persuasion or factual truth. Explicitly supplied holds are never removed
by the tool.

`commercial.pricing_model` is `discounted`, `fixed`, or `free`; omission preserves
the original `discounted` behavior for existing runs. Discounted offers require
`normal_price` and `discounted_price`; fixed offers require `price`. All models
require `turnaround` and `approval_ref`. Missing approval remains a hold even for
a free offer. The agent must verify the approval reference; a populated string
does not establish authority. Do not put unapproved prices in spoken copy.

This workflow prepares a substantive teaching VSL (at least 500 spoken words),
five candidate angles, and three opening options. Short ads belong in the
consumer's short-video workflow. The default research checklist covers forums,
Amazon reviews and competitor Google reviews; unavailable or poorly matched
surfaces retain a hold and an explicit explanation rather than fake coverage.

`render` writes a numbered recording script, clean spoken text, shot-list table,
and package status. Timing is estimated at 140 words per minute; it is not a
measurement of a performance. Shot modes are talking_head,
screen_share, slide or hybrid. A slide specification counts as planned production
work, not a finished visual. `chain` rereads all stages and source hashes; it does
not trust a previous receipt's status.
