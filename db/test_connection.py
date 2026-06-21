from client import SupabaseClient
client = SupabaseClient.get_instance()
response = client.table("events").select("name").execute()
print(response)