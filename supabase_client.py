from supabase import create_client

SUPABASE_URL = "https://lxsfnlyszcouywqcgmuz.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_kqQ9aUC259akUtGAV7dCZQ_EFPmir0U"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)