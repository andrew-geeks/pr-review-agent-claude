### Script to review code in a GitHub PR using Claude and post inline comments based on the review. Running in GitHub Actions pipeline.


import os
import json
import requests
from dotenv import load_dotenv
import anthropic

# 1. Configuration & Setup
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")  # format: "owner/repo" (auto-set in GitHub Actions)
MODEL_ID = "claude-sonnet-4-6"
ALLOWED_EXTENSIONS = {'.py', '.sql', '.java'} # add extensions of those files you want to review
EXCLUDED_FILES = {'agent.py'} # add specific files to exclude from review.
GITHUB_API_BASE = "https://api.github.com"
GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_pr_head_sha(repo, pr_number):
    """Fetches the head commit SHA for the Pull Request (required for inline comments)."""
    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=GITHUB_HEADERS)
    if response.status_code == 200:
        return response.json()["head"]["sha"]
    print(f"❌ Error fetching PR info: {response.status_code}")
    print(response.text)
    return None


def get_entire_pr_diff(repo, pr_number):
    """Fetches the complete unified diff for the entire Pull Request."""
    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}"
    headers = {**GITHUB_HEADERS, "Accept": "application/vnd.github.v3.diff"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text

    print(f"❌ Error fetching diff: {response.status_code}")
    print(response.text)
    return ""


def parse_diff_by_file(full_diff):
    """
    Splits the unified diff into chunks by file and extracts the filename.
    Returns a dictionary mapping filename -> diff_content.
    """
    files_diffs = {}
    # Split by the git diff header
    chunks = full_diff.split('diff --git')
    
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        # Find the '+++ b/' line which indicates the new file path
        lines = chunk.split('\n')
        filename = None
        for line in lines:
            if line.startswith('+++ b/'):
                filename = line[6:].strip() # Extract path after '+++ b/'
                break
        
        if filename:
            # Check if it's a file type we want to review and not excluded
            if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS) and filename not in EXCLUDED_FILES:
                files_diffs[filename] = chunk
                
    return files_diffs


def load_domain_knowledge_skill():
    """Skill: Loads project-specific rules from a local Markdown file."""
    for rule_file in ("DOMAIN_RULES.md", "skills.md"):
        if os.path.exists(rule_file):
            with open(rule_file, "r") as f:
                return f.read()
    return "No specific domain rules found for this project."


def review_code_with_claude(code_content, domain_knowledge):
    """Sends code to Claude and parses the JSON review recommendations."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=4096,
        system=(
            "You are a Senior Developer. Use the following project-specific "
            f"domain rules to guide your review:\n\n{domain_knowledge}\n\n"
            "Review the code for these rules and general best practices. "
            "Output ONLY a valid JSON list of objects: [{\"line\": int, \"message\": \"string\"}]"
        ),
        messages=[
            {
                "role": "user",
                "content": f"Review this code change:\n{code_content}"
            }
        ],
        temperature=0,
    )

    raw_output = message.content[0].text
    try:
        clean_json = raw_output.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except:
        return []



def post_inline_comment(repo, pr_number, commit_sha, file_path, line_number, message):
    """Posts an inline review comment to a GitHub PR."""
    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}/comments"

    payload = {
        "body": message,
        "commit_id": commit_sha,
        "path": file_path,
        "line": line_number,
        "side": "RIGHT",
    }

    response = requests.post(url, json=payload, headers=GITHUB_HEADERS)

    if response.status_code in [200, 201]:
        print(f"✅ Successfully posted to {file_path}:{line_number}")
    else:
        print(f"❌ Failed to post to {file_path}:{line_number}. Status: {response.status_code}")
        print(response.text)



if __name__ == "__main__":

    required_vars = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GITHUB_REPOSITORY": GITHUB_REPOSITORY,
        "PR_NUMBER": os.getenv("PR_NUMBER"),
    }
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Set ANTHROPIC_API_KEY as a GitHub Actions secret. GITHUB_TOKEN and GITHUB_REPOSITORY are auto-set by Actions.")
        exit(1)

    pr_number = required_vars["PR_NUMBER"]
    repo = GITHUB_REPOSITORY
    domain_knowledge = load_domain_knowledge_skill()

    print(f"📦 Analyzing PR #{pr_number} in {repo}")

    # Fetch the head commit SHA (required for GitHub inline comments)
    commit_sha = get_pr_head_sha(repo, pr_number)
    if not commit_sha:
        print("❌ Could not retrieve PR head commit SHA. Exiting.")
        exit(1)

    # Fetch the full diff
    full_diff = get_entire_pr_diff(repo, pr_number)

    if full_diff:
        file_map = parse_diff_by_file(full_diff)

        for file_path, diff_content in file_map.items():
            print(f"🤖 Reviewing: {file_path}")
            recommendations = review_code_with_claude(diff_content, domain_knowledge)

            for rec in recommendations:
                line = rec.get('line')
                message = rec.get('message')

                post_inline_comment(repo, pr_number, commit_sha, file_path, line, message)