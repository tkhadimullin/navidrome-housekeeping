import requests
import aiohttp

class NavidromeClient:
    """Simple client for interacting with Navidrome Subsonic API"""
    
    def __init__(self, NAVIDROME_URL, NAVIDROME_USERNAME, NAVIDROME_PASSWORD):
        self.base_url = NAVIDROME_URL
        self.username = NAVIDROME_USERNAME
        self.password = NAVIDROME_PASSWORD
        self._auth_token = None
        self._subsonic_token = None
        self._subsonic_salt = None
        
    async def _ensure_authenticated(self):
        """Ensure we have valid authentication credentials"""
        if self.username and self.password and not self._subsonic_token:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/auth/login",
                        json={"username": self.username, "password": self.password},
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()

                        # Store both JWT token and Subsonic credentials
                        self._auth_token = data.get("token")
                        self._subsonic_token = data.get("subsonicToken")
                        self._subsonic_salt = data.get("subsonicSalt")

                        if not self._subsonic_token or not self._subsonic_salt:
                            raise Exception("No Subsonic credentials received from login response")

            except Exception as e:
                raise Exception(f"Unexpected error during login: {e}")

        elif not self.username or not self.password:
            raise Exception(
                "No authentication method available (need NAVIDROME_API_KEY or NAVIDROME_USERNAME/PASSWORD)"
            )
            
    def _get_subsonic_params(self):
        """Get Subsonic API parameters"""
        return {
            "u": self.username,
            "t": self._subsonic_token,
            "s": self._subsonic_salt,
            "v": "1.16.1",
            "c": "PlaylistHousekeeper",
            "f": "json",
            "x-nd-authorization": f"Bearer {self._auth_token}"
        }
    
    async def api_call(self, endpoint, **kwargs):
        """Make Navidrome API call"""
        try:
            await self._ensure_authenticated()

            url = f"{self.base_url}/{endpoint}"
            params = {**self._get_subsonic_params(), **kwargs}
            headers = {**self._get_subsonic_params()}
        

            async with aiohttp.ClientSession() as session:                
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            raise Exception(f"Error talking to Navidrome API: {e}")