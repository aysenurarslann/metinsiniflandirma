import re
import sqlite3
import requests
from collections import Counter

# Türkçe durma kelimelerinin listesi
turkish_stopwords = [
    'acaba', 'ama', 'ancak', 'artık', 'asla', 'bana', 'bazen', 'bazı', 'bazıları',
    'belki', 'ben', 'beni', 'benim', 'beri', 'beş', 'bile', 'bir', 'birçok', 'biri',
    'birisi', 'birkaç', 'birşey', 'biz', 'bize', 'bizi', 'bizim', 'böyle', 'böylece',
    'bu', 'buna', 'bunda', 'bundan', 'bunlar', 'bunları', 'bunların', 'bunu', 'bunun',
    'burada', 'bütün', 'çoğu', 'çoğunu', 'çok', 'çünkü', 'da', 'daha', 'dahi', 'de',
    'defa', 'diğer', 'diye', 'doksan', 'dokuz', 'dolayı', 'dolayısıyla', 'dört', 'edecek',
    'eden', 'ederek', 'edilecek', 'ediliyor', 'edilmesi', 'ediyor', 'elbette', 'elli',
    'en', 'etmesi', 'etti', 'ettiği', 'ettiğini', 'gibi', 'göre', 'halen', 'hangi',
    'hatta', 'hem', 'henüz', 'hep', 'hepsi', 'her', 'herhangi', 'herkesin', 'hiç',
    'hiçbir', 'için', 'iki', 'ile', 'ilgili', 'ise', 'işte', 'itibaren', 'itibariyle',
    'kadar', 'karşın', 'kendi', 'kendilerine', 'kendini', 'kendisi', 'kendisine',
    'kendisini', 'kez', 'ki', 'kim', 'kime', 'kimi', 'kimin', 'kimisi', 'kimse',
    'kırk', 'madem', 'mi', 'mı', 'nasıl', 'ne', 'neden', 'nedenle', 'nerde',
    'nerede', 'nereye', 'niçin', 'nin', 'nın', 'niye', 'nun', 'nün', 'o', 'öbür',
    'olan', 'olarak', 'oldu', 'olduğu', 'olduğunu', 'olduklarını', 'olmadı', 'olmadığı',
    'olmak', 'olması', 'olmayan', 'olmaz', 'olsa', 'olsun', 'olup', 'olur', 'olursa',
    'oluyor', 'on', 'ona', 'ondan', 'onlar', 'onlardan', 'onları', 'onların', 'onu',
    'onun', 'otuz', 'öyle', 'pek', 'rağmen', 'sana', 'sanki', 'sanki', 'sanki', 'sekiz',
    'seksen', 'sen', 'senden', 'seni', 'senin', 'siz', 'sizden', 'sizi', 'sizin', 'şey',
    'şeyden', 'şeyi', 'şeyler', 'şöyle', 'şu', 'şuna', 'şunları', 'şunu', 'tarafından',
    'trilyon', 'tüm', 'üzere', 'var', 'vardı', 've', 'veya', 'ya', 'yani', 'yapacak',
    'yapılan', 'yapılması', 'yapıyor', 'yapmak', 'yaptı', 'yaptığı', 'yaptığını',
    'yaptıkları', 'ye', 'yedi', 'yerine', 'yetmiş', 'yi', 'yı', 'yine', 'yirmi', 'yoksa',
    'yu', 'yüz', 'zaten', 'altmış', 'altı', 'arasında', 'ayrıca', 'bilmem', 'biraz',
    'birbiri', 'birden', 'bilinen', 'biri', 'birileri', 'birisi', 'birkaç', 'birlikte',
    'bizim', 'bize', 'bizi', 'bizden', 'çünkü', 'daha', 'dahi', 'diğer', 'diye',
    'dolayı', 'fazla', 'gibi', 'hem', 'her', 'için', 'ile', 'ise', 'kadar', 'ki',
    'kendi', 'mi', 'mı', 'mu', 'mü', 'nasıl', 'ne', 'niçin', 'niye', 'öyle', 'şu',
    'sonra', 've', 'veya', 'ya', 'ya da', 'yani', 'yine'
]


# Metin sınıflandırıcı sınıfı
class MetinSiniflandirici:
    def __init__(self):
        self.metinler = []  # Metinlerin tutulduğu liste
        self.veritabani = "konusma.db"  # Veritabanı dosyası
        self.veritabani_olustur()  # Veritabanı oluşturma işlemi
        self.serpapi_api_anahtari = 'c8cae4af239ca9e291962587a1da8460de26c7908ffe843dbe2ab5a27dd95fb5'  # SerpAPI anahtarı

    def veritabani_olustur(self):
        # SQLite veritabanına bağlan ve tabloları oluştur (eğer yoksa)
        conn = sqlite3.connect(self.veritabani)
        cursor = conn.cursor()
        # Metinler tablosunu oluştur
        cursor.execute('''CREATE TABLE IF NOT EXISTS Metinler (
                          id INTEGER PRIMARY KEY,
                          metin TEXT,
                          ana_konu TEXT,
                          alt_konu TEXT)''')
        # Bilgi tablosunu oluştur
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bilgi (
                          id INTEGER PRIMARY KEY,
                          metin_id INTEGER,
                          bilgi TEXT,
                          FOREIGN KEY(metin_id) REFERENCES Metinler(id))''')
        conn.commit()  # Değişiklikleri kaydet
        conn.close()  # Bağlantıyı kapat

    def metin_girisi(self, kullanici_metni):
        # Kullanıcıdan metin al
        self.metinler.append(kullanici_metni)  # Metni listeye ekle
        # Metni sınıflandır ve ana ve alt konuları belirle
        ana_konu, alt_konu = self.metin_siniflandir(kullanici_metni)
        # Metni ve sınıflandırmaları veritabanına kaydet
        self.veritabanina_kaydet(kullanici_metni, ana_konu, alt_konu)
        print(f"\nAna konu: {ana_konu}\nAlt konu: {alt_konu}")
        # Genel konuyu değerlendir
        genel_konu = self.genel_konu_degerlendir()
        print(f"Genel konu: {genel_konu}")
        # İnternetten bilgi arama
        bilgi = self.bilgi_arama(genel_konu, ana_konu, alt_konu)
        # Bilgiyi veritabanına kaydet
        self.bilgi_kaydet(len(self.metinler), bilgi)
        print("İnternetten alınan bilgiler:\n", bilgi)

    def kelime_frekansi_hesapla(self, metin):
        # Metindeki kelimeleri ve frekanslarını hesapla
        kelimeler = re.findall(r'\w+', metin.lower())  # Metni kelimelerine ayır ve küçük harfe çevir
        kelime_freq = Counter(kelimeler)  # Kelime frekanslarını say
        # Durma kelimelerini frekanslardan çıkar
        for kelime in list(kelime_freq):
            if kelime in turkish_stopwords:
                del kelime_freq[kelime]
        return kelime_freq

    def metin_siniflandir(self, metin):
        # Metindeki kelime frekanslarını hesapla
        kelime_freq = self.kelime_frekansi_hesapla(metin)

        if not kelime_freq:
            return "bilinmiyor", "bilinmiyor"

        # İlk metin için ana ve alt konuları belirle
        if len(self.metinler) < 2:
            ana_konu = kelime_freq.most_common(1)[0][0]  # En sık geçen kelimeyi ana konu olarak belirle
            alt_konu = kelime_freq.most_common(2)[1][0] if len(
                kelime_freq) > 1 else ana_konu  # İkinci en sık geçen kelimeyi alt konu olarak belirle
        else:
            # Diğer metinler için ortak kelimeleri bul
            tum_kelimeler = Counter()
            for m in self.metinler:
                tum_kelimeler.update(self.kelime_frekansi_hesapla(m))

            ortak_kelimeler = kelime_freq & tum_kelimeler  # Ortak kelimeleri bul
            ana_konu = ortak_kelimeler.most_common(1)[0][0]  # En sık geçen ortak kelimeyi ana konu olarak belirle
            alt_konu = ortak_kelimeler.most_common(2)[1][0] if len(
                ortak_kelimeler) > 1 else ana_konu  # İkinci en sık geçen ortak kelimeyi alt konu olarak belirle

        return ana_konu, alt_konu

    def veritabanina_kaydet(self, metin, ana_konu, alt_konu):
        # Metni ve sınıflandırmaları veritabanına kaydet
        conn = sqlite3.connect(self.veritabani)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Metinler (metin, ana_konu, alt_konu) VALUES (?, ?, ?)",
                       (metin, ana_konu, alt_konu))
        conn.commit()  # Değişiklikleri kaydet
        conn.close()  # Bağlantıyı kapat

    def genel_konu_degerlendir(self):
        # Genel konuyu değerlendir
        tum_konular = [self.metin_siniflandir(metin)[0] for metin in
                       self.metinler]  # Tüm metinlerdeki ana konuları topla
        genel_konu = Counter(tum_konular).most_common(1)[0][0]  # En sık geçen ana konuyu genel konu olarak belirle
        return genel_konu

    def bilgi_arama(self, genel_konu, ana_konu, alt_konu):
        # İnternetten bilgi arama
        arama_sorgusu = f"{genel_konu} ve {ana_konu} ve {alt_konu}"  # Arama sorgusu oluştur
        print(f"Arama sorgusu: {arama_sorgusu}")

        params = {
            "q": arama_sorgusu,  # Arama sorgusu
            "api_key": self.serpapi_api_anahtari,  # SerpAPI anahtarı
            "engine": "google"  # Arama motoru
        }

        response = requests.get("https://serpapi.com/search", params=params)  # SerpAPI ile arama yap
        results = response.json()  # Sonuçları JSON formatında al

        bilgi = ""
        if "organic_results" in results:
            for result in results["organic_results"]:
                bilgi += f"{result['title']}: {result['snippet']}\n"  # Sonuçlardan başlık ve özet bilgileri al
        return bilgi

    def bilgi_kaydet(self, metin_id, bilgi):
        # Bilgiyi veritabanına kaydet
        conn = sqlite3.connect(self.veritabani)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Bilgi (metin_id, bilgi) VALUES (?, ?)",
                       (metin_id, bilgi))
        conn.commit()  # Değişiklikleri kaydet
        conn.close()  # Bağlantıyı kapat


if __name__ == "__main__":
    siniflandirici = MetinSiniflandirici()  # Metin sınıflandırıcı sınıfını başlat

    # Sürekli metin girişi almak için döngü
    while True:
        kullanici_metni = input("Türkçe metin giriniz (çıkmak için 'çık' yazınız): ")
        if kullanici_metni.lower() == 'çık':
            break
        siniflandirici.metin_girisi(kullanici_metni)  # Kullanıcıdan metin girişi al ve işleme başla
