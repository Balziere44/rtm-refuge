/* Four effects from React Bits, ported to plain JavaScript.

   The originals are React components that pull in `ogl` and `gsap`. This site
   has no framework, no bundler and no build step on the host - what is
   committed is what the browser receives - so each one is reimplemented here
   against the platform directly. `ogl` is a thin wrapper over WebGL2, and the
   two shaders below are the originals verbatim; gsap's part in FoldText is a
   staggered transform, which CSS does natively.

   Everything here is decoration. It all checks prefers-reduced-motion, it all
   degrades to nothing if WebGL is missing, and no part of the site depends on
   any of it having run. */
(function () {
  'use strict';

  var still = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------------------------------------------------------------------
     A minimal WebGL2 harness: one full-screen triangle, one fragment shader.
     That is all either shader effect needs, and it is a fraction of a
     general-purpose renderer.
     --------------------------------------------------------------------- */

  var VERT = '#version 300 es\n' +
    'in vec2 position;\n' +
    'void main() { gl_Position = vec4(position, 0.0, 1.0); }\n';

  function compile(gl, type, source) {
    var s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      throw new Error(gl.getShaderInfoLog(s));
    }
    return s;
  }

  function triangleProgram(canvas, frag) {
    var gl = canvas.getContext('webgl2', {
      alpha: true, premultipliedAlpha: true, antialias: true
    });
    if (!gl) return null;

    var program = gl.createProgram();
    gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERT));
    gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, frag));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error(gl.getProgramInfoLog(program));
    }
    gl.useProgram(program);

    // One triangle large enough to cover the clip space. Cheaper than two,
    // and no seam down the diagonal.
    var buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]),
                  gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    var uniforms = {};
    var n = gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS);
    for (var i = 0; i < n; i++) {
      var name = gl.getActiveUniform(program, i).name.replace(/\[0\]$/, '');
      uniforms[name] = gl.getUniformLocation(program, name);
    }

    return { gl: gl, program: program, u: uniforms };
  }

  function hexToRgb(hex) {
    var h = hex.replace('#', '');
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var n = parseInt(h, 16);
    // The shader works in linear-ish space the same way ogl's Color does:
    // straight 0-1 components, no gamma conversion.
    return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
  }

  /* Anything that animates registers here, so a single rAF drives the page
     and a hidden tab costs nothing. */
  var loops = [];
  var running = false;

  function frame(t) {
    running = false;
    for (var i = 0; i < loops.length; i++) loops[i](t);
    if (loops.length && !document.hidden) {
      running = true;
      requestAnimationFrame(frame);
    }
  }

  function animate(fn) {
    loops.push(fn);
    if (!running) { running = true; requestAnimationFrame(frame); }
  }

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden && loops.length && !running) {
      running = true;
      requestAnimationFrame(frame);
    }
  });

  /* =====================================================================
     1. Aurora
     The fragment shader is the React Bits original, unchanged.
     ===================================================================== */

  var AURORA_FRAG = '#version 300 es\n' + [
    'precision highp float;',
    'uniform float uTime;',
    'uniform float uAmplitude;',
    'uniform vec3 uColorStops[3];',
    'uniform vec2 uResolution;',
    'uniform float uBlend;',
    'out vec4 fragColor;',
    'vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }',
    'float snoise(vec2 v){',
    '  const vec4 C = vec4(0.211324865405187, 0.366025403784439,',
    '      -0.577350269189626, 0.024390243902439);',
    '  vec2 i  = floor(v + dot(v, C.yy));',
    '  vec2 x0 = v - i + dot(i, C.xx);',
    '  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);',
    '  vec4 x12 = x0.xyxy + C.xxzz;',
    '  x12.xy -= i1;',
    '  i = mod(i, 289.0);',
    '  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));',
    '  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);',
    '  m = m * m; m = m * m;',
    '  vec3 x = 2.0 * fract(p * C.www) - 1.0;',
    '  vec3 h = abs(x) - 0.5;',
    '  vec3 ox = floor(x + 0.5);',
    '  vec3 a0 = x - ox;',
    '  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);',
    '  vec3 g;',
    '  g.x  = a0.x  * x0.x  + h.x  * x0.y;',
    '  g.yz = a0.yz * x12.xz + h.yz * x12.yw;',
    '  return 130.0 * dot(m, g);',
    '}',
    'void main() {',
    '  vec2 uv = gl_FragCoord.xy / uResolution;',
    '  vec3 rampColor;',
    '  if (uv.x < 0.5) {',
    '    rampColor = mix(uColorStops[0], uColorStops[1], uv.x / 0.5);',
    '  } else {',
    '    rampColor = mix(uColorStops[1], uColorStops[2], (uv.x - 0.5) / 0.5);',
    '  }',
    '  float height = snoise(vec2(uv.x * 2.0 + uTime * 0.1, uTime * 0.25)) * 0.5 * uAmplitude;',
    '  height = exp(height);',
    '  height = (uv.y * 2.0 - height + 0.2);',
    '  float intensity = 0.6 * height;',
    '  float midPoint = 0.20;',
    '  float auroraAlpha = smoothstep(midPoint - uBlend * 0.5, midPoint + uBlend * 0.5, intensity);',
    '  vec3 auroraColor = intensity * rampColor;',
    '  fragColor = vec4(auroraColor * auroraAlpha, auroraAlpha);',
    '}'
  ].join('\n') + '\n';

  function aurora(host) {
    // The CSS aurora underneath is the fallback. It only steps aside once
    // WebGL has actually compiled, so a failure here is invisible.
    var canvas = document.createElement('canvas');
    var ctx;
    try {
      ctx = triangleProgram(canvas, AURORA_FRAG);
    } catch (e) {
      return;
    }
    if (!ctx) return;

    var gl = ctx.gl, u = ctx.u;
    var stops = ['#33136a', '#B497CF', '#9e27ff'];
    gl.uniform3fv(u.uColorStops, new Float32Array(
      stops.reduce(function (a, h) { return a.concat(hexToRgb(h)); }, [])));
    gl.uniform1f(u.uAmplitude, 1.0);
    gl.uniform1f(u.uBlend, 0.5);

    function resize() {
      // Half resolution: this is a blurred field behind a page, and nobody
      // has ever noticed the difference. It halves the fill cost.
      var w = Math.max(1, Math.round(host.clientWidth / 2));
      var h = Math.max(1, Math.round(host.clientHeight / 2));
      if (canvas.width === w && canvas.height === h) return;
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
      gl.uniform2f(u.uResolution, w, h);
    }
    new ResizeObserver(resize).observe(host);
    resize();

    host.appendChild(canvas);
    host.dataset.gl = 'on';

    function draw(t) {
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(u.uTime, (t * 0.01) * 0.5 * 0.1);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    if (still.matches) {
      // One frame, held. The shape is the decoration; the drift is the part
      // that makes people ill.
      resize();
      draw(0);
      return;
    }
    animate(draw);
  }

  /* =====================================================================
     2. ClickSpark
     A direct port. One canvas over the whole page, lines flying outward.
     ===================================================================== */

  function clickSpark() {
    if (still.matches) return;

    var canvas = document.createElement('canvas');
    canvas.className = 'fx-spark';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
    var ctx = canvas.getContext('2d');

    var SPARKS = 8, RADIUS = 15, SIZE = 10, MS = 400;
    var live = [];

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = innerWidth * dpr;
      canvas.height = innerHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    addEventListener('resize', resize);
    resize();

    addEventListener('pointerdown', function (e) {
      // Fixed positioning, so viewport coordinates are the canvas ones.
      var now = performance.now();
      for (var i = 0; i < SPARKS; i++) {
        live.push({ x: e.clientX, y: e.clientY,
                    angle: (2 * Math.PI * i) / SPARKS, at: now });
      }
      if (live.length === SPARKS) animate(draw);
    });

    var colour = '';
    function draw(now) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!live.length) return;
      if (!colour) {
        colour = getComputedStyle(document.documentElement)
          .getPropertyValue('--accent').trim() || '#a95cff';
      }
      ctx.strokeStyle = colour;
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';

      live = live.filter(function (s) {
        var p = (now - s.at) / MS;
        if (p >= 1) return false;
        var eased = p * (2 - p);
        var d = eased * RADIUS;
        var len = SIZE * (1 - eased);
        ctx.globalAlpha = 1 - eased;
        ctx.beginPath();
        ctx.moveTo(s.x + d * Math.cos(s.angle), s.y + d * Math.sin(s.angle));
        ctx.lineTo(s.x + (d + len) * Math.cos(s.angle),
                   s.y + (d + len) * Math.sin(s.angle));
        ctx.stroke();
        return true;
      });
      ctx.globalAlpha = 1;
    }

    // The theme can change under us; drop the cached colour when it does.
    new MutationObserver(function () { colour = ''; })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  /* =====================================================================
     3. FoldText
     The original drives a staggered 3D unfold with gsap. CSS does staggering
     with one custom property per character and an animation-delay, which is
     both smaller and runs off the main thread.
     ===================================================================== */

  var original = new WeakMap();

  function foldText(el) {
    if (still.matches) return;

    // Re-runnable, because switching language replaces the words. The clean
    // markup is kept so a second pass splits the new text rather than the
    // spans the first pass left behind.
    if (!original.has(el)) original.set(el, el.innerHTML);
    else el.innerHTML = original.get(el);

    var i = 0;

    function splitText(node) {
      var frag = document.createDocumentFragment();
      // Words, not raw characters. Every panel is an inline-block, and the
      // browser will happily break a line between two of them - which is how
      // "Orphans" ended up as "Orphan" and "s" on separate lines. Wrapping
      // each word puts the only legal break back where it belongs.
      node.nodeValue.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) {
          frag.appendChild(document.createTextNode(part));
          return;
        }
        var word = document.createElement("span");
        word.className = "fold-word";
        Array.from(part).forEach(function (ch) {
          var seg = document.createElement("span");
          seg.className = "fold-seg";
          seg.style.setProperty("--i", i++);
          seg.textContent = ch;
          word.appendChild(seg);
        });
        frag.appendChild(word);
      });
      node.parentNode.replaceChild(frag, node);
    }

    function walk(parent) {
      Array.prototype.slice.call(parent.childNodes).forEach(function (node) {
        if (node.nodeType === 3) {
          if (node.nodeValue.trim()) splitText(node);
          return;
        }
        if (node.nodeType !== 1) return;

        // An element painting its text with background-clip - the gradient
        // word in the headline - must not have its characters split out.
        // Each panel is transformed, which makes it its own painting context,
        // and the parent's clipped background cannot reach inside one. The
        // characters came out transparent and the word vanished. Folding the
        // whole element as a single panel keeps the gradient on the element
        // that owns it.
        var s = getComputedStyle(node);
        var clip = s.webkitBackgroundClip || s.backgroundClip;
        if (clip === "text") {
          node.classList.add("fold-seg", "fold-seg--whole");
          node.style.setProperty("--i", i++);
          return;
        }
        walk(node);
      });
    }

    walk(el);
    if (!el.querySelector(".fold-seg")) return;

    // Set straight away. The animation carries its own first frame through
    // `animation-fill-mode: both`, so there is no window in which the panels
    // are hidden by a rule that something still has to come along and lift.
    el.dataset.fold = "in";
  }

  /* =====================================================================
     4. SpecularButton
     The original gives every button its own WebGL context. Browsers cap the
     number of live contexts at around sixteen and drop the oldest without
     warning, so a page with several buttons plus the aurora would start
     losing them. The highlight is a bright arc travelling around a rounded
     rectangle, steered by the pointer - a conic gradient in a border mask
     does exactly that, on the compositor, for nothing.
     ===================================================================== */

  function specular() {
    var buttons = Array.prototype.slice.call(
      document.querySelectorAll('.btn--primary, [data-specular]'));
    if (!buttons.length || still.matches) return;

    buttons.forEach(function (b) { b.classList.add('is-specular'); });

    var PROXIMITY = 250;
    var state = buttons.map(function () { return { angle: 2.4, bright: 0 }; });
    var target = buttons.map(function () { return { angle: 2.4, bright: 0 }; });
    var last = performance.now();
    var dirty = false;

    addEventListener('pointermove', function (e) {
      buttons.forEach(function (b, i) {
        var r = b.getBoundingClientRect();
        if (!r.width) return;
        var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        var dx = Math.max(r.left - e.clientX, 0, e.clientX - r.right);
        var dy = Math.max(r.top - e.clientY, 0, e.clientY - r.bottom);
        var dist = Math.hypot(dx, dy);
        target[i].angle = Math.atan2(cy - e.clientY, e.clientX - cx);
        var t = Math.max(0, 1 - dist / PROXIMITY);
        target[i].bright = t * t * (3 - 2 * t);
      });
      if (!dirty) { dirty = true; animate(step); }
    }, { passive: true });

    function step(now) {
      var dt = Math.min((now - last) / 1000, 0.05);
      last = now;
      var moving = false;
      buttons.forEach(function (b, i) {
        var s = state[i], t = target[i];
        // Shortest way round, so the highlight never spins the long way.
        var diff = ((t.angle - s.angle + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
        s.angle += diff * (1 - Math.exp(-dt * 7));
        s.bright += (t.bright - s.bright) * (1 - Math.exp(-dt * 8));
        if (Math.abs(diff) > 0.001 || Math.abs(t.bright - s.bright) > 0.001) {
          moving = true;
        }
        // Screen coordinates run down, CSS angles run clockwise from north.
        b.style.setProperty('--sb-angle', (90 - s.angle * 180 / Math.PI) + 'deg');
        b.style.setProperty('--sb-bright', s.bright.toFixed(3));
      });
      if (!moving) {
        loops.splice(loops.indexOf(step), 1);
        dirty = false;
      }
    }
  }

  /* ---- boot ------------------------------------------------------------ */

  var host = document.querySelector('.aurora');
  if (host) aurora(host);
  specular();
  clickSpark();

  // The headline is a translated element, and i18n snapshots the English by
  // reading innerHTML at boot. Splitting it into a hundred spans before that
  // happens would put those spans in the snapshot, so the fold waits a turn -
  // deferred scripts have all run by then - and runs again after a switch.
  var folds = Array.prototype.slice.call(document.querySelectorAll('[data-fold]'));
  if (folds.length) {
    setTimeout(function () { folds.forEach(foldText); }, 0);
    document.addEventListener('rtmr:lang', function () {
      setTimeout(function () { folds.forEach(foldText); }, 0);
    });
  }
})();
