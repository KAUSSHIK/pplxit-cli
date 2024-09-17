#!/usr/bin/env python3
import argparse
import requests


API_URL = "https://api.perplexity.ai/chat/completions"

def query_perplexity(args, conversation_history):
    api_key = "ENTER YOUR API KEY HERE"
    if not api_key:
        print("Error: Please set the PERPLEXITY_API_KEY environment variable.")
        return

    messages = [
        {
            "role": "system",
            "content": "You are a command-line assistant. Provide concise, clear responses suitable for terminal output. Use plain text formatting. For lists, use simple dashes or numbers. Avoid markdown or complex formatting."
        }
    ] + conversation_history + [
        {
            "role": "user",
            "content": args.query
        }
    ]

    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": messages,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "return_citations": args.return_citations,
        "search_domain_filter": args.search_domain_filter,
        "return_images": args.return_images,
        "return_related_questions": args.return_related_questions,
        "search_recency_filter": args.search_recency_filter,
        "top_k": args.top_k,
        "frequency_penalty": args.frequency_penalty
    }

    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        print("\nResponse:")
        print(result['choices'][0]['message']['content'])
        
        if 'citations' in result and result['citations']:
            print("\nCitations:")
            for i, citation in enumerate(result['citations'], 1):
                print(f"{i}. {citation['title']}: {citation['url']}")
        
        if 'related_questions' in result and result['related_questions']:
            print("\nRelated Questions:")
            for i, question in enumerate(result['related_questions'], 1):
                print(f"{i}. {question}")

        return result['choices'][0]['message']['content']

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Error: Rate limit exceeded. Please wait a moment before trying again.")
        else:
            print(f"An HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Query Perplexity AI from the command line.")
    parser.add_argument("query", nargs=argparse.REMAINDER, help="The query to send to Perplexity AI")
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens in the response (optional)")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature for response generation (default: 0.2)")
    parser.add_argument("--top-p", type=float, default=0.9, help="Top P for response generation (default: 0.9)")
    parser.add_argument("--return-citations", action="store_true", help="Return citations")
    parser.add_argument("--search-domain-filter", nargs="*", default=["perplexity.ai"], help="Search domain filter (max 3 domains)")
    parser.add_argument("--return-images", action="store_true", help="Return images")
    parser.add_argument("--return-related-questions", action="store_true", help="Return related questions")
    parser.add_argument("--search-recency-filter", choices=["month", "week", "day", "hour"], default="month", help="Search recency filter (default: month)")
    parser.add_argument("--top-k", type=int, default=0, help="Top K (default: 0)")
    parser.add_argument("--frequency-penalty", type=float, default=1.0, help="Frequency penalty (default: 1.0)")
    
    args = parser.parse_args()
    args.query = " ".join(args.query)
    args.search_domain_filter = args.search_domain_filter[:3]  # Limit to max 3 domains
    
    if not args.query:
        parser.print_help()
        return
    
    conversation_history = []
    while True:
        response = query_perplexity(args, conversation_history)
        if response:
            conversation_history.append({"role": "user", "content": args.query})
            conversation_history.append({"role": "assistant", "content": response})
        
        follow_up = input("\nDo you want to ask a follow-up question? (y/n): ").lower().strip()
        if follow_up != 'y':
            print("Chat ended. Goodbye!")
            break
        
        args.query = input("Enter your follow-up question: ")

if __name__ == "__main__":
    main()