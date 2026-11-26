const CACHE = "ddf-catalog-v2";
const URLS = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png", "./pages/p001.jpg", "./pages/p002.jpg", "./pages/p003.jpg", "./pages/p004.jpg", "./pages/p005.jpg", "./pages/p006.jpg", "./pages/p007.jpg", "./pages/p008.jpg", "./pages/p009.jpg", "./pages/p010.jpg", "./pages/p011.jpg", "./pages/p012.jpg", "./pages/p013.jpg", "./pages/p014.jpg", "./pages/p015.jpg", "./pages/p016.jpg", "./pages/p017.jpg", "./pages/p018.jpg", "./pages/p019.jpg", "./pages/p020.jpg", "./pages/p021.jpg", "./pages/p022.jpg", "./pages/p023.jpg", "./pages/p024.jpg", "./pages/p025.jpg", "./pages/p026.jpg", "./pages/p027.jpg", "./pages/p028.jpg", "./pages/p029.jpg", "./pages/p030.jpg", "./pages/p031.jpg", "./pages/p032.jpg", "./pages/p033.jpg", "./pages/p034.jpg", "./pages/p035.jpg", "./pages/p036.jpg", "./pages/p037.jpg", "./pages/p038.jpg", "./pages/p039.jpg", "./pages/p040.jpg", "./pages/p041.jpg", "./pages/p042.jpg", "./pages/p043.jpg", "./pages/p044.jpg", "./pages/p045.jpg", "./pages/p046.jpg", "./pages/p047.jpg", "./pages/p048.jpg", "./pages/p049.jpg", "./pages/p050.jpg", "./pages/p051.jpg", "./pages/p052.jpg", "./pages/p053.jpg", "./pages/p054.jpg", "./pages/p055.jpg", "./pages/p056.jpg", "./pages/p057.jpg", "./pages/p058.jpg", "./pages/p059.jpg", "./pages/p060.jpg", "./pages/p061.jpg", "./pages/p062.jpg", "./pages/p063.jpg", "./pages/p064.jpg", "./pages/p065.jpg", "./pages/p066.jpg", "./pages/p067.jpg", "./pages/p068.jpg", "./pages/p069.jpg", "./pages/p070.jpg", "./pages/p071.jpg", "./pages/p072.jpg", "./pages/p073.jpg", "./pages/p074.jpg", "./pages/p075.jpg", "./pages/p076.jpg", "./pages/p077.jpg", "./pages/p078.jpg", "./pages/p079.jpg", "./pages/p080.jpg", "./pages/p081.jpg", "./pages/p082.jpg", "./pages/p083.jpg", "./pages/p084.jpg", "./pages/p085.jpg", "./pages/p086.jpg", "./pages/p087.jpg", "./pages/p088.jpg", "./pages/p089.jpg", "./pages/p090.jpg", "./pages/p091.jpg", "./pages/p092.jpg", "./pages/p093.jpg", "./pages/p094.jpg", "./pages/p095.jpg", "./pages/p096.jpg", "./pages/p097.jpg", "./pages/p098.jpg", "./pages/p099.jpg", "./pages/p100.jpg", "./pages/p101.jpg", "./pages/p102.jpg", "./pages/p103.jpg"];
self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(URLS).catch(()=>{})));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
// 2026-11-26 실측 발견: 예전엔 모든 요청이 "한 번 캐시되면 그 뒤로 영원히 캐시만 사용"
// 방식이어서, CACHE 이름을 안 바꾸면 사용자가 아무리 새로고침해도 예전 버전만 계속
// 보였다(줌/이동 기능·카카오공유 버튼이 안 보인다는 신고로 발견). 이제 index.html·
// manifest.json·sw.js 자체는 "먼저 네트워크에서 최신본을 받아오고, 오프라인일 때만
// 캐시로 대체"하도록 바꿔서, 앞으로는 CACHE 이름을 깜빡 안 바꿔도 페이지 내용은
// 항상 최신으로 보인다(사진 등 나머지 정적 자원은 그대로 캐시 우선 유지 — 바뀔 일이
// 없어 오프라인 지원·속도에 유리).
const ALWAYS_FRESH = (req) =>
  req.mode === "navigate" || /\/(index\.html|manifest\.json|sw\.js)$/.test(new URL(req.url).pathname) || new URL(req.url).pathname.endsWith("/");

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  if (ALWAYS_FRESH(e.request)) {
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(()=>{});
        return res;
      }).catch(() => caches.match(e.request))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(()=>{});
      return res;
    }).catch(() => cached))
  );
});
