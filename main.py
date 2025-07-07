#!/usr/bin/env python3
"""
Series A Funding Newsletter Generator

This script combines several components to create an automated Series A funding newsletter:
1. Tracks recent Series A companies using Exa Websets API
2. Generates a concise memo summarizing the companies using Exa AI
3. Converts the memo to audio using ElevenLabs API
4. Sends an email with the text and audio attachment using Gmail API
"""

import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import custom components
from simple_websets import SeriesATracker
from memo_generator import MemoGenerator
from eleven_labs_tts import ElevenLabsTTS
from gmail_sender import GmailEmailSender

# Load environment variables
load_dotenv()

def main():
    """Execute the complete Series A newsletter generation and delivery workflow."""
    
    print("🚀 Starting Series A Newsletter Generation Pipeline")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Step 1: Create a directory structure if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 2: Track Series A companies and get the JSON data
    print("\n📊 Fetching Series A company data...")
    tracker = SeriesATracker(
        timeout_minutes=10,
        query="companies in SF that just raised their series A last week",
        criteria=[
            {"description": "company is headquartered in san francisco, ca"},
            {"description": "completed a series a fundraising round"}
        ],
        days_lookback=7,
        result_count=1,
        entity_type="company",
        output_dir="websites",
        file_prefix=f"series_a_companies_{timestamp}"
    )
    
    # Run the tracker to create and fetch the webset
    json_file_path = tracker.run()
    print(f"✅ Company data saved to: {json_file_path}")
    
    # Step 3: Generate a memo from the JSON data
    print("\n📝 Generating memo from company data...")
    memo_file = os.path.join(output_dir, f"company_memo_{timestamp}.txt")
    
    # Create a memo generator and generate the memo
    mg = MemoGenerator()
    mg.generate(
        input_file=json_file_path,
        output_file=memo_file,
        prompt_template=(
            "Instructions: Create a concise audio-friendly summary with NO links or citations. "
            "Start with 'Hello, here is your summary of companies that raised their Series A this week.' "
            "For each company, mention only their name, core offering, and funding amount in plain text format. "
            "Do not include any URLs, citations, or references in the output:\n\n{items}\n\n"
        )
    )
    print(f"✅ Memo generated and saved to: {memo_file}")
    
    # Step 4: Convert memo to audio using ElevenLabs
    print("\n🔊 Converting memo to audio...")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "UgBBYS2sOqTuMpoF3BR0")  # Default voice ID if not in .env
    
    # Generate a unique audio filename with timestamp
    audio_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file = os.path.join(output_dir, f"series_a_audio_{audio_timestamp}.mp3")
    
    # Initialize TTS engine and generate audio
    tts = ElevenLabsTTS(script_file=memo_file, voice_id=voice_id)
    output_file = tts.generate_audio(audio_file)
    print(f"✅ Audio generated and saved to: {output_file}")
    
    # Step 5: Send email with memo text and audio attachment
    print("\n📧 Sending email with memo and audio...")
    
    # Read the memo content
    with open(memo_file, 'r') as f:
        memo_content = f.read()
    
    # Format the content for HTML email
    formatted_content = memo_content.replace('\n\n', '<br><br>')
    formatted_content = formatted_content.replace('\n', '<br>')
    
    # Create HTML content for email
    html_content = '<html><body><h1>Series A Funding Newsletter</h1>'
    html_content += '<div style="font-family: Arial, sans-serif; line-height: 1.6;">'
    html_content += formatted_content
    html_content += '</div>'
    html_content += '<p>Listen to the audio summary attached to this email.</p>'
    html_content += '<p>Best regards,<br/>AI Newsletter Bot</p></body></html>'
    
    # Initialize email sender
    sender = GmailEmailSender()
    
    # Get recipient email from environment or use default
    recipient_email = os.getenv('RECIPIENT_EMAIL', 'ebaadforrandomstuff@gmail.com')
    print(f"Using recipient email: {recipient_email}")
    
    # Note: The sender email is already set from environment variables in the GmailEmailSender class

    
    # Send the email
    sender.send_email(
        to_emails=[recipient_email],
        subject=f'🎵 Series A Companies Funding Update - {timestamp}',
        html_content=html_content,
        attachment_path=output_file
    )
    print(f"✅ Email sent to: {recipient_email}")
    
    print("\n🎉 Series A Newsletter Generation Pipeline Complete!")
    print(f"Summary of outputs:")
    print(f"- JSON data: {json_file_path}")
    print(f"- Text memo: {memo_file}")
    print(f"- Audio file: {output_file}")

if __name__ == "__main__":
    main()
