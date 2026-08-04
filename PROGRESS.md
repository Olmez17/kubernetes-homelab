# Kubernetes Homelab — Progress

## Proje Amacı
Production-quality bir Kubernetes Homelab geliştirmek (FastAPI + PostgreSQL + K3s),
CV/mülakat için sergilenebilir seviyede. Öğrenme yöntemi: Socratic — kod/YAML kullanıcı
tarafından yazılıyor, mentor sadece review ve yönlendirici sorular soruyor.

## Roadmap (MVP)
1. Linux & Docker temelleri — ✅
2. FastAPI + PostgreSQL — local Docker Compose — ✅
3. K3s cluster kurulumu — ✅
4. PostgreSQL → Kubernetes (Secret, PVC, Deployment, Service) — ✅
5. FastAPI → Kubernetes (ConfigMap, probe'lar, Service) — ✅
6. Ingress — ✅
7. Resource requests/limits — ✅ **TAMAMLANDI**
8. GitHub Actions CI — ⬜ sıradaki adım
9. README + mimari diyagram + troubleshooting guide — ⬜

**Genel ilerleme: ~%75-80 (MVP)**

## Tamamlanan Görevler (bu oturum)
- **Local image → K3s import akışı** kuruldu: `docker save` → `k3s ctr images import`
  → `imagePullPolicy: Never` (registry'ye push olmadan local geliştirme için, CI'a
  bilinçli olarak ertelendi — "gerçekten ihtiyacımız var mı" prensibiyle)
- `k8s/fastapi-configmap.yaml` — `DB_HOST: postgres` (hassas olmayan config)
- `k8s/fastapi-deployment.yaml` — `envFrom` ile hem `postgres-secret` hem
  `fastapi-config` birleştirildi, `readinessProbe` (`/ready`, `port: 8003`)
  eklendi; `livenessProbe` bilinçli olarak atlandı (MVP'de process-hang riski yok)
- `k8s/fastapi-service.yaml` — ClusterIP, `selector: app: fastapi`
- `k8s/fastapi-ingress.yaml` — Traefik (K3s'e bundled gelen, ekstra kurulum
  gerekmedi), `host: fastapi.local`, `/etc/hosts` ile VM içinden test edildi
- Her iki Deployment'a (`postgres`, `fastapi`) **resource requests/limits** eklendi
  (`requests`/`limits` bilinçli olarak farklı tutuldu — burst'e izin ver ama tek
  node'da riski gözden kaçırma); `kubectl top pods` ile gerçek kullanım doğrulandı
  (limitlerin rahat üstünde kalındığı görüldü)

## Doğrulanan Senaryolar (gerçek testlerle kanıtlandı)
- **İsim uyuşmazlığı hatası ve çözümü:** İlk FastAPI deploy denemesinde
  `CrashLoopBackOff` — `database.py` `DB_USER`/`DB_PASSWORD`/`DB_NAME` okuyordu ama
  Secret key'leri `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` idi; `asyncpg`
  `user=None` durumunda OS kullanıcısını (`appuser`) varsayılana düşürüyordu.
  `database.py` güncellendi, build→save→import→`rollout restart` döngüsü uçtan
  uca yaşandı
- **Cluster içi DNS testi:** Geçici `busybox` pod'undan `wget http://fastapi:8003/ready`
  → `{"status":"ok"}` — Service DNS + FastAPI + PostgreSQL zinciri doğrulandı
- **Ingress uçtan uca testi:** `curl http://fastapi.local/ready` ve `/items` →
  Ingress → Traefik → Service → Pod zinciri çalışıyor
- **Rolling update gözlemi:** Resource limits eklenince Deployment'lar `configured`
  oldu, yeni pod ayağa kalkıp sağlıklı olduktan sonra eski pod otomatik silindi
  (kesintisiz geçiş, kısa süreliğine `/items` boş dönmesi geçici rollout anıydı)

## Öğrenilen Kavramlar
- Docker'ın image store'u ile K3s'in `containerd`'i birbirinden habersiz, ayrı
  depolama alanları — local image'ı K8s'e taşımak için explicit bir adım gerekir
- `imagePullPolicy: Always` (latest tag'in varsayılanı) local-only image'larla
  çakışır → `Never` ile registry'ye hiç gitmeme garantisi
- Secret/ConfigMap `envFrom` ile birleştirilebilir (liste halinde birden fazla kaynak)
- Env variable isimleri Secret/ConfigMap key isimleriyle **birebir** eşleşmeli
  (aksi halde `None` değeri sessizce yanlış bir davranışa yol açabilir — bu örnekte
  OS kullanıcı adına fallback)
- Ingress = kural tanımı, Ingress Controller (Traefik) = kuralı uygulayan bileşen
  (Deployment/ReplicaSet ayrımına benzer bir "tanım vs. icra" deseni)
- Resource `requests` = scheduling için minimum garanti, `limits` = üst sınır
  (memory limit aşımı → OOMKilled, CPU limit aşımı → throttle, kill değil)
- `kubectl rollout restart` ile `kubectl apply` farkı: image içeriği değişse bile
  manifest'teki `image:` alanı aynıysa `apply` pod'u yeniden başlatmayabilir
- `kubectl top pods` ile gerçek kaynak kullanımını `requests`/`limits` kararlarına
  karşı doğrulamak — production'da resource tuning'in temel aracı

## Yapılan Hatalar ve Nedenleri
- Deployment'larda `resources` bloğunun `limits` kısmı `requests` ile aynı seviyede
  değil, `resources`'ın dışına yazılmıştı — girinti düzeltildi
- İlk `kubectl run -it --rm` denemeleri image çekme gecikmesinden timeout'a düştü,
  `--command -- sleep N` + ayrı `kubectl exec` yaklaşımına geçildi

## Açık Kalan Problemler / Technical Debt
- Image K3s'e **manuel olarak** import ediliyor (`docker save` + `k3s ctr images
  import`), her kod değişikliğinde tekrar gerekiyor — 8. adımda CI ile
  otomatikleştirilecek (registry'ye push, image tag stratejisi de o zaman netleşecek)
- `livenessProbe` MVP'de yok — bilinçli sınırlama, process-hang riski taşıyan bir
  karmaşıklık olursa eklenmeli

## Bir Sonraki Oturumun Hedefleri
- GitHub Actions CI: image build + push workflow'u tasarla
- Hangi registry kullanılacağına karar ver (Docker Hub / GitHub Container Registry —
  GHCR, private repo ile birlikte geldiği için muhtemelen daha pratik)
- Image tag stratejisi (sadece `latest` mi, yoksa commit SHA / semantic version mı —
  `latest` + `imagePullPolicy: Never` yaklaşımının CI ile birlikte nasıl değişmesi
  gerektiğini düşün)
- CI tetikleyicisi: her push'ta mı, sadece belirli branch'lerde mi çalışsın

## Önerilen Kaynaklar
- GitHub Actions Docs — Docker build-push-action
- GHCR (GitHub Container Registry) kimlik doğrulama dokümantasyonu
