"""Optional browser verification: pip install playwright; requires local Edge.

Run from the course with its Python interpreter. No browser download, network
access, Jupyter server, or robot connection is required by this check.
"""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'assets/interactive/concept_player.html'
data = json.loads(re.search(r'const scenes=(.*?);const select=', path.read_text(encoding='utf-8'), re.S).group(1))
for scene in data:
    for svg_frame in scene['frames']:
        ET.fromstring(svg_frame)
out = ROOT / 'outputs/concept_player_check'
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1120})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(path.as_uri())
    assert page.locator('#position').inner_text() == '1 / 8'
    page.locator('#next').click()
    assert page.locator('#position').inner_text() == '2 / 8'
    page.locator('#prev').click()
    page.locator('#speed').select_option('200')
    page.locator('#play').click()
    page.wait_for_function("Number(document.querySelector('#step').value)>0")
    page.locator('#play').click()
    paused = page.locator('#step').input_value()
    page.wait_for_timeout(350)
    assert page.locator('#step').input_value() == paused
    for index, scene in enumerate(data):
        page.locator('#scene').select_option(str(index))
        assert page.locator('#step').input_value() == '0'
        page.locator('#step').focus()
        page.keyboard.press('End')
        assert page.locator('#step').input_value() == str(len(scene['frames']) - 1)
        assert page.locator('#next').is_disabled()
        assert '看哪里' in page.locator('#stage').text_content()
        page.screenshot(path=str(out / f'scene_{index}.png'))
    # Intermediate frames matter too: changing numeric labels can affect width.
    outside = page.evaluate('''() => {
        const failures = [], stage = document.querySelector('#stage');
        scenes.forEach((scene, sceneIndex) => scene.frames.forEach((svg, frameIndex) => {
            stage.innerHTML = svg;
            stage.querySelectorAll('text').forEach(node => {
                const b = node.getBBox();
                if (b.x < 0 || b.x + b.width > 1100 || b.y < 0 || b.y + b.height > 680)
                    failures.push({sceneIndex, frameIndex, text: node.textContent});
            });
        }));
        return failures;
    }''')
    assert not outside, outside
    assert not errors, errors
    browser.close()
report = {'scenes': len(data), 'frames': sum(len(s['frames']) for s in data),
          'svg_parse': 'passed', 'browser_step_play_pause_seek': 'passed',
          'all_frame_text_bounds': 'passed', 'javascript_errors': errors}
(out / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
