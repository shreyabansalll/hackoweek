import config
from groq import Groq
import re

client = Groq(api_key=config.GROQ_API_KEY)

# Maps Whisper language codes → our internal names
LANG_MAP = {
    "hi": "hindi",
    "mr": "marathi",
    "en": "english",
    "marathi": "marathi",
    "hindi": "hindi",
    "english": "english",
}

def normalize_language(lang: str) -> str:
    return LANG_MAP.get(lang.lower(), "hindi")  # default to hindi

def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text for TTS compatibility."""
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    
    # Remove bullet points (dashes at start of line)
    text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)
    
    # Remove headers (# at start of line)
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    return text.strip()

def detect_marathi_from_transcript(transcript: str) -> bool:
    """Detect if transcript contains Marathi using specific word markers."""
    marathi_markers = ['माझ्या', 'आहे', 'करावे', 'वापरावे', 'आली', 'आले', 'काय', 'कसे', 'पिक', 'शेत', 'औषध']
    count = sum(1 for marker in marathi_markers if marker in transcript)
    return count >= 2

def get_system_prompt(language: str) -> str:
    if language == "marathi":
        return """
तुम्ही Shetkari Vaani आहात — विदर्भातील शेतकऱ्यांसाठी AI कृषी सहाय्यक.

तुम्हाला माहित आहे:
- विदर्भातील मुख्य पिके: कापूस, सोयाबीन, संत्रा, तूर, हरभरा
- सामान्य रोग: बोंड अळी, मर रोग, पानावरील ठिपके, करपा
- स्थानिक बाजार: यवतमाळ, अकोला, अमरावती, नागपूर APMC
- सरकारी योजना: PM-KISAN, नानाजी देशमुख कृषी संजीवनी, MSP

उत्तर देताना:
1. समस्या ओळखा
2. तात्काळ उपाय सांगा (शक्य असल्यास खर्च ₹ मध्ये)
3. प्रतिबंधक उपाय सांगा

नियम:
- फक्त शुद्ध मराठीत उत्तर द्या
- देवनागरी लिपी वापरा
- जास्तीत जास्त 4 वाक्ये
- फक्त शेतीविषयक माहिती द्या
- इंग्रजी किंवा हिंदी शब्द वापरू नका
"""
    elif language == "hindi":
        return """
आप Shetkari Vaani हैं — विदर्भ के किसानों के लिए AI कृषि सहायक।

आपको पता है:
- विदर्भ की मुख्य फसलें: कपास, सोयाबीन, संतरा, अरहर, चना
- सामान्य रोग: बोलवर्म, उकठा, पत्ती धब्बा, झुलसा
- स्थानिक बाजार: यवतमाल, अकोला, अमरावती, नागपुर APMC
- सरकारी योजनाएं: PM-KISAN, MSP, फसल बीमा योजना

उत्तर देते समय:
1. समस्या पहचानें
2. तुरंत उपाय बताएं (संभव हो तो खर्च ₹ में)
3. बचाव के उपाय बताएं

नियम:
- केवल शुद्ध हिंदी में उत्तर दें
- देवनागरी लिपि का उपयोग करें
- अधिकतम 4 वाक्य
- केवल कृषि संबंधित जानकारी दें
- अंग्रेजी या मराठी शब्द न मिलाएं
"""
    else:
        return """
You are Shetkari Vaani, an AI agriculture assistant for farmers in Vidarbha, Maharashtra.

You know:
- Main crops in Vidarbha: cotton, soybean, orange, tur dal, chickpea
- Common diseases: bollworm, wilt, leaf spot, blight
- Local markets: Yavatmal, Akola, Amravati, Nagpur APMC
- Government schemes: PM-KISAN, MSP, Crop Insurance

When answering:
1. Identify the problem
2. Give immediate remedy (with cost in ₹ if possible)
3. Give preventive measures

Rules:
- Reply only in simple English
- Maximum 4 sentences
- Focus only on agriculture topics
"""

def get_response(transcript: str, language: str = "hi") -> tuple:
    try:
        # Detect language: check for Marathi markers first
        is_marathi_detected = detect_marathi_from_transcript(transcript)
        if is_marathi_detected:
            detected_lang = "marathi"
            detection_method = "transcript_markers"
        else:
            detected_lang = normalize_language(language)
            detection_method = "whisper_tag"
        
        print(f"[LLM] Language detected: {detected_lang} (method: {detection_method})")
        
        system_prompt = get_system_prompt(detected_lang)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=0.3,
            max_tokens=120
        )

        reply = response.choices[0].message.content.strip()
        
        # Strip markdown formatting
        reply = strip_markdown(reply)
        
        # Replace newlines with pauses for natural TTS reading
        reply = reply.replace('\n', '. ')
        
        print(f"[LLM] Language: {detected_lang}")
        print(f"[LLM] Reply: {reply}")

        return reply, detected_lang

    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {e}")

        # ✅ CRITICAL FIX: always return a tuple, never a bare string
        fallback_messages = {
            "marathi": "माफ करा, सध्या उत्तर देता येत नाही. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा.",
            "hindi":   "माफ करें, अभी उत्तर देना संभव नहीं है। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
            "english": "Sorry, unable to respond right now. Please try again in a moment.",
        }
        lang = normalize_language(language)
        return fallback_messages.get(lang, fallback_messages["hindi"]), lang