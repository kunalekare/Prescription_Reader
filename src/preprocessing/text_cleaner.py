import re

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\d+)\s*mg", r"\1mg", text)
    return text.strip()