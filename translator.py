from transformers import MarianMTModel, MarianTokenizer

# 加载模型（首次运行会下载）
print("Loading models...")

# 蒙古语 → 英语
mn_en_model_name = "Helsinki-NLP/opus-mt-mn-en"
mn_en_tokenizer = MarianTokenizer.from_pretrained(mn_en_model_name)
mn_en_model = MarianMTModel.from_pretrained(mn_en_model_name)

# 英语 → 中文
en_zh_model_name = "Helsinki-NLP/opus-mt-en-zh"
en_zh_tokenizer = MarianTokenizer.from_pretrained(en_zh_model_name)
en_zh_model = MarianMTModel.from_pretrained(en_zh_model_name)


def translate_mn_to_zh(text):
    try:
        # step1: mn → en
        inputs = mn_en_tokenizer(text, return_tensors="pt", padding=True)
        translated = mn_en_model.generate(**inputs)
        en_text = mn_en_tokenizer.decode(translated[0], skip_special_tokens=True)

        # step2: en → zh
        inputs = en_zh_tokenizer(en_text, return_tensors="pt", padding=True)
        translated = en_zh_model.generate(**inputs)
        zh_text = en_zh_tokenizer.decode(translated[0], skip_special_tokens=True)

        return zh_text

    except Exception as e:
        print("Translate error:", e)
        return text
