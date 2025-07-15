import requests
import json
import base64
from urllib.parse import urlencode, parse_qs
import webbrowser
from datetime import datetime
import os

class LinkedInPoster:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.user_id = None
        
        # LinkedIn API endpoints
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.profile_url = "https://api.linkedin.com/v2/userinfo"
        self.post_url = "https://api.linkedin.com/v2/ugcPosts"
        
        # Required scopes for posting (updated for current LinkedIn API)
        self.scopes = ["openid", "profile", "w_member_social"]
        
    def get_authorization_url(self, redirect_uri="http://localhost:8000/auth/callback"):
        """Generate LinkedIn authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "state": "random_state_string"
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url
    
    def get_access_token(self, authorization_code, redirect_uri="http://localhost:8000/auth/callback"):
        """Exchange authorization code for access token"""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            print("Access token obtained successfully!")
            return self.access_token
        else:
            print(f"Error getting access token: {response.status_code}")
            print(response.text)
            return None
    
    def get_user_profile(self):
        """Get user profile information"""
        if not self.access_token:
            print("No access token available. Please authenticate first.")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(self.profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            # For userinfo endpoint, the ID is in 'sub' field
            self.user_id = profile_data.get("sub") or profile_data.get("id")
            print(f"Profile data: {profile_data}")
            return profile_data
        else:
            print(f"Error getting profile: {response.status_code}")
            print(response.text)
            return None
    
    def create_text_post(self, text_content):
        """Create a text post on LinkedIn"""
        if not self.access_token or not self.user_id:
            print("Please authenticate and get user profile first.")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        post_data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(self.post_url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            print("Post created successfully!")
            return response.json()
        else:
            print(f"Error creating post: {response.status_code}")
            print(response.text)
            return None
    
    def create_article_post(self, text_content, article_title, article_url):
        """Create a post with an article link"""
        if not self.access_token or not self.user_id:
            print("Please authenticate and get user profile first.")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        post_data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": text_content
                            },
                            "originalUrl": article_url,
                            "title": {
                                "text": article_title
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(self.post_url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            print("Article post created successfully!")
            return response.json()
        else:
            print(f"Error creating article post: {response.status_code}")
            print(response.text)
            return None
    
    def post_to_linkedin(self, content):
        """Post content to LinkedIn - main method called by API"""
        try:
            # Use the create_text_post method
            result = self.create_text_post(content)
            
            if result:
                post_id = result.get('id', 'Unknown')
                
                # Return the post ID and URL
                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': f"https://www.linkedin.com/feed/update/{post_id}/"
                }
            else:
                return {'success': False, 'error': 'Failed to create LinkedIn post'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    # Initialize LinkedIn poster with environment variables
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ LinkedIn credentials not configured.")
        print("Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        return
    
    poster = LinkedInPoster(client_id, client_secret)
    
    print("LinkedIn Poster - Social Media Tool")
    print("=" * 40)
    
    # Option to use callback server or manual entry
    use_server = input("Use automatic callback server? (y/n): ").strip().lower() == 'y'
    
    if use_server:
        from callback_server import start_callback_server
        
        # Step 1: Start callback server
        print("\n🚀 Starting callback server...")
        
        # Step 2: Get authorization URL
        auth_url = poster.get_authorization_url()
        print("2. The callback server will automatically capture the response.")
        
        # Step 3: Wait for callback
        auth_code = start_callback_server()
        
        if not auth_code:
            print("❌ Failed to get authorization code from callback server.")
            return
            
    else:
        # Step 1: Get authorization URL
        auth_url = poster.get_authorization_url()
        
        # Step 2: Get authorization code from user
        auth_code = input("\nEnter the authorization code: ").strip()
    
    # Step 3: Exchange code for access token
    if poster.get_access_token(auth_code):
        # Step 4: Get user profile
        profile = poster.get_user_profile()
        if profile:
            print(f"\nWelcome, {profile.get('localizedFirstName', 'User')}!")
            
            # Step 5: Create a post
            while True:
                print("\nWhat would you like to do?")
                print("1. Create a text post")
                print("2. Create an article post")
                print("3. Exit")
                
                choice = input("Enter your choice (1-3): ").strip()
                
                if choice == "1":
                    text_content = input("Enter your post content: ").strip()
                    if text_content:
                        poster.create_text_post(text_content)
                    else:
                        print("Post content cannot be empty.")
                        
                elif choice == "2":
                    text_content = input("Enter your post content: ").strip()
                    article_title = input("Enter article title: ").strip()
                    article_url = input("Enter article URL: ").strip()
                    
                    if text_content and article_title and article_url:
                        poster.create_article_post(text_content, article_title, article_url)
                    else:
                        print("All fields are required for article posts.")
                        
                elif choice == "3":
                    print("Goodbye!")
                    break
                    
                else:
                    print("Invalid choice. Please try again.")
    else:
        print("Failed to get access token. Please try again.")


if __name__ == "__main__":
    main() 