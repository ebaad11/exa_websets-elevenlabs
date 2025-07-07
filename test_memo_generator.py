from memo_generator import MemoGenerator

def main():
    # Initialize the MemoGenerator
    mg = MemoGenerator()
    
    # Generate the memo from the specified JSON file
    mg.generate(
        input_file="/Users/ebaad69/Desktop/Exa-projects/exa+elevenlabs/websites/series_a_companies_2025-07-03.json",
        output_file="company_memo.txt",
        prompt_template=(
            "Instructions: Create a concise audio-friendly summary with NO links or citations. " 
            "Start with 'Hello, here is your summary of companies that raised their Series A this week.' " 
            "For each company, mention only their name, core offering, and funding amount in plain text format. " 
            "Do not include any URLs, citations, or references in the output:\n\n{items}\n\n"
        )
    )

if __name__ == "__main__":
    main()
