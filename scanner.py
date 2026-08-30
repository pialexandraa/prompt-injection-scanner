import os
import zipfile
import sys
from llm_guard.input_scanners import PromptInjection # Used with Python 3.11 on local installation or in a virtual environment

def scan_zip(zip_path: str, threshold: float = 0.5):
    if not os.path.isfile(zip_path):
        print(f"Error: {zip_path} fiel not found.")
        sys.exit(1)

    # Initiate model scanner
    scanner = PromptInjection(threshold=threshold)
    findings = []

    # Added an extensive tuple of file options that the scanner should be able to detect
    target_extensions = (
        ".txt", ".md", ".py", ".js", ".ts", ".json", 
        ".yaml", ".yml", ".html", ".csv", ".rst", ".go",
        ".rs", ".cpp", ".hpp", ".xml", ".toml", ".ini", 
        ".cfg", ".env", ".sh", ".bash", ".ps1", ".bat", 
        ".java", ".cs", ".php", ".rb", ".swift", ".kt", 
        ".log", ".tex"
    )

    print(f"[*] Scanning archive: {zip_path}")

    with zipfile.ZipFile(zip_path, 'r') as archive:
        for member in archive.infolist():
            # Prevent zip slip / directory traversal vulnerabilities
            if ".." in member.filename or member.filename.startswith("/"):
                continue

            if member.filename.endswith(target_extensions):
                try:
                    with archive.open(member) as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        
                        if not content.strip():
                            continue

                        _, is_valid, risk_score = scanner.scan(content)

                        if not is_valid:
                            findings.append({
                                "file": member.filename,
                                "risk_score": round(risk_score, 4)
                            })
                except Exception as e:
                    print(f"[-] Could not read the following element(s){member.filename}: {e}")

    # Output results
    print("\n" + "=" * 40)
    print("SCAN REPORT")
    print("=" * 40)
    if findings:
        print(f"[!] DANGER: Detected {len(findings)} suspicious file(s):")
        for finding in findings:
            print(f"  - {finding['file']} (Risk Score: {finding['risk_score']})")
    else:
        print("[+] SUCCESS: No prompt injections detected above threshold.")

if __name__ == "__main__":
    archive_path = sys.argv[1] if len(sys.argv) > 1 else "/data/input.zip"
    scan_zip(archive_path)