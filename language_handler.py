import requests
import json
from langdetect import detect
from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize import indic_normalize
from indicnlp.transliterate import unicode_transliterate
import re

class LanguageProcessor:
    def __init__(self):
        self.normalizer = indic_normalize.IndicNormalizerFactory().get_normalizer("hi")
    
    def detect_language(self, text):
        """Detect whether text is in Hindi or English"""
        try:
            # Clean text to help with detection
            cleaned_text = re.sub(r'[0-9]', '', text)
            cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
            
            # For very short texts, check for Devanagari characters
            if len(cleaned_text) < 20:
                for char in cleaned_text:
                    # Check if character is in Devanagari Unicode range
                    if '\u0900' <= char <= '\u097F':
                        return 'hi'
                return 'en'
            
            # For longer texts, use langdetect
            lang = detect(cleaned_text)
            
            # Map to our supported languages
            if lang == 'hi':
                return 'hi'
            return 'en'  # Default to English for other languages
        except:
            return 'en'  # Default to English on error
    
    def preprocess_hindi(self, text):
        """Normalize and clean Hindi text"""
        # Normalize
        normalized_text = self.normalizer.normalize(text)
        
        # Remove excessive spaces
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        
        return normalized_text
    
    def translate_hindi_to_english(self, text):
        """
        Translate Hindi to English using LibreTranslate
        Falls back to dictionary method if translation fails
        """
        try:
            response = requests.post(
                "https://libretranslate.com/translate",
                data={
                    "q": text,
                    "source": "hi",
                    "target": "en",
                    "format": "text"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()["translatedText"]
            else:
                print(f"Translation API error: {response.status_code}")
                
        except Exception as e:
            print(f"Translation error: {e}")
        
        # Fallback to dictionary method
        return self._dictionary_translate_hindi_to_english(text)

def _dictionary_translate_hindi_to_english(self, text):
    """Original dictionary-based translation as fallback"""
    # Move your existing dictionary logic here
    hindi_to_english = {
        'कानून': 'law',
        'अदालत': 'court',
        'वकील': 'lawyer',
        'न्यायाधीश': 'judge',
        'अपराध': 'crime',
        'विवाह': 'marriage',
        'तलाक': 'divorce',
        'संपत्ति': 'property',
        'किरायेदार': 'tenant',
        'मकान मालिक': 'landlord',
        'करार': 'agreement',
        'एफआईआर': 'FIR',
        'पुलिस': 'police',
        'अधिकार': 'rights'
        # Add more legal terms as needed
    }
    
    # Replace known terms
    for hindi, english in hindi_to_english.items():
        text = text.replace(hindi, f"{hindi}({english})")
    
    return text

    
    def translate_english_to_hindi(self, text):
        """
        Translate English to Hindi using LibreTranslate
        Falls back to dictionary method if translation fails
        """
        try:
            response = requests.post(
                "https://libretranslate.com/translate",
                data={
                    "q": text,
                    "source": "en",
                    "target": "hi",
                    "format": "text"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()["translatedText"]
            else:
                print(f"Translation API error: {response.status_code}")
                
        except Exception as e:
            print(f"Translation error: {e}")
        
        # Fallback to dictionary method
        return self._dictionary_translate_english_to_hindi(text)

def _dictionary_translate_english_to_hindi(self, text):
    """Original dictionary-based translation as fallback"""
    # Move your existing dictionary logic here
    english_to_hindi = {
        'law': 'कानून',
        'court': 'अदालत',
        'lawyer': 'वकील',
        'judge': 'न्यायाधीश',
        'crime': 'अपराध',
        'marriage': 'विवाह',
        'divorce': 'तलाक',
        'property': 'संपत्ति',
        'tenant': 'किरायेदार',
        'landlord': 'मकान मालिक',
        'agreement': 'करार',
        'FIR': 'एफआईआर',
        'police': 'पुलिस',
        'rights': 'अधिकार'
    }
    
    # Replace known terms
    for english, hindi in english_to_hindi.items():
        pattern = r'\b' + english + r'\b'
        text = re.sub(pattern, f"{english}({hindi})", text, flags=re.IGNORECASE)
    
    return text

# Initialize language processor
lang_processor = LanguageProcessor()