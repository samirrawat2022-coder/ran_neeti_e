# RAN-NEETI — Research Synthesis Build

## What this build does
- Home Dashboard
- Real Sports Lab: matchup inputs, sport/format, venue, competition/date, context and advanced instructions
- Anime & Fictional Battles: matchup type, universe, character versions/story arcs and scenario rules
- MediaWiki entity lookup; Jikan character lookup with MediaWiki fallback
- Public web research retrieval through Brave Search Web API (ranked web results, publisher domains, snippets, extra snippets and source URLs)
- Gemini text-only analysis over the retrieved evidence; no Google Search grounding tool is enabled in Gemini requests
- Structured report: matchup identification, evidence/current context, outcome estimate, strengths/weaknesses, major moves, turning points, win conditions, outcome paths, uncertainty and references
- Recent Reports session history and Markdown downloads
- API connection test and clearer quota/network errors

## Important: how search and AI work
RAN-NEETI retrieves public search-result references and entity metadata first. Gemini then independently synthesizes the supplied evidence into a new RAN-NEETI report. The app does not copy Google's AI Overview or represent a publisher's text as original writing. The final report includes source links so readers can inspect the underlying evidence.

The search implementation currently uses Google News RSS, which is useful for news/current updates but is **not equivalent to full Google Search or Google AI Overviews**. It may miss official statistics, match scorecards, injury reports, niche sources, or older evergreen material. Search snippets are incomplete; important claims should be checked at the publisher's page. When search retrieval fails or returns no results, the app must say so rather than pretending it searched.

## Deploy
1. Extract the ZIP.
2. Upload the contents of `RAN_NEETI_Full_Build/` to the root of a GitHub repository.
3. Deploy `app.py` using Streamlit Community Cloud.
4. In App settings → Secrets, add:

```toml
GEMINI_API_KEY = "YOUR_PRIVATE_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
BRAVE_SEARCH_API_KEY = "YOUR_PRIVATE_BRAVE_SEARCH_API_KEY"
```

Keep the model setting only if that exact model ID is available to your API key/project. If Google reports `model not found`, choose a currently available model ID in the `GEMINI_MODEL` secret. Never commit either API key to GitHub. Obtain a Brave Search API key from the Brave Search API dashboard and store it only in Streamlit Secrets. Brave documents the `X-Subscription-Token` header for authentication and the `/res/v1/web/search` endpoint; check the current plan, credits and usage in your Brave dashboard.

## API and quota notes
- Gemini requests are text-only and do not enable paid Google Search grounding.
- Removing Search grounding does not make Gemini unlimited or guarantee that the free tier is available for every model/region/account.
- HTTP 429 means quota/rate limit; retries cannot bypass exhausted quota. Check the exact API error and model quotas.
- Brave Search, Jikan and MediaWiki endpoints can rate-limit or be unavailable. Brave Search is metered; its plan and free-credit terms can change, so verify current pricing and usage in your dashboard.

## Academic limitation
This is an AI-assisted research/reporting prototype. It does not contain trained sport-specific ML models, historical model-training pipelines, calibrated probability forecasts, or validated accuracy metrics. Sports percentages are qualitative AI estimates. Fictional matchup percentages are subjective scenario interpretations.

## Verification
Python syntax compilation and offline mocked tests are performed on the delivered source. A live end-to-end test still requires internet access, a valid Gemini API key, model access and remaining quota in the deployment environment.

## Offline regression test
Run `python tests/test_research_pipeline_offline.py` in an environment with `requests` installed. This test mocks network calls and checks Brave Search response parsing, evidence formatting, prompt construction and that Gemini requests do not include Google Search grounding. It does not validate live third-party services.


## Test-path fix
The offline regression test now locates `app.py` whether the test is run from
`tests/`, from the repository root, or when the project is nested one folder
inside the repository. This avoids the `FileNotFoundError` caused by assuming
`parents[1]` always points to the application root.


## Brave Search setup
1. Create/activate a Brave Search API plan and generate an API key in the official Brave Search API dashboard.
2. Add `BRAVE_SEARCH_API_KEY` to Streamlit Cloud Secrets alongside `GEMINI_API_KEY`.
3. In the sidebar, use **TEST BRAVE SEARCH** to verify that the key returns results.
4. Each matchup performs several targeted searches; monitor usage and billing in Brave.
