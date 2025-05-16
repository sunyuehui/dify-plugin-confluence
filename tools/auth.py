from typing import Any

from atlassian.confluence import Confluence


def auth(credential: dict[str, Any]) -> Confluence:
    """
    Authenticate to Confluence using either token or username/password.
    """
    auth_method = credential.get("auth_method", "token")
    
    if auth_method == "token":
        confluence = Confluence(
            url=credential.get("url"),
            token=credential.get("api_token")
        )
    else:  # username_password
        confluence = Confluence(
            url=credential.get("url"),
            username=credential.get("username"),
            password=credential.get("api_token")
        )
    
    return confluence
