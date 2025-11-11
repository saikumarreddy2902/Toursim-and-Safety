"""
Google Translate API Integration for Tourist Safety System
Provides real-time translation of user content and details
"""

import requests
from functools import lru_cache
import os
from datetime import datetime
from typing import Optional, Dict, Any, TypedDict, List, cast


class BhashiniOutputItem(TypedDict, total=False):
    translatedText: str
    translation: str


class BhashiniResponse(TypedDict, total=False):
    translatedText: str
    translation: str
    outputText: str
    output: List[BhashiniOutputItem]

# LibreTranslate response structure (subset)
class LibreTranslateResponse(TypedDict, total=False):
    translatedText: str
    translation: str
    detectedLanguage: str
    alternatives: List[str]

class GoogleTranslateService:
    """Google Translate API service for real-time translation"""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        # Disable API requirement - use only mock translations for offline/demo mode
        self.api_key = None  # Disabled to avoid API errors
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        
        # Supported language mappings
        self.language_codes = {
            'en': 'en',
            'hi': 'hi',
            'ta': 'ta',
            'te': 'te',
            'bn': 'bn',
            'mr': 'mr',
            'gu': 'gu',
            'kn': 'kn',
            'ml': 'ml',
            'pa': 'pa',
            'or': 'or',
            'as': 'as'
        }
        
        # Enhanced translations dictionary for better accuracy
        self.enhanced_translations = {
            'app_name': {
                'en': 'Tourist Safety System',
                'hi': 'पर्यटक सुरक्षा प्रणाली',
                'ta': 'பர்യटक பாதुகாப்பு அமைப்பு',
                'te': 'పర్యాటక భద్రత వ్యవస్థ',
                'bn': 'পর্যটক নিরাপত্তা ব্যবস্থা',
                'mr': 'पर्यटक सुरक्षा प्रणाली',
                'gu': 'પર્યટક સુરક્ષા સિસ્ટમ',
                'kn': 'ಪರ್ಯಾಟಕ ಸುರಕ್ಷತಾ ವ್ಯವಸ್ಥೆ',
                'ml': 'ടൂറിസ്റ്റ് സേഫ്റ്റി സിസ്റ്റം',
                'pa': 'ਟੂਰਿਸਟ ਸੇਫਟੀ ਸਿਸਟਮ',
                'or': 'ପର୍ଯ୍ୟଟକ ସୁରକ୍ଷା ପ୍ରଣାଳୀ',
                'as': 'পৰ্যটক সুৰক্ষা ব্যৱস্থা'
            },
            'title': {
                'en': 'Complete Tourist Onboarding System',
                'hi': 'संपूर्ण पर्यटक ऑनबोर्डिंग सिस्टम',
                'ta': 'முழுமையான பர்यटक ஆன்போர்டிং் சிस்டம்',
                'te': 'పూర్తి పర్యాటక ఆన్‌బోర్డింగ్ సిస్టమ్',
                'bn': 'সম্পূর্ণ পর্যটক অনবোর্ডিং সিস্টেম',
                'mr': 'संपूर्ण पर्यटक ऑनबोर्डिंग सिस्टम',
                'gu': 'સંપૂર્ણ પર્યટક ઓનબોર્ડિંગ સિસ્ટમ',
                'kn': 'ಸಂಪೂರ್ಣ ಪರ್ಯಾಟಕ ಆನ್‌ಬೋರ್ಡಿಂಗ್ ಸಿಸ್ಟಂ',
                'ml': 'സമ്പൂർണ്ണ ടൂറിസ്റ്റ് ഓൺബോർഡിംഗ് സിസ്റ്റം',
                'pa': 'ਪੂਰਾ ਟੂਰਿਸਟ ਆਨਬੋਰਡਿੰਗ ਸਿਸਟਮ',
                'or': 'ସମ୍ପୂର୍ଣ୍ଣ ପର୍ଯ୍ୟଟକ ଅନ୍‌ବୋର୍ଡିଂ ସିଷ୍ଟମ୍',
                'as': 'সম্পূৰ্ণ পৰ্যটক অনবর্ডিং চিস্টেম'
            },
            'sos_emergency': {
                'en': 'SOS Emergency',
                'hi': 'SOS आपातकाल',
                'ta': 'SOS அவசரம்',
                'te': 'SOS అత్యవసరం',
                'bn': 'SOS জরুরি',
                'mr': 'SOS आपत्कालीन',
                'gu': 'SOS ઇમર્જન્સી',
                'kn': 'SOS ತುರ್ತು',
                'ml': 'SOS അടിയന്തിരാവസ്ഥ',
                'pa': 'SOS ਐਮਰਜੈਂਸੀ',
                'or': 'SOS ଜରୁରୀ',
                'as': 'SOS জৰুৰীকালীন'
            },
            'user_login': {
                'en': 'User Login',
                'hi': 'उपयोगकर्ता लॉगिन',
                'ta': 'பயனர் உள்நுழைவு',
                'te': 'వినియోగదారు లాగిన్',
                'bn': 'ব্যবহারকারী লগইন',
                'mr': 'वापरकर्ता लॉगिन',
                'gu': 'વપરાશકર્તા લોગિન',
                'kn': 'ಬಳಕೆದಾರ ಲಾಗಿನ್',
                'ml': 'ഉപയോക്താവിന്റെ ലോഗിൻ',
                'pa': 'ਯੂਜ਼ਰ ਲਾਗਇਨ',
                'or': 'ବ୍ୟବହାରକାରୀ ଲଗଇନ୍',
                'as': 'ব্যৱহাৰকাৰী লগইন'
            },
            'admin_login': {
                'en': 'Admin Login',
                'hi': 'एडमिन लॉगिन',
                'ta': 'நிர்வாக உள்நுழைवு',
                'te': 'అడ్మిన్ లాగిన్',
                'bn': 'অ্যাডমিন লগইন',
                'mr': 'अॅडमिन लॉगिन',
                'gu': 'એડમિન લોગિન',
                'kn': 'ಅಡ್ಮಿನ್ ಲಾಗಿನ್',
                'ml': 'അഡ്മിൻ ലോഗിൻ',
                'pa': 'ਐਡਮਿਨ ਲਾਗਇਨ',
                'or': 'ଆଡମିନ୍ ଲଗଇନ୍',
                'as': 'এডমিন লগইন'
            }
        }
        # Basic mock dictionary for common phrases and UI text to support demo mode
        # This prevents attribute errors and provides reasonable offline behavior
        self.mock_translations = {
            'en_to_hi': {
                'Tourist Login': 'पर्यटक लॉगिन',
                'Admin Login': 'एडमिन लॉगिन',
                'User Login': 'उपयोगकर्ता लॉगिन',
                'Enter your Tourist ID to access your safety dashboard': 'अपने सुरक्षा डैशबोर्ड तक पहुंचने के लिए अपना पर्यटक आईडी दर्ज करें',
                'Enter Username': 'उपयोगकर्ता नाम दर्ज करें',
                'Enter Password': 'पासवर्ड दर्ज करें',
                'Login': 'लॉगिन',
                'Police': 'पुलिस',
                'Ambulance': 'एम्बुलेंस',
                'Fire Service': 'अग्निशमन सेवा',
                'Tourist Helpline': 'पर्यटक हेल्पलाइन',
                'Get Started': 'शुरू करें',
                'Watch Demo': 'डेमो देखें',
                'Our Features': 'हमारी विशेषताएं',
                'Tourist Safety System': 'पर्यटक सुरक्षा प्रणाली',
                'Secure, blockchain-verified digital identity for modern tourism with comprehensive safety features': 'व्यापक सुरक्षा सुविधाओं के साथ आधुनिक पर्यटन के लिए सुरक्षित, ब्लॉकचेन-सत्यापित डिजिटल पहचान'
            },
            'en_to_te': {
                'Tourist Login': 'పర్యాటక లాగిన్',
                'Admin Login': 'అడ్మిన్ లాగిన్',
                'User Login': 'వినియోగదారు లాగిన్',
                'Enter your Tourist ID to access your safety dashboard': 'మీ భద్రతా డాష్‌బోర్డ్‌ను యాక్సెస్ చేయడానికి మీ టూరిస్ట్ IDని నమోదు చేయండి',
                'Enter Username': 'వాడుకరిపేరు నమోదు చేయండి',
                'Enter Password': 'పాస్‌వర్డ్ నమోదు చేయండి',
                'Login': 'లాగిన్',
                'Police': 'పోలీసులు',
                'Ambulance': 'ఆంబులెన్స్',
                'Fire Service': 'ఫైర్ సర్వీస్',
                'Tourist Helpline': 'టూరిస్ట్ హెల్ప్‌లైన్',
                'Get Started': 'ప్రారంభించండి',
                'Watch Demo': 'డెమో చూడండి',
                'Our Features': 'మా ఫీచర్లు',
                'Tourist Safety System': 'పర్యాటక భద్రత వ్యవస్థ',
                'Secure, blockchain-verified digital identity for modern tourism with comprehensive safety features': 'సమగ్ర భద్రత లక్షణాలతో ఆధునిక పర్యాటకం కోసం సురక్షిత, బ్లాక్‌చెయిన్-వెరిఫైడ్ డిజిటల్ గుర్తింపు'
            },
            'en_to_ta': {
                'Tourist Login': 'பர்யாटக உள்நுழைவு',
                'Admin Login': 'நிர்வாக உள்நुழைवு',
                'User Login': 'பயனர் உள்நుழைவு',
                'Get Started': 'தொடங்குங்கள்',
                'Watch Demo': 'டெமோ பார்க்கவும்',
                'Our Features': 'எங்கள் அம்சங்கள்',
                'Login': 'உள்நுழைவு'
            },
            'en_to_mr': {
                'Tourist Login': 'पर्यटक लॉगिन',
                'Admin Login': 'अॅडमिन लॉगिन', 
                'User Login': 'वापरकर्ता लॉगिन',
                'Get Started': 'सुरुवात करा',
                'Watch Demo': 'डेमो पहा',
                'Our Features': 'आमची वैशिष्ट्ये',
                'Login': 'लॉगिन'
            }
        }
    
    @lru_cache(maxsize=1000)
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """
        Translate text from source language to target language
        """
        if not text or not text.strip():
            return text
        
        # Check enhanced translations first
        if text in self.enhanced_translations:
            if target_lang in self.enhanced_translations[text]:
                return self.enhanced_translations[text][target_lang]
        
        source_code = self.language_codes.get(source_lang, source_lang)
        target_code = self.language_codes.get(target_lang, target_lang)
        
        # Try Bhashini (Indian languages) first if API key provided
        bhashini_key = os.environ.get('BHASHINI_API_KEY')
        if bhashini_key:
            try:
                translated = self._translate_via_bhashini(text, source_code, target_code, bhashini_key)
                if translated:
                    return translated
            except Exception as e:  # pragma: no cover - network failure path
                print(f"Bhashini API error: {e}")

        # Try LibreTranslate (self-hostable / public) next if available
        try:
            libre_translated = self._translate_via_libre(text, source_code, target_code)
            if libre_translated:
                return libre_translated
        except Exception as e:  # pragma: no cover
            print(f"LibreTranslate error: {e}")

        # Try Google Translate API if key is available and not demo (next fallback)
        if self.api_key and self.api_key != "DEMO_API_KEY" and not self.api_key.endswith('-demo'):
            try:
                params = {
                    'key': self.api_key,
                    'q': text,
                    'source': source_code,
                    'target': target_code,
                    'format': 'text'
                }
                
                response = requests.post(self.base_url, params=params, timeout=5)
                response.raise_for_status()
                
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                
                return translated_text
                
            except Exception as e:
                print(f"Google Translate API error: {e}")
                # Fall back to enhanced translations or mock
        
        # Fallback to mock translations for demo
        return self._mock_translate(text, source_lang, target_lang)

    def _translate_via_bhashini(self, text: str, source_code: str, target_code: str, api_key: str) -> Optional[str]:
        """Attempt translation using Bhashini APIs (typed parsing, silent fallback).

        Adjust base_url / payload as per the real Bhashini spec when available.
        """
        if source_code == target_code:
            return text

        base_url = os.environ.get('BHASHINI_BASE_URL', 'https://api.bhashini.gov.in/translate')
        payload: Dict[str, Any] = {
            'sourceLanguage': source_code,
            'targetLanguage': target_code,
            'text': text
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        try:
            resp = requests.post(base_url, json=payload, headers=headers, timeout=5)
            if resp.status_code != 200:
                return None
            raw_json: Any = resp.json()
            if not isinstance(raw_json, dict):  # Unexpected structure
                return None
            data = cast(BhashiniResponse, raw_json)

            # Direct keys first
            for key_candidate in ('translatedText', 'translation', 'outputText'):
                direct_val = data.get(key_candidate)  # type: ignore[arg-type]
                if isinstance(direct_val, str) and direct_val.strip():
                    return direct_val

            # Look into output list if present
            output_list = data.get('output')  # type: ignore[arg-type]
            if isinstance(output_list, list):
                for item in output_list:
                    for k in ('translatedText', 'translation'):
                        cand = item.get(k)  # type: ignore[arg-type]
                        if isinstance(cand, str) and cand.strip():
                            return cand
            return None
        except Exception:
            # Silent fallback: caller will use Google/mock path
            return None

    # -------------------- LibreTranslate Integration --------------------
    def _translate_via_libre(self, text: str, source_code: str, target_code: str) -> Optional[str]:
        """Translate using LibreTranslate if endpoint configured / reachable.

        Environment variables:
            LIBRE_TRANSLATE_URL  (default: https://libretranslate.com)
            LIBRE_TRANSLATE_API_KEY (optional)
        Notes:
            - Supports batching, but here we call per string; batch endpoint already exists separately.
            - Returns None on any failure so caller can fall back.
        """
        base_url = os.environ.get('LIBRE_TRANSLATE_URL', 'https://libretranslate.com').rstrip('/')
        api_key = os.environ.get('LIBRE_TRANSLATE_API_KEY', '')

        # Quick reject if obviously unsupported (Libre may not support Assamese yet)
        unsupported = {'as'}
        if target_code in unsupported:
            return None

        # Libre wants 'q', 'source', 'target'; 'source' can be 'auto'
        payload: Dict[str, Any] = {
            'q': text,
            'source': source_code if source_code != 'auto' else 'auto',
            'target': target_code,
            'format': 'text'
        }
        if api_key:
            payload['api_key'] = api_key

        try:
            resp = requests.post(f"{base_url}/translate", json=payload, timeout=5)
            if resp.status_code != 200:
                return None
            raw = resp.json()
            if not isinstance(raw, dict):
                return None
            data = cast(LibreTranslateResponse, raw)
            val: Optional[str] = None
            t_field = data.get('translatedText')
            if isinstance(t_field, str) and t_field.strip():
                val = t_field
            else:
                alt_field = data.get('translation')
                if isinstance(alt_field, str) and alt_field.strip():
                    val = alt_field
            if val:
                return val
        except Exception:
            return None
        return None
    
    def _mock_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation for demo purposes"""
        translation_key = f"{source_lang}_to_{target_lang}"
        reverse_key = f"{target_lang}_to_{source_lang}"
        
        # Check for direct translation
        if hasattr(self, 'mock_translations') and translation_key in self.mock_translations:
            mapped = self.mock_translations[translation_key].get(text)
            if mapped:
                return mapped
        
        # Check for reverse translation
        if hasattr(self, 'mock_translations') and reverse_key in self.mock_translations:
            for original, translated in self.mock_translations[reverse_key].items():
                if translated == text:
                    return original
        
        # For English to other languages, just return the text as-is for now
        # This prevents unwanted suffixes like "(తెలుగులో)" appearing on buttons
        if source_lang == 'en':
            return text
        
        return text
    
    def translate_form_data(self, form_data: Dict[str, Any], target_lang: str = 'en') -> Dict[str, Any]:
        """
        Translate entire form data to target language
        """
        translated_data: Dict[str, Any] = {}
        for key, value in form_data.items():
            if isinstance(value, str) and value.strip():
                translated_data[key] = self.translate_text(value, target_lang=target_lang)
            else:
                translated_data[key] = value
        return translated_data
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text
        """
        if not text or not text.strip():
            return 'en'
        
        # For demo, simple detection based on script
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            return 'hi'  # Devanagari script (Hindi)
        elif any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):
            return 'ta'  # Tamil script
        elif any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):
            return 'te'  # Telugu script
        
        return 'en'  # Default to English
    
    def get_translation_confidence(self, original_text: str, translated_text: str) -> float:
        """
        Get confidence score for translation (mock implementation)
        """
        if not original_text or not translated_text:
            return 0.0
        
        # Mock confidence based on length difference
        length_ratio = len(translated_text) / len(original_text)
        if 0.5 <= length_ratio <= 2.0:
            return 0.85
        else:
            return 0.65

class TranslationCache:
    """Cache for storing translations to reduce API calls"""
    
    def __init__(self) -> None:
        self.cache: Dict[str, Dict[str, str]] = {}
        self.max_size = 10000
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, str]]:
        """Get cached translation"""
        key = f"{source_lang}:{target_lang}:{hash(text)}"
        return self.cache.get(key)
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str) -> None:
        """Cache translation"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entries
            oldest_keys = list(self.cache.keys())[:100]
            for key in oldest_keys:
                del self.cache[key]
        
        key = f"{source_lang}:{target_lang}:{hash(text)}"
        self.cache[key] = {
            'translation': translation,
            'timestamp': datetime.now().isoformat()
        }

# Global instances
translate_service = GoogleTranslateService()
translation_cache = TranslationCache()

def translate_with_cache(text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
    """Translate text with caching"""
    cached = translation_cache.get(text, source_lang, target_lang)
    if cached:
        return cached['translation']
    
    translation = translate_service.translate_text(text, source_lang, target_lang)
    translation_cache.set(text, source_lang, target_lang, translation)
    
    return translation