from app.config.settings import get_settings
from supabase import Client, create_client

settings = get_settings()


class SupabaseClient:
    @property
    def client(self) -> Client:
        return create_client(settings.supabase_url, settings.supabase_key)

    def ping(self):
        return self.client.table('profiles').select('*').limit(1).execute()

    def get_user(self, access_token: str):
        return self.client.auth.get_user(access_token).user
