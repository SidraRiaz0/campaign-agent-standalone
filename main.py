import streamlit as st
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from campaign_agent import CampaignAgent
from brand_rag import BrandRAG

st.set_page_config(
    page_title="Campaign Performance Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for landing page
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .feature-box {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("<h1 class='main-header'>📊 Campaign Performance Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>AI-powered campaign optimization. Predict ROAS before spending a dollar.</p>", unsafe_allow_html=True)

st.markdown("---")

# Two columns: Campaign Input & Brand Upload
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 Campaign Strategy")
    
    goal = st.text_area(
        "What's your campaign goal?",
        placeholder='e.g., "Launch AI analytics tool to enterprise customers, drive 100 demo bookings in Q1"',
        height=120,
        help="Be specific about target audience, objectives, and success metrics"
    )
    
    # Campaign parameters in 3 columns
    c1, c2, c3 = st.columns(3)
    
    with c1:
        budget = st.number_input(
            "Budget ($)",
            min_value=500,
            max_value=100000,
            value=5000,
            step=500
        )
    
    with c2:
        duration = st.number_input(
            "Duration (days)",
            min_value=3,
            max_value=90,
            value=14
        )
    
    with c3:
        industry = st.selectbox(
            "Industry",
            ["B2B SaaS", "E-commerce", "Fintech", "Healthcare", "Education", "Other"]
        )
    
    # Analyze button
    if st.button("📊 Generate Campaign Strategy", type="primary", use_container_width=True):
        if not goal.strip():
            st.error("Please describe your campaign goal")
        else:
            with st.spinner("🤖 AI Agent analyzing... (10-15 seconds)"):
                try:
                    agent = CampaignAgent()
                    
                    # Get brand context if available
                    org_id = st.session_state.get('org_id', None)
                    brand_context = []
                    
                    if org_id:
                        rag = BrandRAG()
                        brand_context = rag.retrieve_brand_context(
                            brand_id=org_id,
                            query=goal,
                            top_k=3
                        )
                    
                    recommendations = agent.analyze_campaign(
                        campaign_goal=goal,
                        budget=budget,
                        duration_days=duration,
                        industry=industry,
                        brand_context=brand_context
                    )
                    
                    st.session_state.recommendations = recommendations
                    st.session_state.params = {
                        'goal': goal,
                        'budget': budget,
                        'duration': duration,
                        'industry': industry
                    }
                    
                    st.success("✅ Strategy generated!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    # Fallback
                    agent = CampaignAgent()
                    recommendations = agent._get_fallback_recommendations(goal, budget, duration)
                    st.session_state.recommendations = recommendations

with col2:
    st.markdown("### 📚 Brand Knowledge")
    
    with st.expander("Upload Brand Docs (Optional)", expanded=False):
        st.caption("Train AI on your brand voice")
        
        uploaded_docs = st.file_uploader(
            "Upload PDFs",
            type=['pdf'],
            accept_multiple_files=True,
            help="Brand guidelines, past campaigns, strategy docs"
        )
        
        if uploaded_docs:
            if st.button("🚀 Process Documents", use_container_width=True):
                with st.spinner("Processing..."):
                    try:
                        import io
                        from PyPDF2 import PdfReader
                        
                        rag = BrandRAG()
                        org_id = st.session_state.get('org_id', None)
                        
                        total_chunks = 0
                        
                        for uploaded_file in uploaded_docs:
                            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                            
                            full_text = ""
                            for page in pdf_reader.pages:
                                text = page.extract_text()
                                if text:
                                    text = text.replace('\x00', '').replace('\u0000', '')
                                    full_text += text + "\n"
                            
                            # Chunk text
                            chunks = []
                            paragraphs = full_text.split('\n\n')
                            current_chunk = ""
                            
                            for para in paragraphs:
                                para = para.strip()
                                if not para:
                                    continue
                                
                                if len(current_chunk) + len(para) < 500:
                                    current_chunk += para + "\n\n"
                                else:
                                    if current_chunk.strip():
                                        clean = current_chunk.strip().replace('\x00', '')
                                        if clean:
                                            chunks.append(clean)
                                    current_chunk = para + "\n\n"
                            
                            if current_chunk.strip():
                                clean = current_chunk.strip().replace('\x00', '')
                                if clean:
                                    chunks.append(clean)
                            
                            if chunks:
                                success = rag.store_brand_examples(
                                    brand_id=org_id,
                                    examples=chunks,
                                    content_type='brand_knowledge',
                                    source=uploaded_file.name
                                )
                                
                                if success:
                                    total_chunks += len(chunks)
                        
                        if total_chunks > 0:
                            st.success(f"✅ Stored {total_chunks} chunks!")
                            if not org_id:
                                st.session_state.org_id = "demo-user"
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Display recommendations if available
if 'recommendations' in st.session_state:
    st.markdown("---")
    st.markdown("## 💡 AI-Generated Strategy")
    
    rec = st.session_state.recommendations
    params = st.session_state.params
    
    # Budget allocation
    st.markdown("### 💰 Budget Allocation")
    cols = st.columns(len(rec['budget_allocation']))
    
    for idx, (platform, data) in enumerate(rec['budget_allocation'].items()):
        with cols[idx]:
            st.metric(platform, f"${data['amount']:,.0f}", f"{data['percentage']}%")
    
    # Predicted metrics
    st.markdown("---")
    st.markdown("### 📈 Predicted Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Leads", f"{rec['predicted_metrics']['leads']:,}")
    with col2:
        st.metric("Target CPA", f"${rec['predicted_metrics']['cpa']:.0f}")
    with col3:
        st.metric("Predicted ROAS", f"{rec['predicted_metrics']['roas']:.1f}x")
    with col4:
        st.metric("Expected CTR", f"{rec['predicted_metrics']['ctr']:.1f}%")
    
    # Optimization tips
    st.markdown("---")
    st.markdown("### 🎯 Optimization Strategy")
    
    for i, tip in enumerate(rec['optimization_tips'], 1):
        st.markdown(f"**{i}.** {tip}")
    
    # Risk factors
    if rec.get('risk_factors'):
        st.markdown("---")
        st.markdown("### ⚠️ Risk Factors")
        for risk in rec['risk_factors']:
            st.warning(risk)
    
    # Full analysis
    with st.expander("📄 View Full AI Analysis"):
        st.markdown(rec.get('full_analysis', 'No detailed analysis available'))

# Footer
st.markdown("---")
st.caption("Powered by AI • Google Gemini 2.0 • sentence-transformers • pgvector")