# agents/campaign_agent.py

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class CampaignAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def create_strategy(self, goal, platform, budget):
        """Generate campaign strategy with Gemini"""
        org_id = get_org_id()
        
        # Get platform knowledge
        platform_context = self._get_platform_knowledge(platform)
        
        # Build prompt
        prompt = f"""You are an expert digital marketing strategist. Create a detailed campaign plan.

CAMPAIGN DETAILS:
- Goal: {goal}
- Platform: {platform}
- Budget: ${budget}

PLATFORM KNOWLEDGE:
{platform_context}

Generate a complete campaign strategy as JSON with this EXACT structure:
{{
  "targeting": {{
    "demographics": ["target1", "target2"],
    "interests": ["interest1", "interest2"],
    "locations": ["location1"]
  }},
  "placements": ["Feed", "Stories"],
  "bid_strategy": "cost_cap or lowest_cost",
  "predictions": {{
    "impressions": 50000,
    "ctr": 1.2,
    "cpc": 5.50,
    "conversions": 250,
    "cpa": 120,
    "roas": 3.5
  }},
  "creative_brief": {{
    "count": 5,
    "formats": ["carousel"],
    "tone": "professional",
    "hooks": ["problem_solution", "metric_led"],
    "copy_specs": {{
      "headline_max_chars": 70,
      "body_max_chars": 150
    }},
    "asset_specs": {{
      "image_ratio": "1.91:1",
      "min_resolution": "1200x627"
    }}
  }}
}}

Return ONLY valid JSON, no markdown, no explanations."""

        try:
            # Generate with Gemini
            response = self.model.generate_content(prompt)
            
            # Clean response (remove markdown if present)
            text = response.text.strip()
            if text.startswith('```json'):
                text = text.split('```json')[1].split('```')[0].strip()
            elif text.startswith('```'):
                text = text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            strategy = json.loads(text)
            
            # Save to database
            result = supabase.table('campaign_plans').insert({
                'org_id': org_id,
                'goal': goal,
                'platform': platform,
                'budget': float(budget),
                'targeting': strategy.get('targeting'),
                'placements': strategy.get('placements'),
                'bid_strategy': strategy.get('bid_strategy'),
                'predictions': strategy.get('predictions'),
                'status': 'strategy_pending'
            }).execute()
            
            campaign_id = result.data[0]['id']
            
            # Save creative brief
            supabase.table('creative_briefs').insert({
                'campaign_plan_id': campaign_id,
                'org_id': org_id,
                'formats': strategy['creative_brief'].get('formats'),
                'tone': strategy['creative_brief'].get('tone'),
                'specs': strategy['creative_brief']
            }).execute()
            
            return {
                'campaign_id': campaign_id,
                'strategy': strategy
            }
            
        except Exception as e:
            print(f"Error generating strategy: {str(e)}")
            raise e
    
    def _get_platform_knowledge(self, platform):
        """Get platform-specific best practices"""
        knowledge = {
            'linkedin': """
LinkedIn Best Practices:
- B2B focus, professional tone essential
- Carousel ads: 2x engagement vs single image
- Targeting: Job titles, company size, industry
- Lead gen forms reduce friction
- Optimal times: Tue-Thu, 9-11am
- Image specs: 1200x627px (1.91:1 ratio)
- Character limits: Headline 70, Body 150
- Typical CTR: 0.5-1.0%, CPC: $5-15, CPL: $50-150
            """,
            'meta': """
Meta (Facebook/Instagram) Best Practices:
- Stories and Reels: highest engagement
- Interest-based + lookalike targeting
- Retargeting essential for conversions
- Image ratio: 1:1 or 4:5 for feed, 9:16 for stories
- Character limits: Headline 40, Body 125
- Typical CTR: 0.9-2.5%, CPC: $0.50-3.00
- Test multiple ad variations
            """,
            'tiktok': """
TikTok Best Practices:
- Short vertical video (15-30 sec)
- Authentic, raw content beats polished
- Hook in first 3 seconds critical
- 9:16 aspect ratio required
- Gen Z and Millennial audience
- Typical CTR: 1.5-3.0%, CPC: $0.30-1.50
- Use trending sounds and effects
            """
        }
        return knowledge.get(platform, "No platform knowledge available")