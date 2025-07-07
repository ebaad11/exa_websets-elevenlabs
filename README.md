# Series A Funding Newsletter Generator

This project automates the process of creating and delivering Series A funding newsletters by:
1. Tracking recent Series A companies using Exa Websets API
2. Generating a concise memo summarizing these companies using Exa AI
3. Converting the memo to audio using ElevenLabs API
4. Sending an email with the text and audio attachment using Gmail API

## Prerequisites

- Python 3.8+
- Access to Exa API (requires a Pro plan)
- ElevenLabs API access
- Gmail API credentials

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/buildclub-team/exawebsets_elevenlabs.git
cd exawebsets_elevenlabs
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```
# Exa API Configuration
EXA_API_KEY=your_exa_api_key_here

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_preferred_voice_id

# Gmail Configuration
SENDER_EMAIL=your_gmail_address@gmail.com
RECIPIENT_EMAIL=recipient_email@example.com
```

### 4. Gmail API Authentication

1. Set up a Google Cloud Project and enable the Gmail API
2. Create OAuth 2.0 credentials (Desktop application type)
3. Download the credentials JSON file and save it as `credentials.json` in the project root directory
4. On first run, the application will prompt you to authorize access to your Gmail account

## Usage

Run the main script to generate and send a newsletter:

```bash
python main.py
```

The script will:
1. Fetch data about recent Series A companies
2. Generate a text summary
3. Convert the summary to audio
4. Send an email with the text and audio attachment

## Project Structure

- `main.py`: Main script that orchestrates the entire workflow
- `simple_websets.py`: Handles interaction with Exa Websets API
- `memo_generator.py`: Generates the text summary using Exa AI
- `eleven_labs_tts.py`: Converts text to speech using ElevenLabs API
- `gmail_sender.py`: Sends emails with attachments via Gmail API

## Output

The script creates an `output` directory containing:
- JSON data from Exa Websets API
- Text summary of Series A companies
- Audio file of the summary

## Note

This project requires valid API keys and credentials for all services. The Exa Websets API specifically requires a Pro plan subscription.

## License

MIT
