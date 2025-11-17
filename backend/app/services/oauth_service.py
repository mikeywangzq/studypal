"""
OAuth Service - OAuth 第三方登录服务
"""
from typing import Optional, Dict
import httpx
from ..config import settings


class OAuthService:
    """OAuth 服务"""

    # OAuth 提供商配置
    OAUTH_PROVIDERS = {
        "google": {
            "token_url": "https://oauth2.googleapis.com/token",
            "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            "client_id_env": "GOOGLE_CLIENT_ID",
            "client_secret_env": "GOOGLE_CLIENT_SECRET",
        },
        "github": {
            "token_url": "https://github.com/login/oauth/access_token",
            "user_info_url": "https://api.github.com/user",
            "client_id_env": "GITHUB_CLIENT_ID",
            "client_secret_env": "GITHUB_CLIENT_SECRET",
        },
    }

    @staticmethod
    async def exchange_code_for_token(
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Optional[str]:
        """
        用授权码换取访问令牌

        Args:
            provider: OAuth 提供商（google, github）
            code: 授权码
            redirect_uri: 重定向 URI

        Returns:
            访问令牌或 None
        """
        if provider not in OAuthService.OAUTH_PROVIDERS:
            return None

        config = OAuthService.OAUTH_PROVIDERS[provider]

        # 从环境变量获取客户端凭证
        client_id = getattr(settings, config["client_id_env"], None)
        client_secret = getattr(settings, config["client_secret_env"], None)

        if not client_id or not client_secret:
            return None

        # 准备请求数据
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }

        if provider == "google":
            data["grant_type"] = "authorization_code"

        # 发送请求
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Accept": "application/json"}
                response = await client.post(
                    config["token_url"],
                    data=data,
                    headers=headers
                )

                if response.status_code != 200:
                    return None

                result = response.json()
                return result.get("access_token")

        except Exception:
            return None

    @staticmethod
    async def get_user_info(
        provider: str,
        access_token: str
    ) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            provider: OAuth 提供商
            access_token: 访问令牌

        Returns:
            用户信息字典或 None
            {
                "email": str,
                "oauth_id": str,
                "username": str (optional),
                "full_name": str (optional),
                "avatar_url": str (optional),
            }
        """
        if provider not in OAuthService.OAUTH_PROVIDERS:
            return None

        config = OAuthService.OAUTH_PROVIDERS[provider]

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(
                    config["user_info_url"],
                    headers=headers
                )

                if response.status_code != 200:
                    return None

                user_data = response.json()

                # 根据不同的提供商解析用户信息
                if provider == "google":
                    return {
                        "email": user_data.get("email"),
                        "oauth_id": user_data.get("id"),
                        "username": user_data.get("email", "").split("@")[0],
                        "full_name": user_data.get("name"),
                        "avatar_url": user_data.get("picture"),
                    }
                elif provider == "github":
                    # GitHub 可能不返回邮箱，需要额外请求
                    email = user_data.get("email")
                    if not email:
                        # 获取用户邮箱列表
                        email_response = await client.get(
                            "https://api.github.com/user/emails",
                            headers=headers
                        )
                        if email_response.status_code == 200:
                            emails = email_response.json()
                            # 获取主邮箱或第一个验证的邮箱
                            for email_obj in emails:
                                if email_obj.get("primary") and email_obj.get("verified"):
                                    email = email_obj.get("email")
                                    break
                            if not email:
                                for email_obj in emails:
                                    if email_obj.get("verified"):
                                        email = email_obj.get("email")
                                        break

                    return {
                        "email": email,
                        "oauth_id": str(user_data.get("id")),
                        "username": user_data.get("login"),
                        "full_name": user_data.get("name"),
                        "avatar_url": user_data.get("avatar_url"),
                    }

                return None

        except Exception:
            return None

    @staticmethod
    def get_authorization_url(provider: str, redirect_uri: str, state: str = "") -> Optional[str]:
        """
        获取 OAuth 授权 URL

        Args:
            provider: OAuth 提供商
            redirect_uri: 重定向 URI
            state: 状态参数（可选）

        Returns:
            授权 URL 或 None
        """
        if provider not in OAuthService.OAUTH_PROVIDERS:
            return None

        config = OAuthService.OAUTH_PROVIDERS[provider]
        client_id = getattr(settings, config["client_id_env"], None)

        if not client_id:
            return None

        if provider == "google":
            base_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "access_type": "offline",
            }
        elif provider == "github":
            base_url = "https://github.com/login/oauth/authorize"
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": "user:email",
            }
        else:
            return None

        if state:
            params["state"] = state

        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"


# 全局实例
oauth_service = OAuthService()
