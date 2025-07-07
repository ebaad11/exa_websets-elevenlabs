import os
import json
import argparse
import re
from dotenv import load_dotenv
import requests
import sys

class MemoGenerator:
    """
    Generates memos from a list of webset items using Exa AI Answers API.

    Usage:
        from memo_generator import MemoGenerator
        mg = MemoGenerator()
        mg.generate(
            input_file='webset_items.json',
            output_file='company_memo.txt',
            prompt_template=(
                "Draft a concise memo summarizing each company below, "
                "including name, description, and funding size:\n\n{items}"
            )
        )
    """

    API_URL = "https://api.exa.ai/answer"

    def __init__(self, api_key: str = None):
        """
        Initialize the generator. Loads EXA_API_KEY from environment if not provided.
        """
        load_dotenv()
        self.exa_api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.exa_api_key:
            raise ValueError("EXA_API_KEY not found. Please set it in your .env file or pass it explicitly.")

    def _remove_links(self, text: str) -> str:
        """
        Remove URLs and markdown links from text to make it suitable for audio playback.
        
        :param text: The text to process
        :return: Text with all links removed
        """
        # Remove markdown links - pattern: [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove bare URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove citations like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Clean up any double spaces created by removing links
        text = re.sub(r'\s{2,}', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text
        
    def _extract_items_block(self, items: list) -> str:
        lines = []
        for itm in items:
            # Extract company name from properties or use URL as fallback
            name = "<Unknown>"
            properties = itm.get("properties", {})
            
            if "company" in properties and isinstance(properties["company"], dict) and "name" in properties["company"]:
                name = properties["company"]["name"]
            elif "url" in properties:
                # Use domain name as fallback
                url = properties["url"]
                name = url.replace("https://", "").replace("http://", "").split("/")[0]
                
            # Get description and extract funding if available
            desc = properties.get("description", "").strip().replace("\n", " ")
            funding = ""
            if "$" in desc:
                # Extract funding amount - find text after $ and take the first "word"
                try:
                    segment = desc.split("$", 1)[1]
                    funding = "$" + segment.split()[0]
                except (IndexError, ValueError):
                    funding = "Unknown"
                    
            lines.append(f"- **{name}**: {desc}  \n  Funding: {funding}")
        return "\n".join(lines)

    def generate(self, input_file: str, output_file: str, prompt_template: str = None):
        """
        Read items from input_file, call Exa API, and write the memo to output_file.

        :param input_file: Path to JSON file with a single object or list of objects.
        :param output_file: Path where the resulting memo will be saved.
        :param prompt_template: Template string containing '{items}' placeholder.
        """
        try:
            # Load items
            with open(input_file, 'r') as f:
                data = json.load(f)
            items = data if isinstance(data, list) else [data]
            
            # Validate we have items to process
            if not items:
                print(f"Warning: No items found in {input_file}")
                return
                
            # Print item count for verification
            print(f"Processing {len(items)} companies from {input_file}")

            # Prepare prompt
            items_block = self._extract_items_block(items)
            prompt = (prompt_template or
                    "Create a concise memo summarizing each company below, including name, description, and funding size raised:\n\n{items}")
            prompt = prompt.format(items=items_block)

            # Call Exa API
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "query": prompt,
                "includeGeneratedQuery": False,
                "max_results": 0
            }
            
            print("Sending request to Exa API...")
            resp = requests.post(self.API_URL, headers=headers, json=payload)
            
            # Check if request was successful
            resp.raise_for_status()
            
            # Parse response
            response_data = resp.json()
            memo = response_data.get("answer", "")
            
            if not memo:
                print("Warning: Empty response from Exa API")
                memo = "No memo could be generated. Please check your API key and try again."
            
            # Remove links from the memo
            memo = self._remove_links(memo)

            # Write output
            with open(output_file, 'w') as out:
                out.write(memo)

            print(f"✅ Memo successfully written to {output_file}")
            return memo
            
        except requests.exceptions.HTTPError as e:
            print(f"Error: HTTP request failed: {e}")
            print(f"Response content: {e.response.content.decode() if hasattr(e, 'response') else 'Unknown'}")
            sys.exit(1)
            
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON response: {e}")
            sys.exit(1)
            
        except Exception as e:
            print(f"Error generating memo: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a memo from a JSON list of webset items using Exa AI."
    )
    parser.add_argument("input_file", help="Path to JSON file containing the item(s).")
    parser.add_argument("output_file", help="Where to write the resulting memo.")
    parser.add_argument(
        "-p", "--prompt",
        help=(
            "Custom prompt template with '{items}' placeholder. Example:\n"
            "  'Draft a one-page summary of these companies:\n{items}'"
        )
    )
    args = parser.parse_args()

    mg = MemoGenerator()
    mg.generate(
        input_file=args.input_file,
        output_file=args.output_file,
        prompt_template=args.prompt
    )
