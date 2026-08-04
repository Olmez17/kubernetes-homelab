# Kubernetes Homelab — Progress

## Proje Amacı
Production-quality bir Kubernetes Homelab geliştirmek (FastAPI + PostgreSQL + K3s),
CV/mülakat için sergilenebilir seviyede. Öğrenme yöntemi: Socratic — kod/YAML kullanıcı
tarafından yazılıyor, mentor sadece review ve yönlendirici sorular soruyor.

## Roadmap (MVP) — TAMAMLANDI
1. Linux & Docker temelleri — ✅
2. FastAPI + PostgreSQL — local Docker Compose — ✅
3. K3s cluster kurulumu — ✅
4. PostgreSQL → Kubernetes (Secret, PVC, Deployment, Service) — ✅
5. FastAPI → Kubernetes (ConfigMap, probe'lar, Service) — ✅
6. Ingress — ✅
7. Resource requests/limits — ✅
8. GitHub Actions CI — ✅ **TAMAMLANDI**
9. README + mimari diyagram + troubleshooting guide — ✅ **TAMAMLANDI**

**MVP %100 tamamlandı.**

## Tamamlanan Görevler (bu oturum)
- **GitHub Actions CI kuruldu** (`.github/workflows/docker-build.yml`):
  `main` branch'e push tetikleyici, `actions/checkout`, `docker/login-action`
  (GHCR, `secrets.GITHUB_TOKEN` ile — ekstra token yönetimi gerekmedi),
  `docker/build-push-action` ile build+push
- **Repo GitHub'a taşındı**: `git init`, `.gitignore` genişletildi (`__pycache__/`,
  `*.tar` eklendi), yanlışlıkla oluşmuş boş `app/Dockerfile` ve `app/crud.py`
  temizlendi, ilk commit + push (`Olmez17/kubernetes-homelab`, public repo)
- **GHCR entegrasyonu**: image `ghcr.io/olmez17/kubernetes-homelab-web:latest`
  olarak push edildi, paket otomatik public geldi (repo public olduğu için)
- **Deployment'lar CI'a bağlandı**: `fastapi-deployment.yaml`'da `image` GHCR
  yoluna, `imagePullPolicy` `Never`'dan `Always`'e çevrildi — local
  `docker save`/`k3s ctr import` adımına artık gerek kalmadı
- **README.md yazıldı**: amaç/felsefe paragrafı, mermaid mimari diyagramı,
  teknoloji tablosu (gerekçeli), proje yapısı, kurulum (Compose + K8s),
  API endpoint tablosu, mimari kararlar (StatefulSet/Deployment, ORM/ham SQL,
  async/sync, local-import/CI, livenessProbe kararı — hepsi gerekçeli),
  troubleshooting (4 gerçek senaryo, bu proje sırasında yaşanmış hatalardan),
  CI/CD akış özeti, PROGRESS.md'ye link

## Doğrulanan Senaryolar (gerçek testlerle kanıtlandı)
- **GHCR tag hatası ve çözümü:** İlk CI run'ı `repository name must be lowercase`
  hatasıyla başarısız oldu (`github.repository_owner` büyük harf içeriyordu) —
  tag elle küçük harfle (`ghcr.io/olmez17/...`) sabitlendi
- **Workflow izin hatası ve çözümü:** İkinci run `denied: installation not
  allowed to Create organization package` hatası verdi — repo Settings →
  Actions → "Read and write permissions" ile çözüldü (GitHub'ın varsayılan
  least-privilege davranışı)
- **Uçtan uca CI/CD doğrulaması:** `kubectl describe pod` çıktısında
  `Successfully pulled image "ghcr.io/olmez17/..."` görüldü — image gerçekten
  registry'den çekildi (local cache değil); rolling update ile eski pod
  düzgünce sonlandı; `/ready` ve `/items` yeni pod üzerinden doğru sonuç verdi

## Öğrenilen Kavramlar
- Docker registry image isimleri tamamen küçük harf olmalı (GitHub kullanıcı
  adları büyük harf içerebildiği için `github.repository_owner` gibi otomatik
  değişkenler bu kuralı ihlal edebilir)
- GitHub Actions'ın `GITHUB_TOKEN`'ı varsayılan olarak salt-okunur — yazma
  izni (paket oluşturma dahil) repo ayarlarından açıkça verilmeli
  (least-privilege / güvenli varsayılan prensibi)
- `imagePullPolicy: Never` (local-only) → `Always` (registry-backed) geçişi,
  CI/CD'nin manuel adımları nasıl ortadan kaldırdığının somut örneği
- Markdown içinde mermaid gibi kod-bloğu-içeren-içerik eklerken, dış/iç
  backtick çakışmasından kaçınmak için ayrı dosyaya yazıp `sed` ile birleştirme
  ya da 4-boşluklu girinti (backtick'siz kod bloğu) syntax'ı kullanılabilir

## Yapılan Hatalar ve Nedenleri
- İlk README taslağı büyük bir tek `cat << EOF` bloğu içinde mermaid diyagramı
  içerdiği için iç içe backtick çakışması yaşandı, çıktı bozuldu — bölüm bölüm
  ekleme + girintili kod bloğu yaklaşımına geçildi
- GHCR tag'inde büyük/küçük harf hatası, workflow izin hatası — ikisi de ilk
  CI çalıştırmasında ortaya çıktı, sırayla teşhis edilip düzeltildi

## Açık Kalan Problemler / Technical Debt (bilinçli, MVP kapsamı dışı)
- `PUT /items/{item_id}` (update) yok — CRUD'un temel amacı için gerekli değildi
- `livenessProbe` yok — MVP'de process-hang riski taşıyan karmaşıklık olmadığı
  için bilinçli olarak eklenmedi (README'de gerekçesi belgelendi)
- Image tag stratejisi sadece `latest` — commit SHA / semantic versioning yok,
  MVP için yeterli görüldü

## Stretch Goals (MVP sonrası, opsiyonel)
Helm, Prometheus, Grafana, Loki, Alertmanager, ArgoCD/GitOps, HPA, Network
Policies, gelişmiş RBAC, disaster recovery, multi-node cluster — hiçbiri
zorunlu değil, ileride CV'yi güçlendirmek istenirse değerlendirilebilir.

## Önerilen Kaynaklar
- Kubernetes Docs — Production Best Practices bölümü (stretch goal'lara
  geçmeden önce genel bir tazeleme için)
- ArgoCD / GitOps dokümantasyonu (stretch goal olarak değerlendirilirse)
