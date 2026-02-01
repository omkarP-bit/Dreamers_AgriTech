"""
Multilingual Service - Integrates with multilingual_translator.py

Handles:
1. Language detection
2. Translation to English for processing
3. Translation of responses back to user's language
"""

import os
from langdetect import detect
from groq import Groq
import sys

# Get GROQ API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise Exception("❌ GROQ_API_KEY not found in environment")

client = Groq(api_key=GROQ_API_KEY)


class MultilingualService:
    """Service for multilingual translation and validation"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect the language of the input text"""
        try:
            lang = detect(text)
            print(f"  🌐 Detected language: {lang}")
            return lang
        except Exception as e:
            print(f"  ⚠️ Language detection failed: {e}. Defaulting to English.")
            return "en"
    
    @staticmethod
    def translate_with_model(text: str, src: str, tgt: str, model: str) -> str:
        """Translate text using a specific Groq model"""
        if src == tgt:
            return text
            
        prompt = f"""Translate from {src} to {tgt}.
Only provide the translated text, nothing else.

Text:
{text}"""
        
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a translator. Provide only the translated text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠️ {model} translation failed: {e}")
            return text
    
    @staticmethod
    def translate_dual(text: str, source: str, target: str) -> str:
        """Translate using multiple models and pick the best result"""
        if source == target:
            return text
        
        t1 = MultilingualService.translate_with_model(text, source, target, "openai/gpt-oss-20b")
        t2 = MultilingualService.translate_with_model(text, source, target, "moonshotai/kimi-k2-instruct-0905")
        
        sim = MultilingualService.simple_similarity(t1, t2)
        
        if sim >= 0.6:
            return t1
        return min([t1, t2], key=len)
    
    @staticmethod
    def simple_similarity(a: str, b: str) -> float:
        """Calculate simple word-level similarity between two strings"""
        a_set = set(a.lower().split())
        b_set = set(b.lower().split())
        
        if not a_set or not b_set:
            return 0
        
        intersection = len(a_set & b_set)
        union = len(a_set | b_set)
        return intersection / union if union > 0 else 0
    
    @staticmethod
    def back_translation_check(original: str, translated: str, source_lang: str) -> bool:
        """Verify translation quality using back-translation"""
        if source_lang == "en":
            return True
        
        back = MultilingualService.translate_dual(translated, "en", source_lang)
        similarity = MultilingualService.simple_similarity(original, back)
        
        print(f"  🔄 Back translation similarity: {similarity:.2f}")
        return similarity >= 0.45
    
    @staticmethod
    def translate_to_english(user_text: str, source_lang: str) -> tuple[str, bool]:
        """
        Translate user input to English if needed
        
        Returns:
            (english_text, is_valid) - English text and whether translation was valid
        """
        if source_lang == "en":
            print(f"  ✅ Input is already in English")
            return user_text, True
        
        english_text = MultilingualService.translate_dual(user_text, source_lang, "en")
        print(f"  📝 Translated to English: {english_text[:100]}...")
        
        # Verify translation quality
        is_valid = MultilingualService.back_translation_check(user_text, english_text, source_lang)
        
        if not is_valid:
            print(f"  ⚠️ Translation quality low - user may need to clarify")
        
        return english_text, is_valid
    
    @staticmethod
    def translate_from_english(response_en: str, target_lang: str) -> str:
        """Translate response from English to target language"""
        if target_lang == "en":
            return response_en
        
        print(f"  🔤 Translating response to {target_lang}...")
        translated = MultilingualService.translate_dual(response_en, "en", target_lang)
        return translated


# Singleton instance
_service = None

def get_multilingual_service() -> MultilingualService:
    """Get or create the multilingual service instance"""
    global _service
    if _service is None:
        _service = MultilingualService()
    return _service
