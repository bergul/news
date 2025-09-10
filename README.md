# Economy & Commodities News Ingestor

Python uygulaması: ekonomi/emtia odaklı haberleri belirlediğiniz kaynaklardan düzenli aralıklarla kontrol eder,
en güncel haberleri parse eder ve web projenizin veritabanına (ör. PostgreSQL) kaydeder.

## Özellikler
- **Kaynak yapılandırması**: `config/sources.yml` (RSS/Atom veya JSON API).
- **Zamanlama**: APScheduler (varsayılan: 15 dakikada bir).
- **Veritabanı**: SQLAlchemy + Alembic'siz basit model (PostgreSQL/MySQL/SQLite).
- **Tekrarlanan haberleri engelleme**: URL hash + başlık+zaman damgası eşsizliği.
- **Basit konu/etiket çıkarımı**: emtia anahtar kelimeleri ile otomatik etiketleme.
- **Sağlıklı kapanış ve loglama**: rota bazlı (stdout) logging.
- **Docker & docker-compose**: Postgres ile tek komutla ayağa kalkar.

## Hızlı Başlangıç
1) .env dosyasını doldurun (aşağıdaki örneğe bakın).
2) `config/sources.yml` içinde takip etmek istediğiniz RSS/APı adreslerini girin.
3) Docker ile:
```bash
docker compose up --build
```
veya Python ile:
```bash
pip install -r requirements.txt
python -m app.main --once   # tek sefer çalıştır
python -m app.main          # scheduler ile sürekli çalışır
```

## .env Örneği
```
DATABASE_URL=postgresql+psycopg2://news_user:news_pass@db:5432/newsdb
SCHEDULE_CRON=*/15 * * * *   # her 15 dakikada bir
TZ=Europe/Istanbul
```

## `config/sources.yml` Örneği
```yaml
# RSS örnekleri (kendi kaynaklarınızı ekleyin)
- name: Reuters Commodities
  type: rss
  url: https://www.reuters.com/markets/commodities/rss
  language: en
  enabled: true

- name: BloombergHT Ekonomi
  type: rss
  url: https://www.bloomberght.com/rss/ekonomi.xml
  language: tr
  enabled: true

- name: Dünya Gazetesi Emtia
  type: rss
  url: https://www.dunya.com/rss/ekonomi
  language: tr
  enabled: true
```

> Not: RSS/Atom beslemeleri telif ve robots.txt kurallarına uygun olduğu için önerilir.
> JSON API kullanan kaynaklar için `type: json` ile özelleştirme ekleyebilirsiniz.

## Tablo Şeması (news)
- id (PK)
- source_name
- title
- url (unique-ish)
- published_at (UTC)
- summary
- content (opsiyonel – RSS özetinden)
- language
- tags (virgülle ayrılmış)
- fetched_at (UTC)
- raw (JSON – kaynak verisi)

## Web projesine entegrasyon
- Bu uygulama ayrı bir ingest servisidir. Web projeniz aynı PostgreSQL veritabanına bağlanabilir.
- Alternatif: Bu servis REST webhook’larına POST atacak şekilde genişletilebilir.

## Lisans
MIT
