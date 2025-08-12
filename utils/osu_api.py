import aiohttp

class OsuAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
    async def get_access_token(self):
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials',
                    'scope': 'public'
                }
                async with session.post('https://osu.ppy.sh/oauth/token', data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result.get('access_token')
                        return self.access_token
                    else:
                        print(f"[!] error 4")
                        return None
        except Exception as e:
            print(f"[!] error 4")
            return None
    
    async def get_user(self, username_or_id, mode='osu'):
        try:
            if not self.access_token:
                await self.get_access_token()
                
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f'https://osu.ppy.sh/api/v2/users/{username_or_id}/{mode}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        return None
                    else:
                        print(f"[!] error 4")
                        return None
        except Exception as e:
            print(f"[!] error 44")
            return None
    
    async def get_user_recent(self, user_id, limit=1):
        try:
            if not self.access_token:
                await self.get_access_token()
                
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f'https://osu.ppy.sh/api/v2/users/{user_id}/scores/recent?limit={limit}&include_fails=1'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    elif response.status == 404:
                        return []
                    else:
                        print(f"[!] error 4: {response.status}")
                        return []
        except Exception as e:
            print(f"[!] error during loading last play: {e}")
            return []