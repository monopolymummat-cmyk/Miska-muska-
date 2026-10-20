const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function render3DVideo({ sceneConfig, outputFramesDir, fps = 30, duration = 6, width = 1080, height = 1920 }) {
  console.log(`[Renderer] Starting 3D WebGL frame rendering (${width}x${height} @ ${fps} fps)...`);

  if (!fs.existsSync(outputFramesDir)) {
    fs.mkdirSync(outputFramesDir, { recursive: true });
  }

  const htmlPath = 'file://' + path.resolve(__dirname, 'index.html');

  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--use-gl=angle',
      '--use-angle=gl-egl',
      '--ignore-gpu-blocklist',
      '--enable-gpu-rasterization'
    ]
  });

  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 1
  });

  await page.goto(htmlPath);
  await page.waitForTimeout(1000); // Wait for Three.js initialization

  // Inject Scene Config into browser
  await page.evaluate((config) => {
    window.loadSceneConfig(config);
  }, sceneConfig);

  const totalFrames = Math.floor(duration * fps);
  console.log(`[Renderer] Rendering ${totalFrames} frames for ${duration}s video...`);

  for (let frame = 0; frame < totalFrames; frame++) {
    const timeInSeconds = frame / fps;

    // Trigger window frame render
    await page.evaluate(({ t, dur }) => {
      window.renderFrameAtTime(t, dur);
    }, { t: timeInSeconds, dur: duration });

    const frameNumStr = String(frame + 1).padStart(5, '0');
    const framePath = path.join(outputFramesDir, `frame_${frameNumStr}.png`);

    await page.screenshot({
      path: framePath,
      type: 'png',
      omitBackground: false
    });

    if ((frame + 1) % 30 === 0 || frame === totalFrames - 1) {
      console.log(`[Renderer] Rendered frame ${frame + 1}/${totalFrames} (${Math.round(((frame + 1) / totalFrames) * 100)}%)`);
    }
  }

  await browser.close();
  console.log(`[Renderer] Completed rendering ${totalFrames} frames to ${outputFramesDir}`);
}

module.exports = { render3DVideo };
