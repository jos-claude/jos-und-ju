// Vorschau-Renderer fuer den Weltgenerator (three.js). Bildet Roblox moeglichst treu nach:
// - Terrain-Material je Voxel nach der Regel des WorldBuilders (Deckschicht / Unterboden / Grundgestein / Schichtbaender)
// - Zusatzformen (terrain_ops) inkl. Luft-Ausschnitten (Fenster, Tunnel, Bogen)
// - Deko aus Vorlagen (Block, Ball, Cylinder = Achse X, Ellipsoid, Wedge), Neon + Bloom, Transparenz
// - Licht nach meta.lighting, Atmosphaere als Luftperspektive, Farbkorrektur
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const DATA = '/out/preview/';
const hud = document.getElementById('hud');
const Q = new URLSearchParams(location.search);
const WIDTH = +(Q.get('w') || innerWidth);
const HEIGHT = +(Q.get('h') || innerHeight);
const NEON_GAIN = 2.4;

const deg = (d) => d * Math.PI / 180;
const lin = (c) => new THREE.Color().setRGB(c[0] / 255, c[1] / 255, c[2] / 255, THREE.SRGBColorSpace);
const v3 = (c) => `vec3(${c.r.toFixed(5)}, ${c.g.toFixed(5)}, ${c.b.toFixed(5)})`;

async function main() {
  const scn = await (await fetch(DATA + 'scene.json')).json();
  const bin = await (await fetch(DATA + 'terrain.bin')).arrayBuffer();
  const meta = scn.meta;
  const L = meta.lighting || {};
  const LL = L.Lighting || {};
  const AT = L.Atmosphere || {};
  const N = scn.grid.n, CELL = scn.grid.cell, ORIGIN = scn.grid.origin;

  // ---------------------------------------------------------------- Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(WIDTH, HEIGHT);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = Math.pow(2, (LL.ExposureCompensation || 0)) * 1.05;
  document.body.appendChild(renderer.domElement);

  // ---------------------------------------------------------------- Sonne, Atmosphaere
  const sunAz = deg(meta.sun?.azimuth ?? 250), sunEl = deg(meta.sun?.elevation ?? 22);
  const SUN = new THREE.Vector3(Math.sin(sunAz) * Math.cos(sunEl), Math.sin(sunEl), -Math.cos(sunAz) * Math.cos(sunEl));
  const atmoColor = lin(AT.Color || [242, 184, 160]);
  const atmoDecay = lin(AT.Decay || [142, 111, 168]);
  const density = AT.Density ?? 0.28;
  // Zielkurve der Vorgabe: 15 % bei 500, 55 % bei 1500, 70 % bei 2000 Studs (fuer Density 0.28)
  const fogL = 1754 * Math.pow(0.28 / Math.max(density, 0.01), 0.7);
  const ATMO = `
    const vec3 SUN_DIR = ${'vec3(' + SUN.x.toFixed(5) + ',' + SUN.y.toFixed(5) + ',' + SUN.z.toFixed(5) + ')'};
    const vec3 ATMO_COL = ${v3(atmoColor)};
    const vec3 ATMO_DECAY = ${v3(atmoDecay)};
    vec3 atmoColorDir(vec3 dir) {
      vec2 dh = normalize(dir.xz + vec2(1e-5));
      float s = dot(dh, normalize(SUN_DIR.xz)) * 0.5 + 0.5;
      vec3 c = mix(ATMO_DECAY, ATMO_COL, smoothstep(0.05, 0.95, s));
      float g = pow(max(dot(dir, SUN_DIR), 0.0), 12.0);
      c += vec3(1.0, 0.8, 0.6) * g * ${(AT.Glare ?? 0.35).toFixed(3)} * 1.4;
      return c * 1.18;
    }
    vec3 applyAtmo(vec3 col, vec3 wp) {
      vec3 v = wp - cameraPosition;
      float d = length(v);
      vec3 dir = v / max(d, 1e-3);
      float f = 1.0 - exp(-pow(d / ${fogL.toFixed(1)}, 1.448));
      f = 1.0 - pow(1.0 - f, 1.0 + 0.22 * ${(AT.Haze ?? 1.6).toFixed(2)});
      f *= mix(1.0, 0.45, smoothstep(0.0, 0.6, dir.y));
      return mix(col, atmoColorDir(dir), clamp(f, 0.0, 0.94));
    }`;
  THREE.ShaderChunk.fog_pars_vertex = '#ifdef USE_FOG\n varying vec3 vFogWorld;\n#endif\n';
  THREE.ShaderChunk.fog_vertex = `#ifdef USE_FOG
    { vec4 fw = vec4(transformed, 1.0);
      #ifdef USE_INSTANCING
        fw = instanceMatrix * fw;
      #endif
      fw = modelMatrix * fw; vFogWorld = fw.xyz; }
  #endif\n`;
  THREE.ShaderChunk.fog_pars_fragment = '#ifdef USE_FOG\n varying vec3 vFogWorld;\n' + ATMO + '\n#endif\n';
  THREE.ShaderChunk.fog_fragment = '#ifdef USE_FOG\n gl_FragColor.rgb = applyAtmo(gl_FragColor.rgb, vFogWorld);\n#endif\n';

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xffffff, 1, 2);   // nur damit USE_FOG gesetzt ist

  // Licht: Sonne (ColorShift_Top), Umgebung (Ambient + OutdoorAmbient), Himmel/Boden (EnvironmentDiffuse, ColorShift_Bottom)
  const bright = LL.Brightness ?? 2.4;
  const sunCol = lin(LL.ColorShift_Top || [255, 217, 168]).lerp(new THREE.Color(1, 1, 1), 0.45);
  const sun = new THREE.DirectionalLight(sunCol, bright * 1.4);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 1.2;
  sun.shadow.radius = 2.0;
  scene.add(sun, sun.target);
  const amb = lin(LL.Ambient || [106, 88, 120]).add(lin(LL.OutdoorAmbient || [178, 140, 138]));
  scene.add(new THREE.AmbientLight(amb, 1.05));
  const hemi = new THREE.HemisphereLight(lin([120, 170, 190]), lin(LL.ColorShift_Bottom || [122, 111, 176]), 0.9 * (LL.EnvironmentDiffuseScale ?? 0.6) / 0.6);
  scene.add(hemi);

  // ---------------------------------------------------------------- Terrain-Daten
  const NN = N * N;
  const Hs = new Float32Array(bin, 0, NN);
  const M = new Uint8Array(bin, NN * 4, NN);
  const Wt = new Uint8Array(bin, NN * 5, NN);
  const S = new Uint8Array(bin, NN * 6, NN);
  const D = new Uint8Array(bin, NN * 7, NN);
  const VOID = -10000;
  const hTex = new Float32Array(NN);
  for (let i = 0; i < NN; i++) hTex[i] = Number.isNaN(Hs[i]) ? VOID : Hs[i];
  const info = new Uint8Array(NN * 4);
  for (let i = 0; i < NN; i++) { info[i * 4] = M[i]; info[i * 4 + 1] = Wt[i]; info[i * 4 + 2] = S[i]; info[i * 4 + 3] = D[i]; }
  const mkTex = (data, w, h, fmt, type) => {
    const t = new THREE.DataTexture(data, w, h, fmt, type);
    t.minFilter = t.magFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true; return t;
  };
  const texH = mkTex(hTex, N, N, THREE.RedFormat, THREE.FloatType);
  const texInfo = mkTex(info, N, N, THREE.RGBAFormat, THREE.UnsignedByteType);
  // Schichtbaender
  const mats = scn.materials;
  const midx = Object.fromEntries(mats.map((m, i) => [m, i]));
  const bands = new Uint8Array(256);
  let period = 0;
  for (const [m, t] of meta.strata.bands) for (let k = 0; k < t; k++) bands[period++] = midx[m];
  const texBand = mkTex(bands, 256, 1, THREE.RedFormat, THREE.UnsignedByteType);
  const lvls = new Float32Array(256);
  scn.waterLevels.forEach((v, i) => { lvls[i + 1] = v; });
  // Materialfarben
  const DEFAULT_COL = { Pavement: [148, 148, 140], Asphalt: [80, 80, 82], Cobblestone: [140, 130, 120], Brick: [160, 90, 70], WoodPlanks: [160, 120, 80], Concrete: [169, 229, 210] };
  const matCol = mats.map((m) => lin(meta.materialColors[m] || DEFAULT_COL[m] || [255, 0, 255]));
  const layers = meta.layers;
  const subsoil = mats.map((m) => midx[layers.subsoil[m] || layers.bedrock] ?? 0);
  // Punktlichter (aus Deko) -> Lichtflecken auf dem Terrain
  const lightList = [];
  // Luft-Formen
  const airOps = scn.terrainOps.filter((o) => o.material === 'Air');
  const airData = new Float32Array(Math.max(1, airOps.length) * 16);
  airOps.forEach((o, i) => {
    let c, R = [1, 0, 0, 0, 1, 0, 0, 0, 1], p = [0, 0, 0], type;
    if (o.op === 'Ball') { c = o.c; type = 0; p = [o.r, 0, 0]; }
    else { c = o.cf.slice(0, 3); R = o.cf.slice(3); if (o.op === 'Block') { type = 1; p = [o.size[0] / 2, o.size[1] / 2, o.size[2] / 2]; } else { type = 2; p = [o.r, o.height / 2, 0]; } }
    const b = i * 16;
    airData.set([c[0], c[1], c[2], type], b);
    airData.set([R[0], R[3], R[6], p[0]], b + 4);    // Spalte 0 von R
    airData.set([R[1], R[4], R[7], p[1]], b + 8);    // Spalte 1
    airData.set([R[2], R[5], R[8], p[2]], b + 12);   // Spalte 2
  });
  const texAir = mkTex(airData, 4, Math.max(1, airOps.length), THREE.RGBAFormat, THREE.FloatType);

  const lightTexData = new Float32Array(128 * 2 * 4);
  const texLights = mkTex(lightTexData, 128, 2, THREE.RGBAFormat, THREE.FloatType);

  const TU = {
    tH: { value: texH }, tInfo: { value: texInfo }, tBand: { value: texBand }, tAir: { value: texAir }, tLights: { value: texLights },
    nAir: { value: airOps.length }, nLights: { value: 0 },
    matCol: { value: matCol.map((c) => new THREE.Vector3(c.r, c.g, c.b)) },
    subsoil: { value: subsoil }, bedrock: { value: midx[layers.bedrock] },
    topDepth: { value: layers.topDepth }, subDepth: { value: layers.subDepth },
    strataBase: { value: meta.strata.base }, period: { value: period },
  };
  const COMMON = `
    uniform sampler2D tH; uniform sampler2D tInfo; uniform sampler2D tBand; uniform sampler2D tAir; uniform sampler2D tLights;
    uniform int nAir; uniform int nLights;
    uniform vec3 matCol[${mats.length}]; uniform int subsoil[${mats.length}]; uniform int bedrock;
    uniform float topDepth; uniform float subDepth; uniform float strataBase; uniform float period;
    varying vec3 vWPos; varying vec3 vWNrm;
    float hash3(vec3 p) { p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3)); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
    float vnoise(vec3 x) {
      vec3 i = floor(x); vec3 f = fract(x); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(mix(hash3(i), hash3(i + vec3(1,0,0)), f.x), mix(hash3(i + vec3(0,1,0)), hash3(i + vec3(1,1,0)), f.x), f.y),
                 mix(mix(hash3(i + vec3(0,0,1)), hash3(i + vec3(1,0,1)), f.x), mix(hash3(i + vec3(0,1,1)), hash3(i + vec3(1,1,1)), f.x), f.y), f.z);
    }
    ivec2 colAt(vec2 xz) { return clamp(ivec2(floor((xz - ${ORIGIN.toFixed(1)}) / ${CELL.toFixed(1)})), ivec2(0), ivec2(${N - 1})); }
    float colH(ivec2 ij) { return texelFetch(tH, ij, 0).r; }
    bool airCut(vec3 p) {
      for (int i = 0; i < 256; i++) {
        if (i >= nAir) break;
        vec4 a = texelFetch(tAir, ivec2(0, i), 0);
        vec4 c0 = texelFetch(tAir, ivec2(1, i), 0);
        vec4 c1 = texelFetch(tAir, ivec2(2, i), 0);
        vec4 c2 = texelFetch(tAir, ivec2(3, i), 0);
        vec3 v = p - a.xyz;
        float br = a.w < 0.5 ? c0.w : (a.w < 1.5 ? length(vec3(c0.w, c1.w, c2.w)) : length(vec2(c0.w, c1.w)));
        if (dot(v, v) > br * br) continue;
        if (a.w < 0.5) return true;
        vec3 l = vec3(dot(c0.xyz, v), dot(c1.xyz, v), dot(c2.xyz, v));
        if (a.w < 1.5) { if (all(lessThan(abs(l), vec3(c0.w, c1.w, c2.w)))) return true; }
        else { if (length(l.xz) < c0.w && abs(l.y) < c1.w) return true; }
      }
      return false;
    }
    // Material eines Voxels wie im WorldBuilder
    int voxelMat(ivec2 ij, float y) {
      float h = colH(ij);
      vec4 inf = texelFetch(tInfo, ij, 0) * 255.0;
      int code = int(inf.r + 0.5);
      float s = floor(inf.b + 0.5);
      bool strata = code >= 32;
      int ti = strata ? code - 32 : code;
      float yc = floor(y / 4.0) * 4.0 + 2.0;
      float d = h - yc;
      if (strata) {
        if (ti != 0 && d < topDepth) return ti;
        float k = mod(floor(yc + s + strataBase), period);
        return int(texelFetch(tBand, ivec2(int(k), 0), 0).r * 255.0 + 0.5);
      }
      if (d < topDepth) return ti;
      if (d < subDepth) return subsoil[ti];
      return bedrock;
    }
    float matAmp(int m) {
      if (m == ${midx.Sand} || m == ${midx.Salt} || m == ${midx.Snow}) return 0.05;
      if (m == ${midx.Grass} || m == ${midx.LeafyGrass}) return 0.16;
      if (m == ${midx.Basalt} || m == ${midx.Rock} || m == ${midx.Slate}) return 0.14;
      return 0.10;
    }
    // Ersatz fuer Roblox-Texturen: leichte Helligkeits-Variation je Material
    vec3 varyColor(vec3 c, int m, float amp, vec3 p) {
      float n1 = vnoise(p * 0.33) - 0.5;
      float n2 = vnoise(p * 0.09 + 13.0) - 0.5;
      float n3 = hash3(floor(p / 4.0) + 0.5) - 0.5;
      c *= 1.0 + amp * (n1 * 0.9 + n2 * 0.7) + 0.035 * n3;
      if (m == ${midx.Sandstone}) c *= 1.0 + 0.05 * sin(p.y * 2.3 + n2 * 4.0);
      if (m == ${midx.CrackedLava}) {
        float cr = abs(vnoise(p * 0.45) - 0.5) + abs(vnoise(p * 0.9 + 7.0) - 0.5) * 0.5;
        c = mix(c * 0.38, c * 1.25, smoothstep(0.08, 0.0, cr));
      }
      return c;
    }
    vec3 matColor(int m, vec3 p, vec3 n) { return varyColor(matCol[m], m, matAmp(m), p); }
    // Roblox mischt Materialien benachbarter Voxel weich: bilinear ueber 2x2 Spalten (nur Spalten, die hier fest sind)
    // und an Steilwaenden zusaetzlich ueber die Voxel-Grenze in der Hoehe.
    vec3 blendedColor(vec2 q, float y, vec3 p, vec3 nn, out int domM) {
      vec2 g = (q - ${ORIGIN.toFixed(1)}) / ${CELL.toFixed(1)} - 0.5;
      ivec2 i0 = ivec2(floor(g));
      vec2 jit = vec2(vnoise(vec3(q * 0.55, 1.7)), vnoise(vec3(q * 0.55, 9.3))) - 0.5;
      vec2 jit2 = vec2(vnoise(vec3(q * 0.17, 4.1)), vnoise(vec3(q * 0.17, 2.2))) - 0.5;
      vec2 f = smoothstep(0.05, 0.95, g - vec2(i0) + jit * 0.55 + jit2 * 0.5);
      vec3 acc = vec3(0.0); float ws = 0.0; float amp = 0.0; float best = -1.0; domM = 0;
      float fy = fract(y / 4.0);
      float vw = 0.5 * smoothstep(0.55, 1.0, abs(fy - 0.5) * 2.0) * (1.0 - smoothstep(0.55, 0.85, abs(nn.y)));
      float yo = fy > 0.5 ? 4.0 : -4.0;
      for (int k = 0; k < 4; k++) {
        ivec2 o = ivec2(k & 1, k >> 1);
        ivec2 ij = clamp(i0 + o, ivec2(0), ivec2(${N - 1}));
        float w = (o.x == 1 ? f.x : 1.0 - f.x) * (o.y == 1 ? f.y : 1.0 - f.y);
        if (w < 0.001) continue;
        float h = colH(ij);
        if (h < -9000.0 || h < y - 2.5) continue;
        int m = voxelMat(ij, y);
        vec3 c = matCol[m];
        if (vw > 0.001) { int m2 = voxelMat(ij, y + yo); c = mix(c, matCol[m2], vw); }
        acc += w * c; ws += w; amp += w * matAmp(m);
        if (w > best) { best = w; domM = m; }
      }
      if (ws < 1e-4) { ivec2 ij = colAt(q); int m = voxelMat(ij, y); domM = m; return matCol[m]; }
      return acc / ws;
    }
    vec3 poolLight(vec3 p, vec3 n) {
      vec3 acc = vec3(0.0);
      for (int i = 0; i < 128; i++) {
        if (i >= nLights) break;
        vec4 a = texelFetch(tLights, ivec2(i, 0), 0);
        vec3 Lv = a.xyz - p;
        float d = length(Lv);
        if (d < a.w) {
          vec4 b = texelFetch(tLights, ivec2(i, 1), 0);
          float att = 1.0 - d / a.w; att *= att;
          acc += b.rgb * att * (0.35 + 0.65 * max(dot(n, Lv / max(d, 1e-3)), 0.0));
        }
      }
      return acc;
    }`;

  function terrainMat(kind) {
    // kind: 'top' | 'bottom' | 'airInner' | 'op'
    const m = new THREE.MeshLambertMaterial({ color: 0xffffff, side: kind === 'airInner' ? THREE.BackSide : THREE.FrontSide });
    m.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, TU);
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vWPos; varying vec3 vWNrm;')
        .replace('#include <fog_vertex>', `#include <fog_vertex>
          { vec4 wp4 = vec4(transformed, 1.0);
            vec3 wn = objectNormal;
            #ifdef USE_INSTANCING
              wp4 = instanceMatrix * wp4; wn = mat3(instanceMatrix) * wn;
            #endif
            vWPos = (modelMatrix * wp4).xyz; vWNrm = normalize(mat3(modelMatrix) * wn); }`);
      let colorCode;
      if (kind === 'op') {
        colorCode = `
          if (airCut(vWPos)) discard;
          vec3 tcol = vec3(1.0 + 0.10 * (vnoise(vWPos * 0.33) - 0.5) + 0.08 * (vnoise(vWPos * 0.1) - 0.5));`;
      } else if (kind === 'airInner') {
        colorCode = `
          ivec2 ij = colAt(vWPos.xz);
          float hh = colH(ij);
          float dd = texelFetch(tInfo, ij, 0).a * 255.0;
          if (hh < -9000.0 || vWPos.y > hh - 0.3 || vWPos.y < floor((hh - dd * 4.0) / 4.0) * 4.0) discard;
          int mm = voxelMat(ij, vWPos.y);
          vec3 tcol = matColor(mm, vWPos, normalize(vWNrm));`;
      } else {
        colorCode = `
          if (airCut(vWPos)) discard;
          vec3 nn = normalize(vWNrm);
          vec2 sh2 = nn.xz * 2.0;
          ivec2 ij = colAt(vWPos.xz - sh2);
          if (colH(ij) < -9000.0) ij = colAt(vWPos.xz);
          if (colH(ij) < -9000.0) ij = colAt(vWPos.xz + sh2);
          float yq = ${kind === 'bottom' ? 'vWPos.y + 0.5' : 'vWPos.y - 0.05'};
          int mm;
          vec3 tcol = blendedColor(vWPos.xz - sh2, yq, vWPos, nn, mm);
          tcol = varyColor(tcol, mm, matAmp(mm), vWPos);`;
      }
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', '#include <common>\n' + COMMON)
        .replace('vec4 diffuseColor = vec4( diffuse, opacity );', colorCode + '\n vec4 diffuseColor = vec4( tcol, opacity );')
        .replace('#include <lights_fragment_end>', '#include <lights_fragment_end>\n reflectedLight.directDiffuse += poolLight(vWPos, normalize(vWNrm)) * BRDF_Lambert(diffuseColor.rgb);');
    };
    m.customProgramCacheKey = () => 'terrain-' + kind;
    if (kind === 'op') {
      const prev = m.onBeforeCompile;
      m.onBeforeCompile = (sh) => {
        prev(sh);
        const disp = `
          #ifdef USE_INSTANCING
          { vec3 wpp = (modelMatrix * instanceMatrix * vec4(position, 1.0)).xyz;
            float nd = sin(wpp.x * 0.61 + wpp.z * 0.37) * sin(wpp.y * 0.73 - wpp.x * 0.29) + 0.5 * sin(wpp.z * 1.3 + wpp.y * 1.1);
            vec3 ln = normalize(mat3(instanceMatrix) * normal);
            vec3 wd = ln * nd * 0.55;
            transformed += (inverse(mat3(instanceMatrix)) * wd); }
          #endif`;
        sh.vertexShader = sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n' + disp);
      };
    }
    return m;
  }

  // ---------------------------------------------------------------- Terrain-Gitter (Oberseite + Unterseite am Rand)
  hud.textContent = 'baue Terrain ...';
  const top = new Float32Array(NN), bot = new Float32Array(NN);
  const state = new Uint8Array(NN); // 0 = nichts, 1 = gueltig, 2 = virtuell (Saum am Rand)
  for (let i = 0; i < NN; i++) {
    if (hTex[i] > VOID + 1) { state[i] = 1; top[i] = hTex[i]; bot[i] = Math.floor((hTex[i] - D[i] * 4) / 4) * 4; }
  }
  for (let iz = 0; iz < N; iz++) for (let ix = 0; ix < N; ix++) {
    const i = iz * N + ix;
    if (state[i]) continue;
    let mn = Infinity;
    for (let dz = -1; dz <= 1; dz++) for (let dx = -1; dx <= 1; dx++) {
      const jx = ix + dx, jz = iz + dz;
      if (jx < 0 || jz < 0 || jx >= N || jz >= N) continue;
      const j = jz * N + jx;
      if (state[j] === 1) mn = Math.min(mn, bot[j]);
    }
    if (mn < Infinity) { state[i] = 2; top[i] = mn; bot[i] = mn; }
  }
  function buildGrid(kind) {
    const vid = new Int32Array(NN).fill(-1);
    const pos = [];
    let nv = 0;
    const deep = (i) => state[i] === 2 || (state[i] === 1 && D[i] >= 8);
    for (let i = 0; i < NN; i++) {
      const ok = kind === 'top' ? state[i] > 0 : deep(i);
      if (!ok) continue;
      const ix = i % N, iz = (i / N) | 0;
      vid[i] = nv++;
      pos.push(ORIGIN + CELL / 2 + CELL * ix, kind === 'top' ? top[i] : bot[i], ORIGIN + CELL / 2 + CELL * iz);
    }
    const idx = [];
    for (let iz = 0; iz < N - 1; iz++) for (let ix = 0; ix < N - 1; ix++) {
      const a = iz * N + ix, b = a + 1, c = a + N, d = c + 1;
      if (vid[a] < 0 || vid[b] < 0 || vid[c] < 0 || vid[d] < 0) continue;
      if (kind === 'top' && state[a] !== 1 && state[b] !== 1 && state[c] !== 1 && state[d] !== 1) continue;
      if (kind === 'bottom' && !(state[a] === 1 || state[b] === 1 || state[c] === 1 || state[d] === 1)) continue;
      const A = vid[a], B = vid[b], C = vid[c], Dd = vid[d];
      const ha = pos[A * 3 + 1], hb = pos[B * 3 + 1], hc = pos[C * 3 + 1], hd = pos[Dd * 3 + 1];
      const diagAD = Math.abs(ha - hd) < Math.abs(hb - hc);
      if (kind === 'top') {
        if (diagAD) idx.push(A, C, Dd, A, Dd, B); else idx.push(A, C, B, B, C, Dd);
      } else {
        if (diagAD) idx.push(A, Dd, C, A, B, Dd); else idx.push(A, B, C, B, Dd, C);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(nv > 65535 ? new THREE.Uint32BufferAttribute(idx, 1) : new THREE.Uint16BufferAttribute(idx, 1));
    g.computeVertexNormals();
    return g;
  }
  const gTop = buildGrid('top');
  const terrainTop = new THREE.Mesh(gTop, terrainMat('top'));
  terrainTop.castShadow = true; terrainTop.receiveShadow = true;
  scene.add(terrainTop);
  const gBot = buildGrid('bottom');
  const terrainBot = new THREE.Mesh(gBot, terrainMat('bottom'));
  terrainBot.castShadow = true; terrainBot.receiveShadow = true;
  scene.add(terrainBot);

  // ---------------------------------------------------------------- Wasser
  {
    const pos = [];
    for (let i = 0; i < NN; i++) {
      if (!Wt[i] || state[i] !== 1) continue;
      const lv = lvls[Wt[i]];
      if (lv <= Math.ceil(top[i] / 4) * 4) continue;   // Builder-Regel: Wasser nur in Voxeln oberhalb der Terrain-Oberkante
      const ix = i % N, iz = (i / N) | 0;
      const x0 = ORIGIN + CELL * ix, z0 = ORIGIN + CELL * iz;
      pos.push(x0, lv, z0, x0, lv, z0 + CELL, x0 + CELL, lv, z0, x0 + CELL, lv, z0, x0, lv, z0 + CELL, x0 + CELL, lv, z0 + CELL);
    }
    if (pos.length) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      g.computeVertexNormals();
      const wcol = lin(meta.water?.WaterColor || [95, 227, 214]);
      const wm = new THREE.MeshStandardMaterial({ color: wcol, transparent: true, opacity: 1 - (meta.water?.WaterTransparency ?? 0.35) * 0.9,
        roughness: 0.06, metalness: 0.0, envMapIntensity: (meta.water?.WaterReflectance ?? 0.4) * 2.2 });
      const water = new THREE.Mesh(g, wm);
      water.receiveShadow = true;
      water.renderOrder = 2;
      water.userData.isWater = true;
      scene.add(water);
    }
  }

  // ---------------------------------------------------------------- Zusatzformen (positiv) + Innenflaechen der Luft-Formen
  {
    const geos = { Ball: new THREE.SphereGeometry(1, 28, 18), Block: new THREE.BoxGeometry(1, 1, 1, 4, 4, 4), Cylinder: new THREE.CylinderGeometry(1, 1, 1, 28, 8) };
    const groups = { Ball: [], Block: [], Cylinder: [] };
    for (const o of scn.terrainOps) {
      const m4 = new THREE.Matrix4();
      if (o.op === 'Ball') m4.compose(new THREE.Vector3(...o.c), new THREE.Quaternion(), new THREE.Vector3(o.r, o.r, o.r));
      else {
        const R = o.cf.slice(3);
        const rot = new THREE.Matrix4().set(R[0], R[1], R[2], 0, R[3], R[4], R[5], 0, R[6], R[7], R[8], 0, 0, 0, 0, 1);
        const sc = o.op === 'Block' ? new THREE.Vector3(...o.size) : new THREE.Vector3(o.r, o.height, o.r);
        m4.makeTranslation(o.cf[0], o.cf[1], o.cf[2]).multiply(rot).multiply(new THREE.Matrix4().makeScale(sc.x, sc.y, sc.z));
      }
      groups[o.op === 'Wedge' ? 'Block' : o.op].push({ m4, mat: o.material });
    }
    for (const [shape, list] of Object.entries(groups)) {
      const pos = list.filter((e) => e.mat !== 'Air');
      if (pos.length) {
        const im = new THREE.InstancedMesh(geos[shape], terrainMat('op'), pos.length);
        pos.forEach((e, i) => { im.setMatrixAt(i, e.m4); im.setColorAt(i, matCol[midx[e.mat]] || new THREE.Color(1, 0, 1)); });
        im.castShadow = true; im.receiveShadow = true;
        scene.add(im);
      }
      const air = list.filter((e) => e.mat === 'Air');
      if (air.length) {
        const im = new THREE.InstancedMesh(geos[shape], terrainMat('airInner'), air.length);
        air.forEach((e, i) => im.setMatrixAt(i, e.m4));
        im.receiveShadow = true;
        scene.add(im);
      }
    }
  }

  // ---------------------------------------------------------------- Himmel
  const skyUniforms = { tSky: { value: null }, hasSky: { value: 0 } };
  {
    const names = ['px', 'nx', 'py', 'ny', 'pz', 'nz'];
    let ok = true;
    for (const n of names) { const r = await fetch(DATA + 'sky/' + n + '.png', { method: 'HEAD' }); if (!r.ok) { ok = false; break; } }
    if (ok) {
      const cube = await new THREE.CubeTextureLoader().setPath(DATA + 'sky/').loadAsync(names.map((n) => n + '.png'));
      cube.colorSpace = THREE.SRGBColorSpace;
      scene.background = cube;          // normal laden, three.js spiegelt beim Abtasten selbst
      scene.environment = cube;
      skyUniforms.hasSky.value = 1;
    }
    const satAz = deg(40), satEl = deg(28);
    const SAT = new THREE.Vector3(Math.sin(satAz) * Math.cos(satEl), Math.sin(satEl), -Math.cos(satAz) * Math.cos(satEl));
    const skyMat = new THREE.ShaderMaterial({
      uniforms: skyUniforms, depthWrite: false, side: THREE.BackSide, transparent: true,
      vertexShader: 'varying vec3 vDir; void main(){ vDir = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position,1.0); gl_Position = p.xyww; }',
      fragmentShader: `
        uniform samplerCube tSky; uniform int hasSky; varying vec3 vDir;
        ${ATMO.replace(/cameraPosition/g, 'vec3(0.0)')}
        float h1(vec3 p){ return fract(sin(dot(p, vec3(12.9898,78.233,37.719))) * 43758.5453); }
        vec3 srgb2lin(vec3 c){ return pow(c, vec3(2.2)); }
        void main(){
          vec3 d = normalize(vDir);
          vec3 col = vec3(0.0);
          if (hasSky == 1) {
            // nur Dunst-Schicht ueber dem Hintergrund (Saturn bei El 28 bleibt klar)
          } else {
            float e = d.y;
            vec3 zen = srgb2lin(vec3(0.039,0.106,0.173)), hor = srgb2lin(vec3(0.122,0.31,0.36)), und = srgb2lin(vec3(0.165,0.141,0.25));
            col = e > 0.0 ? mix(hor, zen, pow(e, 0.6)) : mix(hor, und, pow(-e, 0.5));
            vec3 g = floor(d * 420.0);
            float s = h1(g);
            if (s > 0.9965) col += vec3(0.9, 0.95, 1.0) * (s - 0.9965) * 300.0 * 0.6;
            // grober Platzhalter fuer Saturn (nur bis die echte Skybox da ist)
            vec3 sd = ${'vec3(' + SAT.x.toFixed(4) + ',' + SAT.y.toFixed(4) + ',' + SAT.z.toFixed(4) + ')'};
            float ang = acos(clamp(dot(d, sd), -1.0, 1.0));
            vec3 up = normalize(vec3(0.0,1.0,0.0) - sd * sd.y);
            vec3 rt = normalize(cross(sd, up));
            float px = dot(d - sd, rt), py = dot(d - sd, up);
            float rr = 0.122;
            float qx = px * cos(0.244) - py * sin(0.244), qy = px * sin(0.244) + py * cos(0.244);
            float ell = length(vec2(qx, qy / 0.34));
            bool ring = ell > rr * 1.24 && ell < rr * 2.27 && !(ell > rr * 1.95 && ell < rr * 2.03);
            bool front = qy < 0.0;
            vec3 satc = srgb2lin(vec3(0.85, 0.78, 0.6)) * (0.9 + 0.1 * sin(py * 90.0));
            if (ang < rr && !(ring && front)) col = satc * (0.45 + 0.55 * smoothstep(0.1, -0.06, px));
            else if (ring && (front || ang > rr)) col = mix(col, srgb2lin(vec3(0.8, 0.74, 0.6)), ell < rr * 1.53 ? 0.45 : 0.85);
          }
          // Atmosphaere ueber dem Himmel: nur der Horizont-Bereich verschwimmt (El < ~10 Grad)
          float hz = exp(-abs(d.y) / 0.075) * (d.y > 0.0 ? 1.0 : 0.85);
          hz = clamp(hz * ${(0.55 + 0.6 * density).toFixed(3)}, 0.0, 0.9);
          if (hasSky == 1) gl_FragColor = vec4(atmoColorDir(d), hz);
          else gl_FragColor = vec4(mix(col, atmoColorDir(d), hz), 1.0);
        }`,
    });
    const sky = new THREE.Mesh(new THREE.SphereGeometry(10000, 64, 32), skyMat);
    sky.frustumCulled = false;
    sky.renderOrder = -10;
    sky.userData.sky = true;
    scene.add(sky);
    scene.userData.sky = sky;
  }

  // ---------------------------------------------------------------- Deko
  const partCount = { n: 0, lights: 0 };
  const steamPuffs = [];
  {
    const wedge = new THREE.BufferGeometry();
    {
      // Roblox-WedgePart: Boden voll, Rueckwand bei +Z, Schraege von oben-hinten nach unten-vorne (-Z)
      const P = [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [0.5, 0.5, 0.5]];
      const F = [[0, 1, 2], [0, 2, 3], [3, 2, 5], [3, 5, 4], [0, 4, 5], [0, 5, 1], [0, 3, 4], [1, 5, 2]];
      const pos = [];
      for (const f of F) for (const k of f) pos.push(...P[k]);
      wedge.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      wedge.computeVertexNormals();
    }
    const cyl = new THREE.CylinderGeometry(0.5, 0.5, 1, 20); cyl.rotateZ(Math.PI / 2);   // Achse X
    const GEO = { Block: new THREE.BoxGeometry(1, 1, 1), Ball: new THREE.SphereGeometry(0.5, 20, 14), Ellipsoid: new THREE.SphereGeometry(0.5, 20, 14), Cylinder: cyl, Wedge: wedge };
    const groups = new Map();
    const tmp = new THREE.Matrix4(), mPlace = new THREE.Matrix4(), mPart = new THREE.Matrix4(), mRot = new THREE.Matrix4();
    const rx = new THREE.Matrix4(), ry = new THREE.Matrix4(), rz = new THREE.Matrix4();
    for (const [name, arr] of Object.entries(scn.placements)) {
      const t = scn.templates[name];
      for (let k = 0; k < arr.length; k += 8) {
        const [x, y, z, a, b, cc, s, v] = arr.slice(k, k + 8);
        const colors = t.variants[v] || t.variants[0];
        mPlace.makeTranslation(x, y, z).multiply(ry.makeRotationY(a)).multiply(rx.makeRotationX(b)).multiply(rz.makeRotationZ(cc));
        for (const p of t.parts) {
          const R = p.rot;
          mRot.set(R[0], R[1], R[2], 0, R[3], R[4], R[5], 0, R[6], R[7], R[8], 0, 0, 0, 0, 1);
          let sx = p.size[0] * s, sy = p.size[1] * s, sz = p.size[2] * s;
          if (p.shape === 'Ball') { const m = Math.min(sx, sy, sz); sx = sy = sz = m; }
          if (p.shape === 'Cylinder') { const d = Math.min(sy, sz); sy = sz = d; }
          mPart.makeTranslation(p.pos[0] * s, p.pos[1] * s, p.pos[2] * s).multiply(mRot).multiply(tmp.makeScale(sx, sy, sz));
          const world = new THREE.Matrix4().multiplyMatrices(mPlace, mPart);
          const neon = p.material === 'Neon';
          const tr = Math.round((p.transparency || 0) * 20) / 20;
          const glass = p.material === 'Glass';
          const key = `${p.shape}|${neon ? 'N' : glass ? 'G' : 'S'}|${tr}|${p.castShadow ? 1 : 0}`;
          if (!groups.has(key)) groups.set(key, { shape: p.shape, neon, glass, tr, cast: p.castShadow, m: [], c: [] });
          const col = lin(colors[p.role] || [255, 0, 255]);
          const gr = groups.get(key);
          gr.m.push(world); gr.c.push(col);
          partCount.n++;
          if (p.light && lightList.length < 128) {
            const lp = new THREE.Vector3(p.pos[0] * s, p.pos[1] * s, p.pos[2] * s).applyMatrix4(mPlace);
            const lc = lin(colors[p.light.role || p.role] || [255, 255, 255]);
            lightList.push({ p: lp, range: Math.min(60, p.light.range * s), c: lc, b: p.light.brightness });
          }
          if (p.particles) steamPuffs.push({ p: new THREE.Vector3(p.pos[0] * s, p.pos[1] * s, p.pos[2] * s).applyMatrix4(mPlace), s });
        }
      }
    }
    for (const g of groups.values()) {
      let mat;
      if (g.neon) mat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: g.tr > 0, opacity: 1 - g.tr * 0.85, depthWrite: g.tr < 0.5 });
      else if (g.glass) mat = new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: Math.max(0.15, 1 - g.tr), roughness: 0.1, metalness: 0.1 });
      else mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.62, metalness: 0.0, transparent: g.tr > 0, opacity: 1 - g.tr, depthWrite: g.tr < 0.5 });
      const im = new THREE.InstancedMesh(GEO[g.shape], mat, g.m.length);
      g.m.forEach((m, i) => im.setMatrixAt(i, m));
      g.c.forEach((c, i) => im.setColorAt(i, g.neon ? c.clone().multiplyScalar(NEON_GAIN) : c));
      im.castShadow = g.cast && g.tr < 0.5; im.receiveShadow = !g.neon;
      if (g.tr > 0) im.renderOrder = 3;
      scene.add(im);
    }
    // Dampf als Platzhalter (der Builder setzt echte ParticleEmitter)
    if (steamPuffs.length) {
      const pm = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.1, 1.08, 1.12), transparent: true, opacity: 0.16, depthWrite: false });
      const n = steamPuffs.length * 7;
      const im = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 12, 8), pm, n);
      let i = 0;
      for (const sp of steamPuffs) for (let k = 0; k < 7; k++) {
        const r = (2 + k * 1.4) * sp.s;
        tmp.compose(new THREE.Vector3(sp.p.x + Math.sin(k * 1.7) * k * 0.8, sp.p.y + 2 + k * 4.2 * sp.s, sp.p.z + Math.cos(k * 2.1) * k * 0.8 + k * 0.6),
          new THREE.Quaternion(), new THREE.Vector3(r, r, r));
        im.setMatrixAt(i++, tmp);
      }
      im.renderOrder = 4;
      scene.add(im);
    }
    lightList.forEach((l, i) => {
      lightTexData.set([l.p.x, l.p.y, l.p.z, l.range], i * 4);
      lightTexData.set([l.c.r * l.b * 2.4, l.c.g * l.b * 2.4, l.c.b * l.b * 2.4, 0], (128 + i) * 4);
    });
    texLights.needsUpdate = true;
    TU.nLights.value = lightList.length;
    partCount.lights = lightList.length;
  }

  // ---------------------------------------------------------------- Platzhalter Basis (nur Vorschau)
  {
    const base = new THREE.Mesh(new THREE.BoxGeometry(120, 30, 60), new THREE.MeshStandardMaterial({ color: lin([242, 140, 40]), roughness: 0.5 }));
    base.position.set(0, 15, 0);
    base.rotation.y = -deg(40);
    base.castShadow = base.receiveShadow = true;
    scene.add(base);
  }

  // ---------------------------------------------------------------- Kamera + Nachbearbeitung
  const camera = new THREE.PerspectiveCamera(70, WIDTH / HEIGHT, 0.5, 30000);
  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(WIDTH, HEIGHT, { type: THREE.HalfFloatType }));
  composer.addPass(new RenderPass(scene, camera));
  const B = L.Bloom || {};
  const bloom = new UnrealBloomPass(new THREE.Vector2(WIDTH, HEIGHT), (B.Intensity ?? 0.45) * 1.6, Math.min(1, (B.Size ?? 24) / 40), (B.Threshold ?? 1.4) * 0.8);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const CC = L.ColorCorrection || {};
  const tint = lin(CC.TintColor || [255, 241, 230]);
  const ccPass = new ShaderPass({
    uniforms: { tDiffuse: { value: null }, br: { value: CC.Brightness ?? 0.02 }, ct: { value: CC.Contrast ?? 0.12 }, sat: { value: CC.Saturation ?? 0.18 },
      tint: { value: new THREE.Vector3(Math.pow(tint.r, 1 / 2.2), Math.pow(tint.g, 1 / 2.2), Math.pow(tint.b, 1 / 2.2)) } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `uniform sampler2D tDiffuse; uniform float br, ct, sat; uniform vec3 tint; varying vec2 vUv;
      void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb; c += br; c = (c - 0.5) * (1.0 + ct) + 0.5;
        float l = dot(c, vec3(0.299, 0.587, 0.114)); c = mix(vec3(l), c, 1.0 + sat); c *= tint; gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0); }`,
  });
  composer.addPass(ccPass);
  const fxaa = new ShaderPass(FXAAShader);
  fxaa.uniforms.resolution.value.set(1 / WIDTH, 1 / HEIGHT);
  composer.addPass(fxaa);

  const cams = (scn.preview && scn.preview.cameras) || {};
  function applyPreset(name) {
    const c = cams[name];
    if (!c) throw new Error('unbekannte Kamera ' + name);
    camera.fov = c.fov || 70;
    camera.aspect = WIDTH / HEIGHT;
    camera.near = c.near || 0.5;
    camera.position.set(...c.pos);
    camera.up.set(0, 1, 0);
    if (c.up) camera.up.set(...c.up);
    camera.lookAt(new THREE.Vector3(...c.target));
    camera.updateProjectionMatrix();
    const sc = c.shadow || { center: [c.target[0], c.target[2]], radius: 800 };
    const cx = sc.center[0], cz = sc.center[1];
    const cy = 0;
    sun.target.position.set(cx, cy, cz);
    sun.position.set(cx + SUN.x * 4000, cy + SUN.y * 4000, cz + SUN.z * 4000);
    const cam = sun.shadow.camera;
    cam.left = -sc.radius; cam.right = sc.radius; cam.top = sc.radius; cam.bottom = -sc.radius;
    cam.near = 100; cam.far = 9000;
    cam.updateProjectionMatrix();
    sun.shadow.needsUpdate = true;
    scene.userData.sky.position.copy(camera.position);
    hud.textContent = name;
  }
  window.presets = Object.keys(cams);
  window.shot = async (name, hideHud = true) => {
    applyPreset(name);
    hud.style.display = hideHud ? 'none' : 'block';
    const t0 = performance.now();
    composer.render();
    const gl = renderer.getContext();
    const px = new Uint8Array(4);
    gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);   // wartet, bis das Bild fertig ist
    await new Promise((r) => requestAnimationFrame(() => r()));
    return performance.now() - t0;
  };
  window.stats = { parts: partCount.n, lights: partCount.lights, ops: scn.terrainOps.length, air: airOps.length };

  if (Q.get('shot')) {
    if (Q.get('shot') !== 'none') await window.shot(Q.get('shot'), false);
  } else {
    const controls = new OrbitControls(camera, renderer.domElement);
    applyPreset(Object.keys(cams)[0]);
    controls.target.set(...cams[Object.keys(cams)[0]].target);
    const loop = () => { controls.update(); scene.userData.sky.position.copy(camera.position); composer.render(); requestAnimationFrame(loop); };
    loop();
  }
  window.__ready = true;
}

main().catch((e) => { hud.textContent = 'Fehler: ' + e.message; console.error(e); window.__error = String(e.stack || e); });
