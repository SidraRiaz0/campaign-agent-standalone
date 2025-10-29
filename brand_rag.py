from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import supabase_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase_client import SupabaseManager

class BrandRAG:
    """
    Retrieval Augmented Generation for brand voice
    Stores and retrieves brand examples using embeddings in Supabase with pgvector
    """
    
    def __init__(self):
        """Initialize RAG system with Supabase and sentence-transformers"""
        
        # Initialize sentence transformer for embeddings
        self.device = 'cpu'  # Force CPU for Mac compatibility
        
        print("📄 Loading sentence transformer model...")
        try:
            # Load model with explicit CPU device (all-MiniLM-L6-v2 = 384 dimensions)
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            print("✅ Sentence transformer loaded successfully (384-dim embeddings)")
        except Exception as e:
            print(f"❌ Failed to load embeddings model: {e}")
            self.embedder = None
        
        # Initialize Supabase client
        print("🔌 Connecting to Supabase...")
        try:
            self.db = SupabaseManager()
            if self.db.is_connected():
                print("✅ Supabase connected successfully")
                # Test knowledge count
                count = self.db.count_knowledge_chunks(org_id=None)
                print(f"📚 Platform knowledge chunks available: {count}")
            else:
                print("⚠️ Supabase connection failed")
                self.db = None
        except Exception as e:
            print(f"❌ Supabase initialization failed: {e}")
            self.db = None
    
    def create_embedding(self, text: str):
        """Create 384-dim embedding for text using sentence-transformers"""
        if self.embedder is None:
            # Fallback: return random embedding (for testing only)
            print("⚠️ Using random embedding fallback")
            return np.random.rand(384).tolist()
        
        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️ Embedding creation failed: {e}")
            return np.random.rand(384).tolist()
    
    def store_brand_examples(
        self, 
        brand_id: str, 
        examples: list, 
        content_type: str = 'example_post',
        source: str = 'manual_upload'
    ):
        """Store brand examples in Supabase with embeddings"""
        if not self.db or not self.db.is_connected():
            print("❌ Supabase not available")
            return False
        
        try:
            success_count = 0
            
            for idx, example in enumerate(examples):
                # Create embedding
                embedding = self.create_embedding(example)
                
                # Store in Supabase
                result = self.db.store_knowledge_chunk(
                    content=example,
                    embedding=embedding,
                    org_id=brand_id,
                    source=source,
                    chunk_index=idx,
                    metadata={
                        'content_type': content_type,
                        'length': len(example)
                    }
                )
                
                if result['success']:
                    success_count += 1
                else:
                    print(f"⚠️ Failed to store chunk {idx}: {result.get('error')}")
            
            print(f"✅ Stored {success_count}/{len(examples)} examples")
            return success_count == len(examples)
            
        except Exception as e:
            print(f"❌ Error storing examples: {e}")
            return False
    
    def retrieve_brand_context(
        self, 
        brand_id: str, 
        query: str, 
        top_k: int = 3,
        include_platform: bool = True
    ):
        """Retrieve relevant brand examples using semantic search with pgvector"""
        if not self.db or not self.db.is_connected():
            print("⚠️ Supabase not available, using default examples")
            return self._get_default_examples()
        
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            results = []
            
            # Search brand-specific knowledge
            if brand_id:
                brand_results = self.db.semantic_search(
                    query_embedding=query_embedding,
                    org_id=brand_id,
                    limit=top_k,
                    threshold=0.5
                )
                results.extend(brand_results)
                print(f"📚 Found {len(brand_results)} brand-specific results")
            
            # Also search platform knowledge if requested
            if include_platform and len(results) < top_k:
                remaining = top_k - len(results)
                platform_results = self.db.semantic_search(
                    query_embedding=query_embedding,
                    org_id=None,
                    limit=remaining,
                    threshold=0.5
                )
                results.extend(platform_results)
                print(f"📚 Found {len(platform_results)} platform knowledge results")
            
            if results:
                # Extract content from results
                examples = [r['content'] for r in results[:top_k]]
                print(f"✅ Retrieved {len(examples)} relevant examples")
                return examples
            else:
                print("⚠️ No results found, using defaults")
                return self._get_default_examples()
                
        except Exception as e:
            print(f"⚠️ RAG retrieval failed: {e}, using defaults")
            return self._get_default_examples()
    
    def _get_default_examples(self):
        """Default B2B SaaS examples if no brand data available"""
        return [
            """Are you still manually pulling data from 5 different tools?

We talked to 200+ startup founders. 73% said they lose 6+ hours per week just gathering basic metrics.

Here's what changed:
→ One dashboard. All your data.
→ Zero SQL required.
→ Insights in minutes, not days.

Try it free for 14 days.""",

            """Question for founders: When was the last time you made a product decision based on data vs. a hunch?

Teams that track retention weekly grow 2.3x faster.

You don't need a data team. You need the right tool.""",

            """Real talk: Most analytics tools were built for enterprises with data teams.

You're a startup. You need something that works today.

✅ Connect in 5 minutes
✅ Pre-built dashboards
✅ Plain English insights"""
        ]
    
    def get_stats(self, org_id: str = None):
        """Get RAG system statistics"""
        if not self.db or not self.db.is_connected():
            return {
                'connected': False,
                'chunks': 0,
                'embedder_loaded': self.embedder is not None
            }
        
        try:
            chunk_count = self.db.count_knowledge_chunks(org_id=org_id)
            
            return {
                'connected': True,
                'chunks': chunk_count,
                'embedder_loaded': self.embedder is not None,
                'embedding_dim': 384,
                'model': 'all-MiniLM-L6-v2'
            }
        except Exception as e:
            print(f"❌ Failed to get stats: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
