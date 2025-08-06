import google.generativeai as genai

genai.configure(api_key="AIzaSyDQq6L_7E0tPewhnbE9tL7QJy6rCMAGkRM")

model = genai.GenerativeModel("gemini-2.5-flash")


def masal_uret(konu):
    prompt = f"""
    Lütfen sadece çocuklara yönelik, eğitici ve yaratıcı bir hikaye yaz. Hikayenin konusu: {konu}.

    Hikayede başlık da olsun. Sadece hikaye içeriği ver, yorum ya da açıklama ekleme.

    Örnek gibi:

    Tavşan Pamuk ve Sincap Fındık(başlık)

    Yeşil bir ormanda, Tavşan Pamuk yaşarmış...
    
    Başlığı yazdıktan sonra bir satır aşağıya geç
    
    ve maksimum 1000 karakterli olsun
    
    Format şöyle olsun:

    **Başlık**

    (Bir satır boşluk bırak)

    Hikaye içeriği buraya gelsin...
    
    Hikayelerde Elif ismini kullanma
    
    Vızzz gibi ttsnin okuyamayacağı şeyler yazma

    """

    response = model.generate_content(prompt)
    return response.text.strip()
