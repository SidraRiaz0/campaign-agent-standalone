"""
Supabase Client for Marketing AI Agent
Handles all database connections with pgvector for RAG
"""

from supabase import create_client, Client
import streamlit as st
from typing import Optional, Dict, List, Any
import os

class SupabaseManager:
    """Manages Supabase connection and operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Create Supabase client from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first (for deployed app)
            if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["anon_key"]
            else:
                # Fallback to environment variables (local dev)
                url = os.getenv("SUPABASE_URL")
                key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                raise ValueError("Supabase credentials not found in secrets or environment")
            
            self.client = create_client(url, key)
            print("✅ Supabase client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if client is properly initialized"""
        return self.client is not None
    
    # ==================== Knowledge Docs (RAG) ====================
    
    def store_knowledge_chunk(
        self, 
        content: str, 
        embedding: List[float], 
        org_id: Optional[str] = None,
        source: str = "manual_upload",
        chunk_index: int = 0,
        metadata: Dict = None
    ) -> Dict:
        """Store a knowledge chunk with its embedding"""
        if not self.is_connected():
            return {"success": False, "error": "Not connected to Supabase"}
        
        try:
            # Store source and chunk_index in metadata to match schema
            full_metadata = metadata or {}
            full_metadata['source'] = source
            full_metadata['chunk_index'] = chunk_index
            
            data = {
                "content": content,
                "embedding": embedding,
                "org_id": org_id,
                "doc_type": "knowledge_chunk",
                "metadata": full_metadata
            }
            
            result = self.client.table("knowledge_docs").insert(data).execute()
            
            if result.data:
                return {"success": True, "id": result.data[0]["id"]}
            else:
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def semantic_search(
        self, 
        query_embedding: List[float], 
        org_id: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        """Perform semantic search using pgvector cosine similarity"""
        if not self.is_connected():
            print("❌ Not connected to Supabase")
            return []
        
        try:
            result = self.client.rpc(
                'match_knowledge_docs',
                {
                    'query_embedding': query_embedding,
                    'match_org_id': org_id,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
            return []
    
    def count_knowledge_chunks(self, org_id: Optional[str] = None) -> int:
        """Count total knowledge chunks"""
        if not self.is_connected():
            return 0
        
        try:
            query = self.client.table("knowledge_docs").select("id", count="exact")
            
            if org_id is None:
                query = query.is_("org_id", "null")
            else:
                query = query.eq("org_id", org_id)
            
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            print(f"❌ Count failed: {e}")
            return 0
    
    def test_connection(self) -> Dict:
        """Test database connectivity"""
        if not self.is_connected():
            return {"success": False, "error": "Client not initialized"}
        
        try:
            # Test with knowledge_docs table instead
            result = self.client.table("knowledge_docs").select("id").limit(1).execute()
            return {
                "success": True, 
                "message": "Successfully connected to Supabase",
                "has_data": len(result.data) > 0 if result.data else False
            }
        except Exception as e:
            return {"success": False, "error": str(e)}