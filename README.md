# TMSA Spotlight

This application generates social media posts (Facebook, LinkedIn, X/Twitter, and Instagram) to feature Transportation Marketing and Sales Association (TMSA) member companies. It uses:

- **Requests + BeautifulSoup** for extracting homepage text,
- **Ollama** for local LLM inference (Llama 3.1), and
- **Gradio** for a user-friendly interface allowing up to 12 company/website entries at once.

When you run this app, each company gets a text file with four social media posts (one for each platform) in the `output` folder, according to TMSA’s branding and style guidelines.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [How It Works](#how-it-works)
5. [Troubleshooting](#troubleshooting)
6. [License](#license)

---

## Prerequisites

1. **Python 3.11+**.
2. **Ollama** installed and configured on your Windows system, including the Llama 3.1 model (`llama3.1:latest` or your preferred variant).
   - You can verify installation in the Windows terminal:
     ```bash
     where ollama
     ```
   - If `ollama` is not on your PATH, add it or refer to Ollama’s documentation.
3. **Basic Python environment** with the following libraries installed:
   - `requests`
   - `beautifulsoup4`
   - `gradio`

---

## Installation

1. **Clone or download** this repository.

2. In your command prompt (Windows) or terminal, navigate to the project directory and install the Python dependencies:
   ```bash
   pip install requests beautifulsoup4 gradio ollama
   ```

3. Check if Ollama is properly installed and accessible:
   ```bash
   where ollama
   ```
   If not found, follow [Ollama’s documentation](https://github.com/jmorganca/ollama) to install and set up on Windows.

4. (Optional) Create and activate a virtual environment to keep dependencies isolated:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the Application**
   From your terminal, run:
   ```bash
   python app.py
   ```
   This launches a local Gradio interface (usually at `http://127.0.0.1:7860`).

2. **Enter Company/Website Pairs**
   - In the Gradio app, enter up to 12 company names and their respective website URLs.
   - Click **Generate Posts**.

3. **Review Output**
   - For each valid `(Company Name, Website URL)` pair, the app will:
     1. Extract homepage text (using `requests` + `BeautifulSoup`).
     2. Generate four social media posts (Facebook, LinkedIn, X, Instagram) by calling **Ollama** sequentially.
     3. Save all four posts in a single text file named `{CompanyName_YYYYMMDD}.txt` inside the `output` directory.
   - Progress and log messages appear in the Gradio textbox and in the `app.log` file.

---

## How It Works

1. **Text Extraction:**
   - The code uses `requests.get()` to fetch the homepage HTML and `BeautifulSoup` to parse it, extracting text from `<p>` and `<h1>`–`<h6>` tags.
   - If any error occurs (e.g., invalid URL, timeout), the process **logs** the error and skips that company.

2. **Generating Social Media Posts:**
   - The script calls `ollama.chat()` four times **in sequence** (Facebook, LinkedIn, X/Twitter, Instagram).
   - Each post uses unique prompts tailored for that social platform, combined with TMSA brand guidelines and a snippet of extracted homepage text.
   - The app waits for each LLM response before moving on to the next.

3. **Saving Output:**
   - The final text file for each company includes all four posts, labeled with the social network.
   - By default, the files are placed in an `output` directory, which is created automatically if it doesn’t exist.

---

## Troubleshooting

- **Ollama not found:**
  - Run `where ollama` on Windows. If it doesn’t show a path, ensure you’ve installed Ollama and added it to your PATH.
  - Confirm you have the correct Llama model: `llama3.1:latest`. If different, update the `model_name` variable in the code.

- **Python library not installed:**
  - Run `pip show requests` (or `pip list | findstr requests` on Windows).
  - If missing, run `pip install requests`. Repeat for `beautifulsoup4`, `gradio`, etc.

- **Time out / Connection errors:**
  - Some websites or restrictive network environments can lead to timeouts. Increase `timeout` in `requests.get(url, timeout=10)` or try again later.

- **Large Webpages / Long Summaries:**
  - The code currently truncates homepage text to the first 1500 characters. Adjust this in `shortened_homepage_context = homepage_text[:1500]` if needed.

- **Output not appearing:**
  - Check your `output` folder.
  - Check `app.log` for any error messages.

---

## License

This project is provided via the MIT license. It is intended as a demonstration for creating a local AI agent application with **Ollama**, **requests**, **BeautifulSoup**, and **Gradio**.

Feel free to adapt or expand this code for your own internal or commercial use, abiding by any relevant licensing.
