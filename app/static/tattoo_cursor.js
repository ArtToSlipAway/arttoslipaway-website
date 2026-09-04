/* ATS_CARTRIDGE_CURSOR_V3 */
(() => {
  "use strict";

  const fine = matchMedia("(hover:hover) and (pointer:fine)");
  const reduced = matchMedia("(prefers-reduced-motion:reduce)");
  if (!fine.matches || reduced.matches || document.getElementById("atsCartridgeCursor")) return;

  const style = document.createElement("style");
  style.textContent = `
html.ats-cartridge-on,html.ats-cartridge-on body,html.ats-cartridge-on body *{cursor:none!important}
html.ats-cartridge-on input,html.ats-cartridge-on textarea,html.ats-cartridge-on select,html.ats-cartridge-on [contenteditable="true"]{cursor:text!important}
#atsCartridgeCursor{position:fixed;inset:0 auto auto 0;width:0;height:0;z-index:2147483647;pointer-events:none;opacity:0;transition:opacity .12s ease}
#atsCartridgeCursor.show{opacity:1}#atsCartridgeCursor.hide{opacity:0}
.ats-cartridge-tip,.ats-cartridge-machine{position:fixed;left:0;top:0;pointer-events:none;will-change:transform}
.ats-cartridge-tip{width:5px;height:5px;margin:-2.5px 0 0 -2.5px;border-radius:50%;background:#080604;box-shadow:0 0 0 1px rgba(229,196,112,.9),0 0 9px rgba(208,160,54,.62)}
.ats-cartridge-machine{width:52px;height:102px;transform-origin:26px 102px;filter:drop-shadow(0 3px 5px rgba(0,0,0,.58)) drop-shadow(0 0 7px rgba(188,135,45,.28))}
.ats-cartridge-machine svg{display:block;width:52px;height:102px;overflow:visible}
.ats-cartridge-label{position:absolute;left:34px;top:54px;color:#edd17b;font:700 8px/1 Arial,sans-serif;letter-spacing:.14em;opacity:0;text-shadow:0 0 7px rgba(221,173,50,.8)}
#atsCartridgeCursor.hot .ats-cartridge-machine{animation:ats-cartridge-buzz 72ms steps(2,end) infinite;filter:drop-shadow(0 3px 5px rgba(0,0,0,.6)) drop-shadow(0 0 10px rgba(215,164,55,.5))}
#atsCartridgeCursor.down .ats-cartridge-machine{animation:none;scale:.94}
#atsCartridgeCursor.down .ats-cartridge-tip{width:13px;height:13px;margin:-6.5px 0 0 -6.5px;background:radial-gradient(circle,#080604 0 28%,rgba(142,94,27,.78) 32% 45%,rgba(219,167,54,.35) 48% 61%,transparent 65%);box-shadow:8px 2px 0 -5px rgba(147,93,22,.82),-7px 4px 0 -5px rgba(111,70,18,.78),1px -8px 0 -5px rgba(213,159,45,.72),0 0 16px rgba(211,158,44,.7)}
#atsCartridgeCursor.mode3d .ats-cartridge-label{opacity:1}
.ats-cartridge-pulse{position:fixed;width:10px;height:10px;margin:-5px 0 0 -5px;border:1px solid rgba(216,170,58,.88);border-radius:50%;pointer-events:none;z-index:2147483646;animation:ats-cartridge-pulse .42s ease-out forwards}
@keyframes ats-cartridge-buzz{0%{margin-left:-.7px;margin-top:.35px}100%{margin-left:.7px;margin-top:-.35px}}
@keyframes ats-cartridge-pulse{from{opacity:.9;transform:scale(.35)}to{opacity:0;transform:scale(4.4)}}
@media (hover:none),(pointer:coarse),(prefers-reduced-motion:reduce){#atsCartridgeCursor{display:none!important}}
`;
  document.head.appendChild(style);

  const cursor = document.createElement("div");
  cursor.id = "atsCartridgeCursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.innerHTML = `
<div class="ats-cartridge-machine">
<svg viewBox="0 0 52 102" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="atsGlass" x1="0" x2="1">
<stop offset="0" stop-color="#2a1913" stop-opacity=".92"/>
<stop offset=".18" stop-color="#8c6555" stop-opacity=".68"/>
<stop offset=".43" stop-color="#d0b4a2" stop-opacity=".38"/>
<stop offset=".64" stop-color="#563a30" stop-opacity=".76"/>
<stop offset="1" stop-color="#1d1210" stop-opacity=".94"/>
</linearGradient>
<linearGradient id="atsMetal" x1="0" x2="1">
<stop offset="0" stop-color="#2b211d"/><stop offset=".22" stop-color="#cab6a9"/><stop offset=".48" stop-color="#54453e"/><stop offset=".72" stop-color="#ead9cc"/><stop offset="1" stop-color="#2b211d"/>
</linearGradient>
<linearGradient id="atsClear" x1="0" x2="1">
<stop offset="0" stop-color="#4b332b" stop-opacity=".55"/><stop offset=".35" stop-color="#f0ddd0" stop-opacity=".28"/><stop offset=".7" stop-color="#806055" stop-opacity=".38"/><stop offset="1" stop-color="#241713" stop-opacity=".62"/>
</linearGradient>
</defs>
<rect x="22" y="1" width="8" height="21" rx="3" fill="#f4f4ef" fill-opacity=".92" stroke="#c9c9c5" stroke-width=".8"/>
<rect x="15" y="18" width="22" height="10" rx="4" fill="url(#atsMetal)" stroke="#1b1411" stroke-width="1"/>
<path d="M13 25Q26 20 39 25L37 60Q36 69 31 75H21Q16 69 15 60Z" fill="url(#atsGlass)" stroke="#1d1411" stroke-width="1.2"/>
<path d="M18 30L20 61Q21 67 24 71" fill="none" stroke="#e4cec0" stroke-opacity=".42" stroke-width="1"/>
<path d="M34 29L32 61Q31 67 28 72" fill="none" stroke="#f0dbcb" stroke-opacity=".28" stroke-width="1"/>
<path d="M20 37L32 33L34 56L25 66L18 59Z" fill="#251a17" fill-opacity=".78" stroke="#b99d8c" stroke-opacity=".7" stroke-width=".8"/>
<path d="M23 38L30 36L31 53L25 60L21 56Z" fill="url(#atsMetal)" stroke="#1b1412" stroke-width=".7"/>
<rect x="24.8" y="27" width="2.4" height="54" rx="1.2" fill="url(#atsMetal)"/>
<path d="M18 69H34L32 83L27 101H25L20 84Z" fill="url(#atsClear)" stroke="#2b1b17" stroke-width="1.1"/>
<path d="M20 76L31 73L29 84L24 91L21 85Z" fill="#7f5c50" fill-opacity=".35" stroke="#d7beb0" stroke-opacity=".38" stroke-width=".7"/>
<path d="M26 76V101" stroke="#f2e6dc" stroke-width=".9"/>
<path d="M26 92V102" stroke="#fff8ee" stroke-width=".7"/>
<circle cx="26" cy="102" r="1.25" fill="#e2ba5b"/>
</svg>
<span class="ats-cartridge-label">3D</span>
</div>
<div class="ats-cartridge-tip"></div>`;
  document.body.appendChild(cursor);
  document.documentElement.classList.add("ats-cartridge-on");

  const machine = cursor.querySelector(".ats-cartridge-machine");
  const tip = cursor.querySelector(".ats-cartridge-tip");

  let x = innerWidth / 2, y = innerHeight / 2, mx = x, my = y, ready = false;
  const hotSel = 'a,button,summary,[role="button"],.main-card,.subcard,.free-sketch-card,.project-card,.category-card';
  const modelSel = 'model-viewer,canvas,.model-viewer,[data-model-viewer],.free-sketch-model-viewer,.free-sketch-preview--model-card';
  const textSel = 'input,textarea,select,[contenteditable="true"]';
  const closest = (target, selector) => target instanceof Element ? target.closest(selector) : null;

  function frame() {
    mx += (x - mx) * .24;
    my += (y - my) * .24;
    const angle = cursor.classList.contains("mode3d") ? 82 : 38;
    machine.style.transform = `translate3d(${mx - 26}px,${my - 102}px,0) rotate(${angle}deg)`;
    requestAnimationFrame(frame);
  }

  document.addEventListener("pointermove", e => {
    x = e.clientX; y = e.clientY;
    if (!ready) { mx = x; my = y; ready = true; }
    tip.style.transform = `translate3d(${x}px,${y}px,0)`;
    const text = closest(e.target, textSel);
    const model = closest(e.target, modelSel);
    const hot = closest(e.target, hotSel);
    cursor.classList.toggle("hide", !!text);
    cursor.classList.toggle("mode3d", !!model);
    cursor.classList.toggle("hot", !!(hot || model));
    cursor.classList.add("show");
  }, {passive:true});

  document.addEventListener("pointerdown", () => {
    cursor.classList.add("down");
    const pulse = document.createElement("div");
    pulse.className = "ats-cartridge-pulse";
    pulse.style.left = x + "px";
    pulse.style.top = y + "px";
    document.body.appendChild(pulse);
    setTimeout(() => pulse.remove(), 450);
  }, {passive:true});

  document.addEventListener("pointerup", () => cursor.classList.remove("down"), {passive:true});
  document.documentElement.addEventListener("mouseleave", () => cursor.classList.remove("show"));
  addEventListener("blur", () => cursor.classList.remove("show", "down"));
  frame();
})();
