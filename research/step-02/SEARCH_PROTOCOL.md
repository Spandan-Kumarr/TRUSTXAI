# Search protocol and audit trail

Search date: 26 October 2026. Scope: bounded evidence review for the supplied thesis title and Review 2 proposal. Status: interim; scholarly-host access prevents priority full-text verification.

## Sources actually used

1. User-supplied full PDFs: Bello et al. and Randl et al.
2. Official ACL Anthology bibliographic XML hosted in acl-org/acl-anthology, accessed through raw.githubusercontent.com.
3. Actual author/institutional GitHub repositories, their READMEs, cited metadata and selected implementation/metric files. Search results or third-party lists were discovery aids, not primary evidence for paper conclusions.

No Google Scholar, Scopus, Web of Science, ACM, Crossref or publisher-site search is represented as completed. No full text was fetched through an unauthorized proxy. Direct scholarly requests were blocked; permitted GitHub sources were accessed normally with TLS verification.

## Metadata-screen procedure

Exact title-screen regex (case-insensitive):

`explan|faithful|counterfactual|rationale|appropriate reliance|overreliance|calibrat.*trust|trust.*calibrat`

Read all paper titles in the retrieved specified collections; retain matches with title, abstract where present, authors, year, volume/booktitle, DOI where supplied, pages and source URL. This title-only pass does not establish that every relevant abstract was retrieved or manually reviewed.

Collection requests are recorded individually in evidence/acl_fetch_log.json with timestamp, response/error, size and SHA-256 for successful files. The requested series include selected ACL, EMNLP, NAACL, EACL, COLING, Findings and TACL collections for 2019–2026. This is deliberately reported as specified coverage, not every publication in every series/year.

- 40 collection URL attempts.
- 30 successful collection downloads.
- 10 failed requests used incorrect separate Findings filenames and returned 404; corrected unified annual Findings files were then retrieved.
- 38,613 paper records in the 30 successful selected collections.
- 754 title matches in the recorded regex screen.
- 38 curated unique evidence records after thematic/citation/repository tracing and deduplication.

The 38 curated records are not a formal inclusion/exclusion assessment of all 754 hits. Some additional foundation records were recovered by exact-title citation tracing within downloaded metadata or selected official records, even when their titles did not match the regex. No PRISMA flow or exhaustiveness claim is made.

Full downloaded XML is retained in /workspace/thesis-reference/literature-cache. The project evidence directory retains the keyword-hit metadata, selected record abstracts, fetch logs and source hashes. Raw source branches are mutable: hashes and local snapshots identify the actual content reviewed; URLs alone are not immutable version pins.

## Targeted search and tracing themes

The thematic notes document actual repositories and evidence URLs for faithful self-explanations, natural-language XAI, SHAP narrative translation, critique/refinement, text counterfactual generation, conversation, audience tailoring and human evaluation. Representative GitHub discovery searches included faithfulness/explanations/LLM, specific paper titles and known method names. A complete ranked search-engine result export was not available, and no invented query-result counts are reported.

Citation tracing started from the supplied papers, then followed primary method/code references. Agarwal2024, Lanham2023 and other unresolved leads remain in PRIORITY_READING.csv rather than being presented as directly reviewed papers.

## Inclusion and exclusion logic

Include direct methodological competitors, conceptual/evaluation foundations and task-relevant system studies. Keep adjacent approaches when needed to explain a scope boundary. Prioritize primary paper metadata, official abstracts and author releases.

Exclude duplicates, repository mirrors without primary provenance, generic model releases, unrelated computer-vision/audio papers that match keywords, and unsupported claims based only on search snippets. RAG answer factuality is not automatically the same construct as faithfulness to an LLM classifier's decision. Some adjacent agent/clinical records are retained as clearly labelled motivation or architecture comparators.

## Evidence-depth coding

- F: user-supplied full paper analysed; two base papers.
- A/R: official abstract/metadata and/or author repository inspected; full text not read unless explicitly indicated.
- R: author repository provides the evidence; archival metadata may remain provisional.

Selected source-code reading is separately stated and is not full-paper review or experimental reproduction. Statements about absent features mean only that inspected sources do not establish the feature; absence from an abstract or README does not prove absence from the paper.

## Network limitation and draft

Direct checks to ACL Anthology, arXiv, Springer, Crossref and Google search failed with proxy tunnel 403. The network-permission tool granted turn-level network permission, but a retry showed the proxy allowlist still blocked scholarly hosts. GitHub/raw GitHub succeeded. A subsequent draft save was confirmed with status saved and requires_publish true; no runtime application or publication was performed.

Saved custom domains: aclanthology.org, arxiv.org, export.arxiv.org, api.crossref.org, doi.org, link.springer.com, www.nature.com, openreview.net, api2.openreview.net, proceedings.neurips.cc, proceedings.mlr.press, dl.acm.org, api.openalex.org, api.semanticscholar.org, www.google.com, www.bing.com. Existing custom rules were empty; package-manager presets and unrelated fields were preserved.

The remaining task is to activate supported network settings, retry authoritative full texts and verify the nearest-method comparison. This limitation must remain visible in summaries and novelty discussions.


## Continuation —26–27October2026

The earlier network blocker is resolved: direct ACL PDF/arXiv/Crossref reads succeeded. This historical protocol section is retained; it does not describe the current blocker state. The library now contains43records and19full-text audits including the supplied base papers. Additional source retrieval is logged in evidence/fulltext_fetch_log.json and evidence/continuation/. New INLG citation tracing adds a collection outside the initial30-collection screen; no revised exhaustive corpus count is asserted. Four Crossref discovery requests produced two successful result sets, one429 and one500. Google returned an interstitial, not usable results. Downloaded-but-not-audited PDFs are not counted as full-text reviews. See the version2report for corrected method/metric interpretations.
