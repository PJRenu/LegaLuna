import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
class LegalKnowledgeBase:
    def __init__(self, docs_dir="legal_docs"):
        self.docs_dir = docs_dir
        self.documents = []
        self.document_embeddings = []
        self.embedding_model = None
        self.faiss_index = None;
        self.load_embedding_model()
        self.load_documents()
    
    def load_embedding_model(self):
        """Load a multilingual sentence embedding model"""
        # This model supports both Hindi and English
        print("Loading multilingual embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        print("Embedding model loaded")
    
    def load_documents(self):
        """Load legal documents from files or use samples if not available"""
        if os.path.exists(self.docs_dir) and any(f.endswith('.txt') or f.endswith('.json') for f in os.listdir(self.docs_dir)):
            print(f"Loading documents from {self.docs_dir}...")
            # Load from text files
            for filename in os.listdir(self.docs_dir):
                if filename.endswith('.txt'):
                    with open(os.path.join(self.docs_dir, filename), 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            self.documents.append({
                                "content": content,
                                "source": filename,
                                "language": "en"  # Assume English by default
                            })
                elif filename.endswith('.json'):
                    with open(os.path.join(self.docs_dir, filename), 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    if "content" in item:
                                        self.documents.append(item)
                            elif isinstance(data, dict) and "content" in data:
                                self.documents.append(data)
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON file: {filename}")
        else:
            print("Using sample legal documents...")
            # Sample documents in both Hindi and English
            self.documents = [
                {
                    "content": "Under the Indian Rent Control Act, tenants have protection against arbitrary eviction without proper notice. Landlords must provide at least 3 months' notice before asking a tenant to vacate the premises.",
                    "source": "rental_laws.txt",
                    "language": "en"
                },
                {
                    "content": "To file an FIR (First Information Report), visit the nearest police station with jurisdiction over the crime area. The police are obligated to register your complaint under Section 154 of the Criminal Procedure Code.",
                    "source": "criminal_procedure.txt",
                    "language": "en"
                },
                {
                    "content": "Under the Protection of Women from Domestic Violence Act, 2005, women can seek protection orders, residence orders, and monetary relief. The law covers physical, sexual, verbal, emotional, and economic abuse.",
                    "source": "domestic_violence.txt",
                    "language": "en"
                },
                {
                    "content": "भारतीय किराया नियंत्रण अधिनियम के तहत, किरायेदारों को उचित नोटिस के बिना मनमाने ढंग से बेदखली के खिलाफ संरक्षण प्राप्त है। मकान मालिकों को किरायेदार को परिसर खाली करने के लिए कहने से पहले कम से कम 3 महीने का नोटिस देना होगा।",
                    "source": "rental_laws_hindi.txt",
                    "language": "hi"
                },
                {
                    "content": "एफआईआर (प्रथम सूचना रिपोर्ट) दर्ज करने के लिए, अपराध क्षेत्र के अधिकार क्षेत्र वाले निकटतम पुलिस स्टेशन पर जाएं। पुलिस आपरराधिक प्रक्रिया संहिता की धारा 154 के तहत आपकी शिकायत दर्ज करने के लिए बाध्य है।",
                    "source": "criminal_procedure_hindi.txt",
                    "language": "hi"
                },
                {
                    "content": "घरेलू हिंसा से महिलाओं का संरक्षण अधिनियम, 2005 के तहत, महिलाएं संरक्षण आदेश, निवास आदेश और मौद्रिक राहत मांग सकती हैं। कानून शारीरिक, यौन, मौखिक, भावनात्मक और आर्थिक दुर्व्यवहार को कवर करता है।",
                    "source": "domestic_violence_hindi.txt",
                    "language": "hi"
                }
            ]
        
        print(f"Loaded {len(self.documents)} documents")
        
        # Create embeddings for all documents
        embeddings = [self.embedding_model.encode(doc["content"]) for doc in self.documents]
        # Initialize FAISS index
        dimension = len(embeddings[0])  # Dimension of embeddings
        self.faiss_index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search
        self.faiss_index.add(np.array(embeddings))  # Add embeddings to FAISS index
        print("FAISS index created with document embeddings")

    
    def retrieve(self, query, language, top_k=3):
        """Retrieve relevant documents based on query"""
        # Encode the query
        query_embedding = self.embedding_model.encode(query)
        query_embedding = np.array([query_embedding])
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if self.documents[idx]["language"] == language:
                results.append({"content": self.documents[idx]["content"], "similarity": 1 - distance})
        return results

# Initialize knowledge base
kb = LegalKnowledgeBase()



