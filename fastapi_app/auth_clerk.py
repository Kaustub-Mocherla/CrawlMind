import jwt
import requests
import os
import pathlib
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from functools import lru_cache
import logging
import json
from dotenv import load_dotenv

root_env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=root_env_path)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "https://quiet-cardinal-60.clerk.accounts.dev/.well-known/jwks.json")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")

print(f"🔧 Clerk Configuration:")
print(f"   JWKS URL: {CLERK_JWKS_URL}")
print(f"   Audience: {CLERK_AUDIENCE or 'None (audience verification disabled)'}")

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_jwks():
    try:
        logger.info(f"Fetching JWKS from: {CLERK_JWKS_URL}")
        response = requests.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        jwks_data = response.json()
        logger.info(f"Successfully fetched JWKS with {len(jwks_data.get('keys', []))} keys")
        return jwks_data
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )

def get_signing_key(token: str):
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        logger.debug(f"Token header: {header}")
        logger.debug(f"Key ID (kid): {kid}")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid)"
            )
        
        jwks = get_jwks()
        
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                logger.debug(f"Found matching key for kid: {kid}")
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        available_kids = [k.get('kid') for k in jwks.get('keys', [])]
        logger.error(f"Key ID {kid} not found. Available keys: {available_kids}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unable to find key for kid: {kid}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signing key: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error processing token: {str(e)}"
        )

# This debug_token_claims function is now replaced by the more detailed one below
    logger.debug(f"User identifier '{field}': {payload[field]}")
    
    # Check for email fields
    email_fields = ["email", "email_address", "primary_email_address"]
    email_found = False
    for field in email_fields:
        if field in payload:
            logger.debug(f"Found email in '{field}': {payload[field]}")
            email_found = True
    
    if not email_found:
        logger.warning("No email field found in token")
    
    logger.debug("=== END TOKEN DEBUG ===")

def verify_clerk_token(token: str) -> Dict:
    try:
        logger.debug(f"Verifying token of length: {len(token)}")
        
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        logger.debug(f"Unverified payload: {json.dumps(unverified_payload, indent=2)}")
        
        signing_key = get_signing_key(token)
        
        verify_options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": False
        }
        
        logger.debug(f"Verification options: {verify_options}")
        
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            options=verify_options
        )
        
        logger.info(f"Token verified successfully for user: {payload.get('sub')}")
        
        # Debug token claims using our new function
        debug_token_claims(token)
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        logger.error(f"Invalid audience. Expected: {CLERK_AUDIENCE}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    logger.debug(f"Authenticating user with token: {credentials.credentials[:20]}...")
    return verify_clerk_token(credentials.credentials)

def get_current_user_id(user: Dict = Depends(get_current_user)) -> str:
    # Try to get user_id from various possible fields
    user_id = user.get('user_id') or user.get('sub') or user.get('id')
    
    if not user_id:
        logger.error(f"No user ID found in token. Available fields: {list(user.keys())}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    # Log additional debug info
    if 'email' in user:
        logger.debug(f"Email in token: {user.get('email')}")
    elif user.get('sub') and user.get('sub').startswith('user_'):
        logger.debug(f"Using sub claim as user ID: {user.get('sub')}")
    
    logger.debug(f"Extracted user ID: {user_id}")
    return user_id

def debug_token_claims(token: str) -> None:
    """Debug function to print all claims in a JWT token"""
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        logger.debug("==== JWT TOKEN CLAIMS DEBUG ====")
        logger.debug(f"All claims: {json.dumps(unverified_payload, indent=2)}")
        
        # Check for email in various possible locations
        email_fields = ['email', 'mail', 'emailAddress', 'primary_email']
        for field in email_fields:
            if field in unverified_payload:
                logger.debug(f"Found email in '{field}': {unverified_payload[field]}")
        
        # Check if email might be nested in other claims
        if 'user' in unverified_payload and isinstance(unverified_payload['user'], dict):
            user_data = unverified_payload['user']
            logger.debug(f"User claim contains: {list(user_data.keys())}")
            for field in email_fields:
                if field in user_data:
                    logger.debug(f"Found email in 'user.{field}': {user_data[field]}")
        
        logger.debug("================================")
    except Exception as e:
        logger.error(f"Error debugging token claims: {e}")

def get_current_user_email(user: Dict = Depends(get_current_user)) -> Optional[str]:
    """Extract the user's email from the JWT token"""
    # Try to get email from various possible fields
    email = user.get('email')
    
    # Check nested fields if Clerk puts email in a nested structure
    if not email and 'user' in user and isinstance(user['user'], dict):
        email = user['user'].get('email')
    
    # Additional common locations for email in JWTs
    if not email:
        for field in ['email_address', 'primary_email_address', 'mail', 'emailAddress']:
            if field in user:
                email = user[field]
                break
    
    logger.debug(f"Extracted email: {email}")
    return email

def get_current_user_name(user: Dict = Depends(get_current_user)) -> str:
    """Extract the user's name from the JWT token"""
    # Try to get name from various possible fields
    name = user.get('name')
    
    # If name is not directly available, try to construct it from first and last name
    if not name:
        first_name = user.get('firstName') or user.get('first_name')
        last_name = user.get('lastName') or user.get('last_name')
        
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
    
    # Fall back to user ID if no name is available
    if not name:
        name = user.get('user_id') or user.get('sub') or user.get('id') or "User"
    
    logger.debug(f"Extracted user name: {name}")
    return name
