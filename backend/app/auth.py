from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def require_role(role: str):
    async def checker(creds: HTTPAuthorizationCredentials = Depends(security)):
        token = creds.credentials
        if not token:
            raise HTTPException(status_code=401, detail="No token")
        # TODO: validate JWT with JWKS/Keycloak
        return {"sub": "stub", "roles": ["analyst", "adminparam"]}
    return checker
