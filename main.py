#!/usr/bin/env python3
import sys
import argparse
from data.fetch_data import load_comments
from model.analyzer import analyze_sentiment, analyze_batch, summary_statistics


def cmd_analyze(args):
    result = analyze_sentiment(args.text)
    print(f"Teks    : {result['text']}")
    print(f"Sentimen: {result['label']}")
    print(f"Skor    : {result['score']}")
    if result.get("positive_words"):
        print(f"Kata positif: {', '.join(result['positive_words'])}")
    if result.get("negative_words"):
        print(f"Kata negatif: {', '.join(result['negative_words'])}")


def cmd_comments(args):
    comments, source = load_comments(args.days, args.limit, args.keyword)
    results = analyze_batch(comments)
    summary = summary_statistics(results)

    print(f"Sumber data: {source}")
    print(f"Total komentar: {summary['total']}")
    print(f"Positif: {summary['positif']}  Negatif: {summary['negatif']}  Netral: {summary['netral']}")
    print()

    for i, r in enumerate(results, 1):
        icon = {"positif": "+", "negatif": "-", "netral": "="}[r["label"]]
        print(f"{i:>3}. [{icon}] ({r['label']:>7}, {r['score']:>+.4f}) {r['text'][:]}")
        if args.verbose:
            if r.get("positive_words"):
                print(f"     positif: {', '.join(r['positive_words'])}")
            if r.get("negative_words"):
                print(f"     negatif: {', '.join(r['negative_words'])}")


def cmd_serve(args):
    import uvicorn
    uvicorn.run("api.server:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(description="Indonesian Sentiment API")
    parser.add_argument("--version", action="version", version="1.0.0")
    sub = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    p_analyze = sub.add_parser("analyze", help="Analisis sentimen satu teks")
    p_analyze.add_argument("text", help="Teks yang akan dianalisis")
    p_analyze.set_defaults(func=cmd_analyze)

    p_comments = sub.add_parser("comments", help="Analisis sentimen komentar dari data")
    p_comments.add_argument("--days", type=int, default=20, help="Rentang hari")
    p_comments.add_argument("--limit", type=int, default=50, help="Jumlah komentar")
    p_comments.add_argument("--keyword", default="BBM", help="Kata kunci pencarian")
    p_comments.add_argument("--verbose", "-v", action="store_true", help="Tampilkan detail kata")
    p_comments.set_defaults(func=cmd_comments)

    p_serve = sub.add_parser("serve", help="Jalankan API server")
    p_serve.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    p_serve.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    p_serve.add_argument("--reload", action="store_true", help="Auto-reload saat ada perubahan")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
