from datetime import datetime, timezone

from analyzer import GeminiAnalyzer
from sources.contestkorea import ContestKoreaSource
from storage import SupabaseStorage
from utils import looks_ai_related, looks_creative, make_fingerprint, normalize_space

def main():
    print("=== AI Contest Radar ===")

    sources = [

        ContestKoreaSource(),

    ]

    analyzer = GeminiAnalyzer()
    storage = SupabaseStorage()

    stats = {
        "discovered": 0,
        "prefiltered": 0,
        "analyzed": 0,
        "saved": 0,
        "skipped": 0,
        "errors": 0,
    }

    seen_urls = set()

    for source in sources:
        print(f"\n--- source: {source.name} ---")
        try:
            urls = source.discover()
        except Exception as exc:
            print(f"[ERROR] discover {source.name}: {exc}")
            stats["errors"] += 1
            continue

        stats["discovered"] += len(urls)
        print(f"discovered links: {len(urls)}")

        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                raw = source.fetch_detail(url)
                combined = f"{raw.title}\n{raw.body}"

                # Free prefilter: AI mention is required before calling Gemini.
                # Creative keyword is a weak additional signal; AI-only technical contests
                # are later rejected by the model.
                if not looks_ai_related(combined):
                    stats["skipped"] += 1
                    continue

                stats["prefiltered"] += 1
                analysis = analyzer.analyze(raw.title, raw.body)
                stats["analyzed"] += 1

                # Keep AI-policy-relevant creative contests. Prohibited contests are also
                # stored for research but hidden by default in the web UI.
                if not analysis.is_creative_contest or not analysis.ai_relevant:
                    stats["skipped"] += 1
                    continue

                title = normalize_space(raw.title)
                fingerprint = make_fingerprint(
                    title,
                    analysis.organizer or "",
                    analysis.deadline or "",
                )

                payload = {
                    "fingerprint": fingerprint,
                    "title": title,
                    "organizer": analysis.organizer,
                    "deadline": analysis.deadline,
                    "prize_text": analysis.prize_text,
                    "total_prize_won": analysis.total_prize_won,
                    "eligibility": analysis.eligibility,
                    "categories": analysis.categories,
                    "ai_requirement": analysis.ai_requirement,
                    "ai_reason": analysis.ai_reason,
                    "ai_confidence": analysis.confidence,
                    "summary": analysis.summary,
                    "source": raw.source,
                    "source_url": raw.source_url,
                    "last_checked_at": datetime.now(timezone.utc).isoformat(),
                }

                storage.upsert(payload)
                stats["saved"] += 1
                print(f"[SAVED] {title[:80]}")

            except Exception as exc:
                stats["errors"] += 1
                print(f"[ERROR] {url}: {exc}")

    print("\n=== result ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
