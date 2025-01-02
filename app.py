import requests
from bs4 import BeautifulSoup
import datetime
import logging
import os

import gradio as gr

# Attempt to import ollama
try:
    import ollama
except ImportError:
    print("Error: The 'ollama' library is not installed or not found.")
    print("Please install or verify Ollama to proceed.")
    raise

# ------------------------------------------------------------------------------
# 1. Configure Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("tmsa_app.log"),  # Log to a file
        logging.StreamHandler()               # Log to console
    ]
)

# ------------------------------------------------------------------------------
# 2. Function to Extract Text from Homepage
# ------------------------------------------------------------------------------
def extract_text_from_url(url):
    """
    Retrieves the homepage HTML using `requests` and parse text via BeautifulSoup.
    Returns the extracted text or None if there's an error.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Gather text from relevant tags (paragraphs, headings)
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    extracted_text = "\n".join([elem.get_text(strip=True) for elem in text_elements])

    if not extracted_text.strip():
        logging.warning(f"No meaningful text extracted from {url}.")
    return extracted_text

# ------------------------------------------------------------------------------
# 3. Function to Generate a Post via Ollama
# ------------------------------------------------------------------------------
def generate_post(desiredModel, prompt):
    """
    Calls Ollama's Llama model with the given prompt.
    Returns the response text or an error message if something goes wrong.
    """
    try:
        response = ollama.chat(model=desiredModel, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        # Ollama's latest response format example:
        # response['message']['content'] holds the LLM reply
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error during AI generation: {e}")
        return f"Error: {str(e)}"

# ------------------------------------------------------------------------------
# 4. Main function to process a single company
# ------------------------------------------------------------------------------
def process_company(company_name, website_url, model_name="llama3.1:latest"):
    """
    1) Extract text from the website.
    2) Calls the LLM 4 times for 4 social networks (Facebook, LinkedIn, X, Instagram).
    3) Saves the results in a text file named with the company name and date.
    4) Returns a short success/failure message to display in Gradio.
    """
    logging.info(f"Processing {company_name} ({website_url})")

    # Extract text
    homepage_text = extract_text_from_url(website_url)
    if not homepage_text:
        msg = f"Skipping {company_name} due to text extraction error."
        logging.warning(msg)
        return msg

    # Brand guide + TMSA context
    tmsa_brand_guide = """\
TMSA Brand Guide (Summary):
- Mission: Empower marketing and sales professionals in transportation and logistics
- Tone: Professional, approachable, industry-specific, inspirational, collaborative
- Goal: Highlight TMSA member companies, build thought leadership, foster community
"""

    # Truncate homepage text to avoid overly long prompts (optional)
    shortened_homepage_context = homepage_text[:1500]

    # --------------------------------------------------------------------------
    # 4.1 Generate the Facebook post
    # --------------------------------------------------------------------------
    facebook_coordinator_context = """\
As the Facebook Coordinator for TMSA, you are adept at creating engaging Facebook posts that drive engagement.
You're focused on fostering a sense of community and maximizing engagement on Facebook.
Use short sentences. Each post should be between 50 to 150 words, with high perplexity and burstiness.
Write one-sentence paragraphs. Include a call to action that encourages community interaction.
Include 3 to 5 hashtags, and 1 to 5 emojis.
"""

    facebook_prompt = f"""\
{tmsa_brand_guide}
{facebook_coordinator_context}

Company: {company_name}
Homepage snippet: {shortened_homepage_context}

Task: Write an engaging Facebook post (50-150 words) featuring {company_name}, a member of TMSA.
Make sure it aligns with TMSA's branding guidelines and fosters a sense of community on Facebook.
"""

    logging.info(f"Generating Facebook post for {company_name}...")
    facebook_post = generate_post(model_name, facebook_prompt)

    # --------------------------------------------------------------------------
    # 4.2 Generate the LinkedIn post
    # --------------------------------------------------------------------------
    linkedin_coordinator_context = """\
As the LinkedIn Coordinator for TMSA, you specialize in crafting professional posts that resonate with a business audience.
Length: 100-150 words. Use short sentences. Write with high perplexity and burstiness.
One-sentence paragraphs. Include a call to action for engagement or traffic.
Include 3 to 5 hashtags, and 1 to 5 emojis.
Ensure professional tone and alignment with TMSA branding.
"""

    linkedin_prompt = f"""\
{tmsa_brand_guide}
{linkedin_coordinator_context}

Company: {company_name}
Homepage snippet: {shortened_homepage_context}

Task: Write a professional LinkedIn post (100-150 words) featuring {company_name}, a member of TMSA.
Adhere to TMSA's brand guidelines, using SEO keywords and a call to action.
"""

    logging.info(f"Generating LinkedIn post for {company_name}...")
    linkedin_post = generate_post(model_name, linkedin_prompt)

    # --------------------------------------------------------------------------
    # 4.3 Generate the X (Twitter) post
    # --------------------------------------------------------------------------
    x_coordinator_context = """\
As the X Coordinator for TMSA, you craft concise tweets that spark engagement.
35 words max, under 280 characters.
Include relevant hashtags and a call to action.
Tone: informal and conversational.
"""

    x_prompt = f"""\
{tmsa_brand_guide}
{x_coordinator_context}

Company: {company_name}
Homepage snippet: {shortened_homepage_context}

Task: Write a short, impactful tweet (max 35 words) featuring {company_name}, a TMSA member.
Include at least one relevant hashtag, a call to action, and ensure it fits X's character limits.
"""

    logging.info(f"Generating X (Twitter) post for {company_name}...")
    x_post = generate_post(model_name, x_prompt)

    # --------------------------------------------------------------------------
    # 4.4 Generate the Instagram post
    # --------------------------------------------------------------------------
    instagram_coordinator_context = """\
As the Instagram Coordinator for TMSA, you focus on visual storytelling to drive engagement.
Create a visually engaging caption that aligns with TMSA's brand identity.
Include a compelling CTA and maintain a brand-consistent style.
Consider typical Instagram dimensions and best practices.
"""

    instagram_prompt = f"""\
{tmsa_brand_guide}
{instagram_coordinator_context}

Company: {company_name}
Homepage snippet: {shortened_homepage_context}

Task: Write an Instagram caption that highlights {company_name}, a TMSA member.
Use a visually descriptive, upbeat tone, and end with a CTA for followers to engage.
"""

    logging.info(f"Generating Instagram post for {company_name}...")
    instagram_post = generate_post(model_name, instagram_prompt)

    # --------------------------------------------------------------------------
    # 4.5 Save all posts to a file
    # --------------------------------------------------------------------------
    date_stamp = datetime.datetime.now().strftime("%Y%m%d")
    # Clean up the company name for a safer filename
    safe_company_name = "".join(
        char for char in company_name if char.isalnum() or char in (" ", "-", "_")
    ).strip()
    filename = f"{safe_company_name}_{date_stamp}.txt"

    if not os.path.exists("output"):
        os.makedirs("output")

    file_path = os.path.join("output", filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Company: {company_name}\n")
            f.write(f"Website: {website_url}\n\n")
            f.write("=== FACEBOOK POST ===\n")
            f.write(facebook_post + "\n\n")
            f.write("=== LINKEDIN POST ===\n")
            f.write(linkedin_post + "\n\n")
            f.write("=== X (TWITTER) POST ===\n")
            f.write(x_post + "\n\n")
            f.write("=== INSTAGRAM POST ===\n")
            f.write(instagram_post + "\n\n")

        msg = f"Successfully processed {company_name}. Posts saved to {file_path}"
        logging.info(msg)
        return msg
    except Exception as e:
        err_msg = f"Failed to write file for {company_name}: {e}"
        logging.error(err_msg)
        return err_msg

# ------------------------------------------------------------------------------
# 5. Gradio Interface
# ------------------------------------------------------------------------------
def run_app(
    company1, website1,
    company2, website2,
    company3, website3,
    company4, website4,
    company5, website5,
    company6, website6,
    company7, website7,
    company8, website8,
    company9, website9,
    company10, website10,
    company11, website11,
    company12, website12
):
    """
    Collect up to 12 (company, website) pairs from Gradio inputs.
    Run the sequential workflow for each non-empty entry.
    """
    results = []
    model_name = "llama3.1:latest"  # Update if needed

    # Build list of pairs
    pairs = [
        (company1, website1),
        (company2, website2),
        (company3, website3),
        (company4, website4),
        (company5, website5),
        (company6, website6),
        (company7, website7),
        (company8, website8),
        (company9, website9),
        (company10, website10),
        (company11, website11),
        (company12, website12),
    ]

    # Process each pair if it's non-empty
    for (c_name, c_website) in pairs:
        c_name = c_name.strip()
        c_website = c_website.strip()
        if c_name and c_website:
            result_msg = process_company(c_name, c_website, model_name=model_name)
            results.append(result_msg)

    # Return a combined message
    if results:
        return "\n".join(results)
    else:
        return "No valid company/website entries provided."

# ------------------------------------------------------------------------------
# 6. Build and Launch Gradio App
# ------------------------------------------------------------------------------
with gr.Blocks() as demo:
    gr.Markdown("# TMSA Spotlight")
    gr.Markdown(
        "Enter up to 12 pairs of (Company Name, Website URL). "
        "For each pair, the app will extract homepage text, generate 4 social media posts (Facebook, LinkedIn, X, Instagram), "
        "and save them to a text file in the 'output' folder."
    )

    # We create 12 rows for the user to input data
    with gr.Row():
        company1 = gr.Textbox(label="Company Name 1")
        website1 = gr.Textbox(label="Website URL 1")
    with gr.Row():
        company2 = gr.Textbox(label="Company Name 2")
        website2 = gr.Textbox(label="Website URL 2")
    with gr.Row():
        company3 = gr.Textbox(label="Company Name 3")
        website3 = gr.Textbox(label="Website URL 3")
    with gr.Row():
        company4 = gr.Textbox(label="Company Name 4")
        website4 = gr.Textbox(label="Website URL 4")
    with gr.Row():
        company5 = gr.Textbox(label="Company Name 5")
        website5 = gr.Textbox(label="Website URL 5")
    with gr.Row():
        company6 = gr.Textbox(label="Company Name 6")
        website6 = gr.Textbox(label="Website URL 6")
    with gr.Row():
        company7 = gr.Textbox(label="Company Name 7")
        website7 = gr.Textbox(label="Website URL 7")
    with gr.Row():
        company8 = gr.Textbox(label="Company Name 8")
        website8 = gr.Textbox(label="Website URL 8")
    with gr.Row():
        company9 = gr.Textbox(label="Company Name 9")
        website9 = gr.Textbox(label="Website URL 9")
    with gr.Row():
        company10 = gr.Textbox(label="Company Name 10")
        website10 = gr.Textbox(label="Website URL 10")
    with gr.Row():
        company11 = gr.Textbox(label="Company Name 11")
        website11 = gr.Textbox(label="Website URL 11")
    with gr.Row():
        company12 = gr.Textbox(label="Company Name 12")
        website12 = gr.Textbox(label="Website URL 12")

    run_button = gr.Button("Generate Posts")
    output_area = gr.Textbox(
        label="Output/Logs",
        placeholder="Processing results will appear here...",
        lines=15
    )

    run_button.click(
        fn=run_app,
        inputs=[
            company1, website1,
            company2, website2,
            company3, website3,
            company4, website4,
            company5, website5,
            company6, website6,
            company7, website7,
            company8, website8,
            company9, website9,
            company10, website10,
            company11, website11,
            company12, website12,
        ],
        outputs=[output_area]
    )

# Launch Gradio interface
if __name__ == "__main__":
    demo.launch()
