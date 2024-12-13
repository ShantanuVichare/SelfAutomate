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

5. (Optional) If you want to use Pushbullet features, set `PUSHBULLET_CONFIG_PATH` environment variable with a path to a json file (file may not exist initially, but its parent directory should).
6. (Optional) If you want to log temporary and runtime files to particular path, set `LOG_DIR` environment variable. (Default path will be set to `$HOME/.self_dev`)

## Running context

1. The script can be executed via the following bash command:

   ```bash
   /path/to/your/environment/bin/python /path/to/SelfAutomate/run.py
   ```

2. Alternatively, you can run it in background with its output redirected. For example:

   ```bash
   /path/to/your/environment/bin/python /path/to/SelfAutomate/run.py >> $LOG_DIR/sa.shell.log 2>&1 &
   ```
