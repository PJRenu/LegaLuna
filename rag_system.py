from model_loader import llm
from knowledge_base import kb
from language_handler import lang_processor
import logging

# Set up logging
logging.basicConfig(
    filename='logs/rag_system.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def answer_legal_question(query):
    """Main function to answer legal questions with RAG"""
    logging.info(f"Received query: {query}")
    
    # Detect language
    language = lang_processor.detect_language(query)
    logging.info(f"Detected language: {language}")
    
    # Preprocess query if in Hindi
    if language == 'hi':
        query = lang_processor.preprocess_hindi(query)
        model_query = lang_processor.translate_hindi_to_english(query)
    else:
        model_query = query
    
    # Retrieve relevant legal information
    retrieved_docs = kb.retrieve(model_query, language)
    logging.info(f"Retrieved {len(retrieved_docs)} documents")
    
    if not retrieved_docs:
        # Fallback to direct LLM response when no documents are retrieved
        logging.info("No documents retrieved, falling back to direct LLM response")
        
        if language == 'hi':
            fallback_prompt = f"""आप भारतीय कानूनों पर एक सहायक कानूनी सलाहकार हैं।
उपयोगकर्ता के प्रश्न के आधार पर केवल सामान्य जानकारी प्रदान करें।
विशिष्ट कानूनी सलाह देने से बचें।
अपने उत्तर में यह स्पष्ट करें कि आप केवल सामान्य जानकारी प्रदान कर रहे हैं और महत्वपूर्ण मामलों के लिए योग्य वकील से परामर्श करने की सलाह दें।

प्रश्न: {query}

सरल, स्पष्ट भाषा में उत्तर दें। यदि आप निश्चित नहीं हैं, तो जानकारी बनाने के बजाय ऐसा कहें।"""
        else:
            fallback_prompt = f"""You are a helpful legal assistant for Indian citizens.
Provide only general information based on the user's question.
Avoid giving specific legal advice.
Make it clear in your response that you are providing general information only and recommend consulting with a qualified lawyer for important matters.

Question: {query}

Answer in simple, clear language. If you are unsure, say so instead of making up information."""
        
        model_response = llm.generate_response(fallback_prompt)
        
        # Post-process response for Hindi queries
        if language == 'hi' and lang_processor.detect_language(model_response) == 'en':
            model_response = lang_processor.translate_english_to_hindi(model_response)
        
        return model_response
    
    # If documents were retrieved, continue with the existing RAG approach
    # Prepare context from retrieved documents
    context_docs = [doc["content"] for doc in retrieved_docs]
    context = "\n\n".join(context_docs)
    
    # Create prompt based on language
    if language == 'hi':
        prompt = f"""आप भारतीय नागरिकों के लिए एक सहायक कानूनी सहायक हैं।
निम्नलिखित भारतीय कानूनी जानकारी के आधार पर प्रश्न का उत्तर दें:

{context}

प्रश्न: {query}

सरल, स्पष्ट भाषा में उत्तर दें। यदि आप प्रदान की गई जानकारी के आधार पर उत्तर नहीं जानते हैं, तो जानकारी बनाने के बजाय ऐसा कहें।"""
    else:
        prompt = f"""You are a helpful legal assistant for Indian citizens.
Answer the question based on the following Indian legal information:

{context}

Question: {query}

Answer in simple, clear language. If you don't know the answer based on the provided information, say so instead of making up information."""
    
    # Generate response
    model_response = llm.generate_response(prompt)
    logging.info(f"Generated response of length: {len(model_response)}")
    
    # Post-process response for Hindi queries
    if language == 'hi' and lang_processor.detect_language(model_response) == 'en':
        model_response = lang_processor.translate_english_to_hindi(model_response)
    
    return model_response