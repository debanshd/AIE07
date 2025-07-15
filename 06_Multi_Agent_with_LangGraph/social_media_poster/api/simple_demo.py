#!/usr/bin/env python3
"""
Simplified demo of the ML Paper Social Media Poster
"""

import os
import tempfile
import webbrowser
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from linkedin_poster import LinkedInPoster
from callback_server import start_callback_server

class SimpleMLPosterDemo:
    """Simplified version for demonstration"""
    
    def __init__(self, openai_api_key=None, tavily_api_key=None, linkedin_client_id=None, linkedin_client_secret=None):
        if openai_api_key:
            self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)
        else:
            self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.working_dir = Path(tempfile.mkdtemp())
        self.tavily_api_key = tavily_api_key
        # LinkedIn credentials - use provided values or environment variables
        self.linkedin_client_id = linkedin_client_id or os.environ.get("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = linkedin_client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET")
        
    def research_paper(self, paper_title, paper_url=None):
        """Research phase - analyze the paper"""
        print("🔍 Research Team: Analyzing paper...")
        
        research_prompt = f"""
        You are a research assistant analyzing the ML paper: "{paper_title}"
        {f"URL: {paper_url}" if paper_url else ""}
        
        Provide a comprehensive analysis including:
        1. Main contributions
        2. Key innovations
        3. Impact on the field
        4. Practical applications
        5. Why it's significant
        
        Write a detailed summary for social media content creation.
        """
        
        response = self.llm.invoke([HumanMessage(content=research_prompt)])
        return response.content
    
    def create_content(self, research_summary, platform="LinkedIn"):
        """Content creation phase"""
        print("✍️ Content Team: Creating social media post...")
        
        platform_guidelines = {
            "LinkedIn": "Professional tone, 2000-2500 characters MAX (strict limit), engaging for professionals, include relevant hashtags, use Unicode bold characters and proper formatting"
        }
        
        content_prompt = f"""
        Based on this research about an ML paper:
        {research_summary}
        
        Create an engaging LinkedIn post.
        
        CRITICAL REQUIREMENTS for LinkedIn:
        - {platform_guidelines.get(platform, platform_guidelines['LinkedIn'])}
        - MUST be under 2500 characters (LinkedIn has a 3000 char limit, stay well under)
        - NEVER use markdown syntax: NO **, *, __, [], (), etc.
        - For emphasis, use ONLY Unicode bold characters like: 𝗞𝗲𝘆 𝗜𝗻𝗻𝗼𝘃𝗮𝘁𝗶𝗼𝗻𝘀, 𝗧𝗿𝗮𝗻𝘀𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝘃𝗲 𝗜𝗺𝗽𝗮𝗰𝘁
        - Use line breaks (\\n) between paragraphs and sections
        - Use section separators: -------------------- (20 hyphens)
        - Use bullet points with emojis: 🔹, 🔸, • (NOT dashes or asterisks)
        - Make it accessible to both technical and non-technical audiences
        - Include a compelling hook in the first line
        - Highlight the key innovation concisely
        - End with a call to action or thought-provoking question
        - Use strategic emojis for visual appeal
        - Be concise but impactful
        - DO NOT include character count or any meta information
        
        FORMATTING EXAMPLES - Use these exact Unicode bold characters:
        - 𝗞𝗲𝘆 𝗜𝗻𝗻𝗼𝘃𝗮𝘁𝗶𝗼𝗻𝘀 (for section headers)
        - 𝗦𝗲𝗹𝗳-𝗔𝘁𝘁𝗲𝗻𝘁𝗶𝗼𝗻 𝗠𝗲𝗰𝗵𝗮𝗻𝗶𝘀𝗺 (for key terms)
        - 𝗧𝗿𝗮𝗻𝘀𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝘃𝗲 𝗜𝗺𝗽𝗮𝗰𝘁 (for impact sections)
        - 𝗣𝗿𝗮𝗰𝘁𝗶𝗰𝗮𝗹 𝗔𝗽𝗽𝗹𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀 (for applications)
        
        IMPORTANT: 
        - Replace ALL ** text ** with Unicode bold: 𝘁𝗲𝘅𝘁
        - Replace ALL * text * with Unicode bold: 𝘁𝗲𝘅𝘁
        - Do NOT include character count at the end
        - Do NOT use any markdown formatting whatsoever
        
        Generate the post ready for direct publishing on LinkedIn.
        """
        
        response = self.llm.invoke([HumanMessage(content=content_prompt)])
        return response.content
    
    def verify_content(self, content, platform="LinkedIn"):
        """Verification phase"""
        print("✅ Verification Team: Checking content...")
        
        verify_prompt = f"""
        Review and FIX this LinkedIn post:
        
        {content}
        
        CRITICAL VERIFICATION TASKS:
        1. Check for LinkedIn formatting compliance:
           - NO markdown syntax (**, *, __, etc.) - LinkedIn doesn't support it
           - Convert any ** text ** to Unicode bold: 𝘁𝗲𝘅𝘁
           - Convert any * text * to Unicode bold: 𝘁𝗲𝘅𝘁
           - Ensure proper Unicode bold characters are used for emphasis
        
        2. Check content requirements:
           - Length under 3000 characters (preferably under 2500)
           - Appropriate professional tone for LinkedIn
           - Engagement potential
           - Professional quality
           - Remove any character count information
        
        3. Fix formatting issues:
           - Replace section headers with Unicode bold: 𝗞𝗲𝘆 𝗜𝗻𝗻𝗼𝘃𝗮𝘁𝗶𝗼𝗻𝘀
           - Use proper line breaks and section separators
           - Use emojis for bullet points (🔹, 🔸, •)
        
        IMPORTANT: 
        - If you find ANY markdown formatting (**, *, etc.), you MUST fix it
        - Convert **text** to Unicode bold equivalent
        - Remove any character count lines
        - Ensure proper LinkedIn formatting
        
        RESPONSE FORMAT:
        - If no issues found: respond with "APPROVED" followed by the original post
        - If issues found: provide ONLY the corrected post content, ready for LinkedIn publishing
        - Do NOT include any commentary, explanations, or meta-text
        - Do NOT include phrases like "Here's the corrected version" or "This version is ready"
        """
        
        response = self.llm.invoke([HumanMessage(content=verify_prompt)])
        return response.content
    
    def generate_post(self, paper_title, paper_url=None, platform="LinkedIn"):
        """Complete workflow"""
        print(f"🎯 Generating {platform} post for: {paper_title}")
        
        # Step 1: Research
        research = self.research_paper(paper_title, paper_url)
        
        # Step 2: Create content
        content = self.create_content(research, platform)
        
        # Step 3: Verify and get corrected content
        verification = self.verify_content(content, platform)
        
        # Extract corrected content from verification response
        if verification.startswith("APPROVED"):
            # If approved, use the original content
            final_content = content
        else:
            # Use the corrected content from verification
            final_content = verification
        
        # Save to file
        post_file = self.working_dir / f"{paper_title.replace(' ', '_')}_post.txt"
        with open(post_file, 'w') as f:
            f.write(f"=== {platform} Post for: {paper_title} ===\n\n")
            f.write(final_content)
            f.write(f"\n\n=== Verification Results ===\n")
            f.write(verification)
        
        print(f"📄 Post saved to: {post_file}")
        return final_content, str(post_file)
    
    def post_to_linkedin(self, content, client_id, client_secret):
        """Post to LinkedIn with enhanced error handling"""
        print("🚀 Posting to LinkedIn...")
        
        # Check content length and truncate if necessary
        max_length = 3000
        if len(content) > max_length:
            print(f"⚠️  Content too long ({len(content)} chars). Truncating to {max_length} chars...")
            content = content[:max_length-3] + "..."
            print(f"✂️  Content truncated to {len(content)} characters")
        
        try:
            poster = LinkedInPoster(client_id, client_secret)
            
            # Authenticate
            print("🔐 Starting authentication...")
            print("This will open a browser window for LinkedIn authentication...")
            
            auth_url = poster.get_authorization_url()
            
            # Use callback server for seamless authentication
            print("📡 Starting callback server to capture authentication...")
            auth_code = start_callback_server()
            
            if not auth_code:
                print("❌ Authentication failed - no authorization code received")
                return False
            
            print("✅ Authorization code received")
            
            # Get access token and profile
            print("🔑 Exchanging code for access token...")
            if poster.get_access_token(auth_code):
                print("✅ Access token obtained")
                
                print("👤 Getting user profile...")
                profile = poster.get_user_profile()
                if profile:
                    name = profile.get('name') or profile.get('given_name', 'User')
                    print(f"✅ Authenticated as: {name}")
                    
                    # Post content
                    print("📝 Creating LinkedIn post...")
                    result = poster.create_text_post(content)
                    if result:
                        print("🎉 Successfully posted to LinkedIn!")
                        print(f"📊 Post ID: {result.get('id', 'N/A')}")
                        return True
                    else:
                        print("❌ Failed to create post")
                        return False
                else:
                    print("❌ Failed to get user profile")
                    return False
            else:
                print("❌ Failed to get access token")
                return False
                
        except Exception as e:
            print(f"❌ Error during LinkedIn posting: {str(e)}")
            return False
    
    def quick_linkedin_post(self, text_content):
        """Quick function to post any text content to LinkedIn"""
        if not self.linkedin_client_id or not self.linkedin_client_secret:
            print("❌ LinkedIn credentials not configured. Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
            return False
        return self.post_to_linkedin(text_content, self.linkedin_client_id, self.linkedin_client_secret)
    
    def interactive_linkedin_post(self):
        """Interactive function to create and post content to LinkedIn"""
        print("📝 Interactive LinkedIn Posting")
        print("=" * 40)
        
        content = input("Enter your LinkedIn post content:\n").strip()
        if not content:
            print("❌ No content provided")
            return False
        
        print("\n📄 Your content:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        confirm = input("\nPost this content to LinkedIn? (y/n): ").strip().lower() == 'y'
        if confirm:
            return self.quick_linkedin_post(content)
        else:
            print("❌ Posting cancelled")
            return False

def main():
    """Demo the system"""
    demo = SimpleMLPosterDemo()
    
    # Example papers to choose from
    papers = [
        ("Attention Is All You Need", "https://arxiv.org/abs/1706.03762"),
        ("BERT: Pre-training of Deep Bidirectional Transformers", "https://arxiv.org/abs/1810.04805"),
        ("GPT-3: Language Models are Few-Shot Learners", "https://arxiv.org/abs/2005.14165"),
        ("ResNet: Deep Residual Learning for Image Recognition", "https://arxiv.org/abs/1512.03385")
    ]
    
    print("🎯 ML Paper Social Media Poster Demo")
    print("=" * 50)
    
    print("\nChoose mode:")
    print("1. Generate post from ML paper")
    print("2. Post custom content to LinkedIn")
    
    mode = input("Select mode (1-2) [1]: ").strip() or "1"
    
    if mode == "2":
        # Direct LinkedIn posting mode
        success = demo.interactive_linkedin_post()
        if success:
            print("✅ Content posted successfully!")
        else:
            print("❌ Posting failed or cancelled")
        return
    
    # ML Paper mode
    print("\nAvailable papers:")
    for i, (title, url) in enumerate(papers, 1):
        print(f"{i}. {title}")
    
    try:
        choice = int(input("\nSelect a paper (1-4): ")) - 1
        if 0 <= choice < len(papers):
            paper_title, paper_url = papers[choice]
        else:
            print("Invalid choice, using default paper")
            paper_title, paper_url = papers[0]
    except:
        print("Invalid input, using default paper")
        paper_title, paper_url = papers[0]
    
    print(f"\n📄 Selected: {paper_title}")
    
    # Generate the LinkedIn post
    print(f"\n🔄 Generating LinkedIn post...")
    content, post_file = demo.generate_post(paper_title, paper_url, "LinkedIn")
    
    print(f"\n📄 Generated Content:")
    print("=" * 50)
    print(content)
    print("=" * 50)
    
    # LinkedIn integration options
    print("\n🔗 LinkedIn Integration Available")
    print("Options:")
    print("1. Post to LinkedIn now")
    print("2. Save content only")
    print("3. Edit content before posting")
    
    choice = input("Choose option (1-3) [2]: ").strip() or "2"
    
    if choice == "1":
        print("\n🚀 Proceeding with LinkedIn posting...")
        success = demo.quick_linkedin_post(content)
        if success:
            print("✅ Post successfully published to LinkedIn!")
        else:
            print("❌ Failed to post to LinkedIn")
                
    elif choice == "3":
        print("\n✏️ Edit your content:")
        print("Current content:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        edited_content = input("\nEnter your edited content (or press Enter to keep original): ").strip()
        if edited_content:
            content = edited_content
            print("✅ Content updated")
            
            # Ask if they want to post the edited content
            post_edited = input("Post the edited content to LinkedIn? (y/n): ").strip().lower() == 'y'
            if post_edited:
                success = demo.quick_linkedin_post(content)
                if success:
                    print("✅ Edited post successfully published to LinkedIn!")
                else:
                    print("❌ Failed to post edited content to LinkedIn")
        else:
            print("No changes made to content")
    
    else:
        print("💾 Content saved for later use")
    
    print(f"\n✅ Demo completed! Post saved to: {post_file}")
    print(f"📁 Working directory: {demo.working_dir}")

if __name__ == "__main__":
    main() 