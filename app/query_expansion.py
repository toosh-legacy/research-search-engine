"""
Query expansion and semantic understanding for natural language queries.
Maps casual/common terms to academic terminology.
"""

# Synonym and related term mappings for query expansion
QUERY_EXPANSIONS = {
    # AI/ML casual terms -> academic terms
    "ai": ["artificial intelligence", "machine learning", "deep learning", "neural network"],
    "robot": ["robotics", "autonomous", "control system", "manipulation"],
    "picture": ["image", "computer vision", "visual", "photo"],
    "video": ["video processing", "temporal", "sequence", "motion"],
    "language": ["natural language processing", "NLP", "text", "linguistic", "language model"],
    "chat": ["chatbot", "conversational", "dialogue", "language model", "LLM"],
    "gpt": ["language model", "transformer", "LLM", "generative", "GPT"],
    "llm": ["large language model", "language model", "transformer", "GPT"],
    
    # Computer vision
    "face": ["facial recognition", "face detection", "biometric", "portrait"],
    "object": ["object detection", "instance segmentation", "recognition"],
    "self driving": ["autonomous vehicle", "self-driving", "autonomous driving", "vehicle control"],
    "car": ["vehicle", "autonomous driving", "automotive"],
    
    # Learning types
    "learn": ["learning", "training", "optimization", "gradient"],
    "train": ["training", "learning", "optimization", "supervised"],
    "predict": ["prediction", "forecasting", "regression", "inference"],
    "classify": ["classification", "categorization", "recognition"],
    
    # Data terms
    "data": ["dataset", "data mining", "data analysis", "training data"],
    "big data": ["large-scale", "distributed", "scalable", "big data"],
    "database": ["data management", "storage", "query", "index"],
    
    # Security
    "hack": ["security", "vulnerability", "exploit", "cybersecurity", "attack"],
    "secure": ["security", "cryptography", "authentication", "privacy"],
    "crypto": ["cryptography", "encryption", "blockchain", "security"],
    
    # Web/Network
    "web": ["web application", "internet", "HTTP", "browser"],
    "internet": ["network", "web", "online", "distributed"],
    "cloud": ["cloud computing", "distributed", "scalable", "serverless"],
    
    # Methods
    "faster": ["efficient", "optimization", "speed", "performance"],
    "better": ["improved", "enhanced", "optimized", "superior"],
    "new": ["novel", "recent", "emerging", "state-of-art"],
    "best": ["optimal", "superior", "state-of-art", "benchmark"],
    
    # Application areas
    "medical": ["healthcare", "clinical", "diagnosis", "medical imaging", "biomedical"],
    "health": ["healthcare", "medical", "clinical", "wellness"],
    "money": ["financial", "economic", "market", "trading"],
    "game": ["gaming", "game theory", "reinforcement learning", "strategy"],
    "music": ["audio", "sound", "acoustic", "music generation"],
    "art": ["generative art", "creative", "style transfer", "GAN"],
    
    # Specific models
    "transformer": ["attention", "BERT", "GPT", "self-attention", "encoder-decoder"],
    "bert": ["language model", "transformer", "pre-training", "bidirectional"],
    "gan": ["generative adversarial", "generator", "discriminator", "synthesis"],
    "cnn": ["convolutional", "convnet", "image processing", "feature extraction"],
    "rnn": ["recurrent", "LSTM", "GRU", "sequence", "temporal"],
    "lstm": ["recurrent", "long short-term memory", "sequence modeling"],
    
    # Research areas
    "research": ["study", "investigation", "analysis", "experiment"],
    "survey": ["review", "overview", "systematic review", "literature"],
    "tutorial": ["introduction", "guide", "primer", "overview"],
    "benchmark": ["evaluation", "comparison", "performance", "dataset"],
}

# Common academic term expansions
ACADEMIC_EXPANSIONS = {
    "neural network": ["deep learning", "backpropagation", "activation"],
    "machine learning": ["supervised", "unsupervised", "reinforcement"],
    "deep learning": ["neural network", "CNN", "RNN", "transformer"],
    "reinforcement learning": ["Q-learning", "policy", "reward", "agent"],
    "computer vision": ["image processing", "object detection", "segmentation"],
    "natural language processing": ["NLP", "text mining", "language model"],
    "optimization": ["gradient descent", "convergence", "loss function"],
}

def expand_query(query: str) -> list[str]:
    """
    Expand a casual/natural query into academic terms.
    Returns list of expanded terms to search for.
    """
    query_lower = query.lower()
    terms = [query]  # Always include original query
    
    # Check each expansion mapping
    for casual_term, academic_terms in QUERY_EXPANSIONS.items():
        if casual_term in query_lower:
            terms.extend(academic_terms)
    
    # Check academic term expansions
    for academic_term, related_terms in ACADEMIC_EXPANSIONS.items():
        if academic_term in query_lower:
            terms.extend(related_terms)
    
    return list(set(terms))  # Remove duplicates

def get_search_suggestions(query: str) -> list[str]:
    """
    Get search suggestions based on query.
    Returns list of suggested searches.
    """
    query_lower = query.lower()
    suggestions = []
    
    # Find matching terms
    for casual_term, academic_terms in QUERY_EXPANSIONS.items():
        if casual_term in query_lower:
            suggestions.extend([f"{query} {term}" for term in academic_terms[:3]])
    
    return suggestions[:5]  # Return top 5 suggestions

# Popular search patterns
POPULAR_SEARCHES = [
    "transformer neural networks",
    "deep learning computer vision",
    "reinforcement learning agents",
    "natural language processing",
    "generative adversarial networks",
    "object detection real-time",
    "medical image analysis",
    "autonomous driving perception",
    "graph neural networks",
    "federated learning privacy",
    "explainable AI interpretability",
    "zero-shot learning",
    "few-shot learning meta-learning",
    "self-supervised learning",
    "multimodal learning vision language",
]
