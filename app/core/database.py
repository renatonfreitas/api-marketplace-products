from app.core.config import get_settings
from supabase import Client, create_client


settings = get_settings()
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)