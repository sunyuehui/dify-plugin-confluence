from typing import Any

from atlassian.confluence import Confluence

def auth(credential: dict[str, Any]) -> Confluence:
    """
    Authenticate to Confluence using different methods based on environment.
    
    Args:
        credential: A dictionary containing authentication details.
            Required keys:
                - url: Confluence instance URL
                - environment: 'cloud' or 'datacenter'
            Conditional keys based on environment:
                - cloud: api_token
                - datacenter: username, password or api_token (for PAT)
    """
    environment = credential.get("environment").lower()
    base_url = credential.get("url")
    
    if environment == "cloud":
        # Cloud 环境使用 API Token
        return Confluence(
            url=base_url,
            token=credential.get("api_token")
        )
    elif environment == "datacenter":
        # Data Center/Server 环境
        auth_method = credential.get("auth_method", "basic")
        
        if auth_method == "basic":
            # 使用用户名/密码认证
            return Confluence(
                url=base_url,
                username=credential.get("username"),
                password=credential.get("password")
            )
        elif auth_method == "pat":
            # 使用个人访问令牌 (PAT) 认证
            return Confluence(
                url=base_url,
                token=credential.get("api_token")
            )
        else:
            raise ValueError("Unsupported authentication method for Data Center")
    else:
        raise ValueError("Unsupported environment. Use 'cloud' or 'datacenter'")
