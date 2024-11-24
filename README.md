# Vision LLM Automator

## Instructions for setting up environment

1. Clone the repo
2. Setup your Python (Conda/virtual/others) environment and install packages using the following command:

   ```bash
   pip install -r /path/to/requirements.txt
   ```

3. This repo uses Groq-based models as preferred backend. Generate and note your API key.
4. This repo uses dotenv to manage secrets. Store your Groq API key in a `.env` file under the key `GROQ_API_KEY` environment variable as follows:

   ```
   GROQ_API_KEY=<your_key>
   ```

## Instructions for setting up MacOS Automate task using keyboard shortcut trigger

1. In Automator app, create an "Application" with the action "Run Shell Script"
2. Set the shell script to use `/bin/bash` and add command as follows:

   ```bash
   /path/to/your/environment/bin/python /path/to/SelfAutomate/ss_text_detect.py
   ```

3. In Automator app, create a "Quick Action" and set "Workflow receives `no input` in `any application`"
4. Add an action "Launch Application" and Select the above created application.
5. In System Settings, configure "Keyboard Shortcuts". Look for "Services" > "General" > `Your Quick Action Name` and set your preferred key combination.

## Instructions for setting up Windows PowerToys task using keyboard shortcut trigger

Reference: https://learn.microsoft.com/en-us/windows/powertoys/keyboard-manager#remap-a-shortcut-to-start-an-app

1. In PowerToys, under the Keyboard Manager utility, map a shortcut to "Start App".
2. Under the "App" field, paste the path to your Python binary (`/path/to/your/environment/bin/python`).
3. Under the "Args" field, paste the path to the repo script (`/path/to/SelfAutomate/ss_text_detect.py`).
