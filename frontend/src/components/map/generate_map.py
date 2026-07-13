import re
import os

svg_path = r"c:\Users\shakt\Downloads\Hack2skill\frontend\src\assets\stadium.svg"
out_path = r"c:\Users\shakt\Downloads\Hack2skill\frontend\src\components\map\StadiumMap.tsx"

with open(svg_path, 'r', encoding='utf-8') as f:
    svg_content = f.read()

# Convert common SVG attributes to camelCase
replacements = {
    'class=': 'className=',
    'stroke-width=': 'strokeWidth=',
    'stroke-dasharray=': 'strokeDasharray=',
    'stroke-linecap=': 'strokeLinecap=',
    'stroke-linejoin=': 'strokeLinejoin=',
    'dominant-baseline=': 'dominantBaseline=',
    'text-anchor=': 'textAnchor=',
    'fill-opacity=': 'fillOpacity=',
    'stop-color=': 'stopColor=',
    'font-family=': 'fontFamily=',
    'font-size=': 'fontSize=',
    'font-weight=': 'fontWeight=',
    'letter-spacing=': 'letterSpacing=',
    'text-transform=': 'textTransform=',
}

for k, v in replacements.items():
    svg_content = svg_content.replace(k, v)

# The <style> tag in React needs to be dangerouslySetInnerHTML or removed and put in CSS.
# Let's extract the style content and put it in a separate CSS file.
style_match = re.search(r'<style>(.*?)</style>', svg_content, re.DOTALL)
if style_match:
    style_content = style_match.group(1)
    css_path = r"c:\Users\shakt\Downloads\Hack2skill\frontend\src\components\map\StadiumMap.css"
    os.makedirs(os.path.dirname(css_path), exist_ok=True)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(style_content)
    svg_content = re.sub(r'<style>.*?</style>', '', svg_content, flags=re.DOTALL)

# Insert React dynamic parts
# Replace the route-overlay and fan-marker with React children/props logic
# Actually, just wrapping the SVG in a component is enough for Phase 3 initially.

react_code = f"""import React from 'react';
import './StadiumMap.css';

interface StadiumMapProps {{
  className?: string;
  selectedSection?: string;
  onSectionClick?: (sectionId: string) => void;
  fanSeat?: {{ x: number, y: number }};
  egressRoute?: {{ x: number, y: number }}[];
}}

export const StadiumMap: React.FC<StadiumMapProps> = ({{ className, selectedSection, onSectionClick, fanSeat, egressRoute }}) => {{
  return (
    <div className={{`relative w-full h-full max-w-[800px] max-h-[800px] aspect-square drop-shadow-[0_0_25px_rgba(34,197,94,0.1)] ${{className || ''}}`}}>
      {svg_content.replace('<?xml version="1.0" encoding="UTF-8"?>', '')}
    </div>
  );
}};
"""

# Modify the sections to add onClick and dynamic classes
sections = ['n1', 'n2', 'e1', 'e2', 's2', 's1', 'w2', 'w1']
for s in sections:
    section_id = f'section-{s}'
    old_tag = f'id="{section_id}" className="section"'
    new_tag = f'id="{section_id}" className={{`section ${{selectedSection === "{section_id}" ? "selected" : ""}}`}} onClick={{() => onSectionClick?.("{section_id}")}}'
    react_code = react_code.replace(old_tag, new_tag)

# Add dynamic overlays
route_replacement = """  <g id="route-overlay">
    {egressRoute && egressRoute.length > 0 && (
      <polyline 
        points={egressRoute.map(p => `${p.x},${p.y}`).join(' ')} 
        className="route-path animate-pulse"
      />
    )}
  </g>"""
react_code = re.sub(r'<g id="route-overlay">\s*<!--.*?-->\s*</g>', route_replacement, react_code, flags=re.DOTALL)

fan_marker_replacement = """  <g id="fan-marker">
    {fanSeat && (
      <circle className="seat-pulse" cx={fanSeat.x} cy={fanSeat.y} r="7" fill="#22c55e" filter="url(#glow-green)"/>
    )}
  </g>"""
react_code = re.sub(r'<g id="fan-marker">\s*<!--.*?-->\s*</g>', fan_marker_replacement, react_code, flags=re.DOTALL)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(react_code)

print("Successfully generated StadiumMap.tsx and StadiumMap.css")
