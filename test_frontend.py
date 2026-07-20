import requests
import uuid

# Create a clean unique email for this production scale run
test_email = f"prod_tester_{uuid.uuid4().hex[:4]}@example.com"
test_password = "ProductionSecure123!"

# 1. Upload the massive 29MB TCS PDF
print("Uploading massive 29MB TCS Annual Report...")
print("NOTE: LlamaParse is visually extracting 347 pages of tables. This will take 1-2 minutes...")

upload_success = False
try:
    with open("annual-report-2025-2026.pdf", "rb") as f:
        upload_res = requests.post(
            "http://localhost:8000/upload",
            files={"file": f}
        )
    
    print("Upload Status Code:", upload_res.status_code)
    try:
        print("Upload Response:", upload_res.json())
        upload_success = True
    except Exception:
        print("Upload Raw Response Error Text:\n", upload_res.text)
except FileNotFoundError:
    print("Error: 'annual-report-2025-2026.pdf' not found in this folder. Make sure the 29MB file is named exactly this.")
except Exception as e:
    print(f"Failed to send the upload request: {e}")

if upload_success:
    try:
        # 2. Automatically register the production test user
        print(f"\nRegistering user ({test_email})...")
        reg_res = requests.post(
            "http://localhost:8000/register",
            json={"email": test_email, "password": test_password}
        )
        print("Registration Status Code:", reg_res.status_code)

        # 3. Log in to get the authentication token
        print("\nLogging in...")
        login_res = requests.post(
            "http://localhost:8000/login",
            json={"email": test_email, "password": test_password}
        )
        
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")

            # 4. Ask a killer financial question targeting page 65 of the report layout
            print("\nAsking high-fidelity layout question...")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Testing if the RAG can differentiate between Standalone and Consolidated metrics in a dense matrix table
            complex_query = (
                "According to the Financial Results table in the Board's Report, "
                "what is the exact value in crore for the Consolidated Revenue from operations "
                "in FY 2025-26, and how does it compare to the Standalone Revenue from operations for the same year?"
            )
            
            chat_res = requests.post(
                "http://localhost:8000/chat",
                json={"message": complex_query},
                headers=headers
            )
            
            print("Chat Status Code:", chat_res.status_code)
            try:
                print("\nAI Answer:\n", chat_res.json().get("response"))
                print("\nSources Used:", chat_res.json().get("sources"))
            except Exception:
                print("Chat Raw Response Error Text:\n", chat_res.text)
        else:
            print("\nLogin failed. Status Code:", login_res.status_code)
    except Exception as e:
        print(f"Script runtime error: {e}")