import os
import requests

class SupabaseStorage:
    def __init__(self):
        self.base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        if not self.base_url:
            raise RuntimeError("SUPABASE_URL is missing")
        if not self.key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing")

    def upsert(self, payload: dict) -> None:
        url = f"{self.base_url}/rest/v1/contests?on_conflict=fingerprint"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if not response.ok:
            raise RuntimeError(
                f"Supabase upsert failed {response.status_code}: {response.text[:500]}"
            )
