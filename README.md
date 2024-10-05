### Amacı:

Bu kod, kullanıcının girdiği Türkçe metinleri analiz ederek ana konu ve alt konuları belirler ve bu bilgileri kullanarak internetten ilgili bilgiler arar. Ayrıca, metinleri ve arama sonuçlarını SQLite veritabanına kaydeder.

**Yapılanlar:**

# Veritabanı Oluşturma:
* SQLite veritabanı kullanılarak Metinler ve Bilgi tabloları oluşturulur.
* Metinler tablosunda kullanıcı tarafından girilen metinler ve bu metinlerin ana ve alt konuları saklanır.
* Bilgi tablosunda, metinlerle ilişkili internetten alınan bilgiler saklanır.

# Metin Girişi ve Sınıflandırma:
* Kullanıcı, program çalışırken metin girer.
* Girilen metin, ana konu ve alt konu belirlemek için analiz edilir. Bu işlem, metindeki kelimelerin frekansını hesaplayarak gerçekleştirilir.
* İlk metin için en sık geçen kelimeler ana ve alt konu olarak belirlenir. Daha sonraki metinler için ortak kelimeler dikkate alınarak ana ve alt konular belirlenir.

# Genel Konu Belirleme:
* Program, girilen tüm metinlerin ana konularını değerlendirerek en sık geçen ana konuyu genel konu olarak belirler.

# İnternetten Bilgi Arama:
* Genel konu, ana konu ve alt konu birleştirilerek bir arama sorgusu oluşturulur.
* SerpAPI kullanılarak bu arama sorgusu ile internette bilgi araması yapılır.
* Arama sonuçlarından elde edilen başlıklar ve özetler derlenir.

# Veritabanına Kaydetme:
* Girilen metin, ana konu ve alt konu Metinler tablosuna kaydedilir.
* İnternetten alınan bilgiler Bilgi tablosuna kaydedilir.

Bu şekilde, program kullanıcıdan aldığı metinleri analiz eder, internetten ilgili bilgileri toplar ve bu bilgileri veritabanında saklar. Bu, belirli bir konu hakkında bilgi toplamak ve organize etmek için etkili bir yöntem sağlar.
