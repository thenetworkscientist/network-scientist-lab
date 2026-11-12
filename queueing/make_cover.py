"""Draws the article cover (house cover style: a warm illustrated scene, not a chart).
Canvas 1456 x 1048; everything important sits in the centre so 16:9, 1.91:1, 2:1, 3:2 and square crops keep it.
Run: python make_cover.py  (writes article_cover.png)
"""
import random, cairosvg
random.seed(4)
W,H=1456,1048
FLOOR=830
out=[]
a=out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('''<defs>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A2A2A"/><stop offset="0.75" stop-color="#5A3C32"/><stop offset="1" stop-color="#6A4636"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6B4430"/><stop offset="1" stop-color="#3A2418"/></linearGradient>
<linearGradient id="counter" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9A6440"/><stop offset="1" stop-color="#5E3A24"/></linearGradient>
<linearGradient id="street" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9CC6E8"/><stop offset="0.65" stop-color="#F6D9B4"/><stop offset="1" stop-color="#FBE6C6"/></linearGradient>
<linearGradient id="beam" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#FFE4A8" stop-opacity="0.38"/><stop offset="1" stop-color="#FFE4A8" stop-opacity="0"/></linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFC871" stop-opacity="0.55"/><stop offset="0.5" stop-color="#FFB35C" stop-opacity="0.16"/><stop offset="1" stop-color="#FFB35C" stop-opacity="0"/></radialGradient>
<radialGradient id="pool" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFD9A0" stop-opacity="0.35"/><stop offset="1" stop-color="#FFD9A0" stop-opacity="0"/></radialGradient>
<linearGradient id="vig" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#140D12" stop-opacity="0.55"/><stop offset="0.18" stop-color="#140D12" stop-opacity="0"/><stop offset="0.82" stop-color="#140D12" stop-opacity="0"/><stop offset="1" stop-color="#140D12" stop-opacity="0.5"/></linearGradient>
</defs>''')
# wall + floor
a(f'<rect width="{W}" height="{H}" fill="url(#wall)"/>')
# wainscot
a(f'<rect x="0" y="{FLOOR-128}" width="{W}" height="128" fill="#3B2622"/>')
a(f'<rect x="0" y="{FLOOR-132}" width="{W}" height="6" fill="#6E4A3A"/>')
a(f'<rect x="0" y="{FLOOR}" width="{W}" height="{H-FLOOR}" fill="url(#floor)"/>')
for i in range(0,W,92):
    a(f'<line x1="{i}" y1="{FLOOR}" x2="{i-60}" y2="{H}" stroke="#2C1A12" stroke-opacity="0.35" stroke-width="2"/>')

# door opening on the right: the line walks out into a cool street
DX0=1088
a(f'<rect x="{DX0}" y="270" width="{W-DX0}" height="{FLOOR-270}" fill="url(#street)"/>')
a(f'<rect x="{DX0}" y="{FLOOR}" width="{W-DX0}" height="{H-FLOOR}" fill="#C2AA86"/>')
a(f'<circle cx="{DX0+180}" cy="400" r="120" fill="#FFE7B0" opacity="0.35"/>')
a(f'<circle cx="{DX0+180}" cy="400" r="44" fill="#FFF4D6"/>')   # low morning sun, behind the buildings
for bx0,bw,bh in ((1088,70,300),(1166,90,240),(1262,60,330),(1330,110,210)):
    a(f'<rect x="{bx0}" y="{FLOOR-90-bh}" width="{bw}" height="{bh}" fill="#8EA6C2" opacity="0.75"/>')
    for wy in range(FLOOR-80-bh, FLOOR-110, 34):
        for wx in range(bx0+12, bx0+bw-12, 24):
            a(f'<rect x="{wx}" y="{wy}" width="9" height="12" fill="#C9DAEA" opacity="0.7"/>')
a(f'<rect x="{DX0}" y="{FLOOR-90}" width="{W-DX0}" height="90" fill="#A88F6E" opacity="0.55"/>')
a(f'<path d="M{DX0},{FLOOR} L{DX0},{FLOOR-40} L{DX0-520},{H} L{DX0},{H} Z" fill="url(#beam)"/>')
a('<g transform="translate(70,0)">')
# pendant lamps
for lx,ly in ((340,330),(480,300)):
    a(f'<circle cx="{lx}" cy="{ly+40}" r="260" fill="url(#glow)"/>')
    a(f'<line x1="{lx}" y1="0" x2="{lx}" y2="{ly}" stroke="#1A1216" stroke-width="3"/>')
    a(f'<path d="M{lx-34},{ly+34} Q{lx},{ly-6} {lx+34},{ly+34} Z" fill="#E8A34A"/>')
    a(f'<ellipse cx="{lx}" cy="{ly+34}" rx="34" ry="6" fill="#FFE2A8"/>')

# chalkboard menu
a('<rect x="112" y="240" width="190" height="150" rx="6" fill="#6E4A3A"/>')
a('<rect x="122" y="250" width="170" height="130" rx="3" fill="#232A26"/>')
for i,wd in enumerate((110,80,96,64,88)):
    a(f'<line x1="140" y1="{276+i*22}" x2="{140+wd}" y2="{276+i*22}" stroke="#E9E2D0" stroke-opacity="0.55" stroke-width="3" stroke-linecap="round"/>')
    a(f'<circle cx="{270}" cy="{276+i*22}" r="2.5" fill="#E9E2D0" opacity="0.55"/>')
# wall clock above the counter: almost no spare time left
cx,cy,r=470,440,58
a(f'<circle cx="{cx}" cy="{cy}" r="{r+8}" fill="#2A1E26" stroke="#C9A27A" stroke-width="5"/>')
a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#F6E7CF"/>')
import math
busy=0.9
ang=busy*2*math.pi
x2=cx+r*math.sin(ang); y2=cy-r*math.cos(ang)
a(f'<path d="M{cx},{cy} L{cx},{cy-r} A{r},{r} 0 1 1 {x2:.1f},{y2:.1f} Z" fill="#E8695A"/>')
for k in range(12):
    t=k/12*2*math.pi
    a(f'<line x1="{cx+(r-8)*math.sin(t):.1f}" y1="{cy-(r-8)*math.cos(t):.1f}" x2="{cx+(r-2)*math.sin(t):.1f}" y2="{cy-(r-2)*math.cos(t):.1f}" stroke="#2A1E26" stroke-width="2.5"/>')
a(f'<line x1="{cx}" y1="{cy}" x2="{cx+30*math.sin(ang):.1f}" y2="{cy-30*math.cos(ang):.1f}" stroke="#2A1E26" stroke-width="4" stroke-linecap="round"/>')
a(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-48}" stroke="#2A1E26" stroke-width="3" stroke-linecap="round"/>')
a(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#2A1E26"/>')

# barista behind the counter, drawn at the same scale as the customers (about 300 px tall)
TOP_C=FLOOR-128          # counter top: about waist height on a 300 px person
bx=360
bh=300; btop=FLOOR-bh; hr=bh*0.075; hy=btop+hr+4
a(f'<path d="M{bx-32},{TOP_C+6} L{bx-32},{btop+bh*0.3:.0f} Q{bx-32},{btop+bh*0.17:.0f} {bx},{btop+bh*0.16:.0f} Q{bx+32},{btop+bh*0.17:.0f} {bx+32},{btop+bh*0.3:.0f} L{bx+32},{TOP_C+6} Z" fill="#2F5E8C"/>')
a(f'<path d="M{bx-20},{btop+bh*0.3:.0f} L{bx+20},{btop+bh*0.3:.0f} L{bx+24},{TOP_C+6} L{bx-24},{TOP_C+6} Z" fill="#E7C08A"/>')
a(f'<rect x="{bx-5}" y="{btop+bh*0.12:.0f}" width="10" height="{bh*0.06:.0f}" fill="#B98563"/>')
a(f'<circle cx="{bx}" cy="{hy:.0f}" r="{hr:.0f}" fill="#C28E69"/>')
a(f'<path d="M{bx-hr*0.95:.0f},{hy-hr*0.1:.0f} Q{bx-hr:.0f},{hy-hr*1.15:.0f} {bx:.0f},{hy-hr*1.1:.0f} Q{bx+hr*1.1:.0f},{hy-hr*1.05:.0f} {bx+hr:.0f},{hy-hr*0.15:.0f} Q{bx+hr*0.5:.0f},{hy-hr*0.6:.0f} {bx-hr*0.2:.0f},{hy-hr*0.45:.0f} Q{bx-hr*0.7:.0f},{hy-hr*0.4:.0f} {bx-hr*0.95:.0f},{hy-hr*0.1:.0f} Z" fill="#2A1A14"/>')
a(f'<circle cx="{bx+hr*0.85:.0f}" cy="{hy-hr*0.8:.0f}" r="{hr*0.35:.0f}" fill="#2A1A14"/>')
sh=btop+bh*0.24
a(f'<path d="M{bx-28},{sh:.0f} Q{bx-62},{sh+40:.0f} {bx-96},{TOP_C-22}" stroke="#2F5E8C" stroke-width="14" fill="none" stroke-linecap="round"/>')
a(f'<circle cx="{bx-99}" cy="{TOP_C-20}" r="8" fill="#C28E69"/>')
a(f'<path d="M{bx+28},{sh:.0f} Q{bx+60},{sh+44:.0f} {bx+92},{TOP_C-12}" stroke="#2F5E8C" stroke-width="14" fill="none" stroke-linecap="round"/>')
a(f'<circle cx="{bx+95}" cy="{TOP_C-11}" r="8" fill="#C28E69"/>')
for d in (0,12,24):
    a(f'<path d="M{bx+112},{TOP_C-34-d} q10,-8 20,0" stroke="#FFE2A8" stroke-opacity="{0.5-d/70:.2f}" stroke-width="3" fill="none" stroke-linecap="round"/>')

# counter at waist height
a(f'<rect x="100" y="{TOP_C+10}" width="560" height="{FLOOR-TOP_C-10}" fill="url(#counter)"/>')
a(f'<rect x="88" y="{TOP_C}" width="584" height="14" rx="4" fill="#C08355"/>')
a(f'<circle cx="380" cy="{TOP_C+40}" r="180" fill="url(#pool)"/>')
# espresso machine, sized to the barista
mx, mw, mh = 150, 112, 86
a(f'<rect x="{mx}" y="{TOP_C-mh}" width="{mw}" height="{mh}" rx="9" fill="#A3ACB7"/>')
a(f'<rect x="{mx}" y="{TOP_C-mh}" width="{mw}" height="16" rx="8" fill="#D3D9E0"/>')
a(f'<rect x="{mx+14}" y="{TOP_C-mh+30}" width="{mw-28}" height="10" rx="4" fill="#5E6670"/>')
for gx in (mx+34, mx+76):
    a(f'<rect x="{gx-8}" y="{TOP_C-mh+40}" width="16" height="11" rx="3" fill="#4A515A"/>')
    a(f'<rect x="{gx-3}" y="{TOP_C-mh+46}" width="26" height="6" rx="3" fill="#2A2630"/>')
a(f'<path d="M{mx+28},{TOP_C} L{mx+40},{TOP_C} L{mx+38},{TOP_C-15} L{mx+30},{TOP_C-15} Z" fill="#F6E7CF"/>')
for sx in (mx+34, mx+76):
    a(f'<path d="M{sx},{TOP_C-mh-8} q-10,-16 0,-30 q10,-14 0,-28" stroke="#FFF3DD" stroke-opacity="0.4" stroke-width="4" fill="none" stroke-linecap="round"/>')
# orders waiting on the counter
for i,col in enumerate(["#F6E7CF","#F2B33D","#F6E7CF","#E8695A","#F6E7CF"]):
    x=466+i*20
    a(f'<path d="M{x},{TOP_C} L{x+14},{TOP_C} L{x+12},{TOP_C-20} L{x+2},{TOP_C-20} Z" fill="{col}"/>')
    a(f'<rect x="{x}" y="{TOP_C-23}" width="14" height="5" rx="2" fill="#FFFFFF" opacity="0.9"/>')
a('</g>')
# the line of customers, curling toward and out of the door
coats=["#E8695A","#3B7DD8","#F2B33D","#6C8A6E","#8E5C7A","#D9A066","#4F6D8F","#B24C46","#7A8899","#C9A27A","#5B4A6E"]
skins=["#C28E69","#8D5B3E","#E2B48F","#A8714E","#6B4430","#D7A27C"]
hairs=["#2A1A14","#5A3A24","#1A1216","#8A6A4A","#3A2A20"]
def person(x, h, coat, skin, hair, cool=False, bag=False, phone=False):
    top=FLOOR-h
    head_r=h*0.075
    hy=top+head_r
    sw=h*random.choice([0.18,0.2,0.22])
    a(f'<ellipse cx="{x}" cy="{FLOOR+4}" rx="{sw*0.9:.1f}" ry="7" fill="#000" opacity="0.25"/>')
    # legs
    a(f'<rect x="{x-sw*0.32:.1f}" y="{top+h*0.62:.1f}" width="{sw*0.26:.1f}" height="{h*0.38:.1f}" rx="5" fill="#2A2630"/>')
    a(f'<rect x="{x+sw*0.06:.1f}" y="{top+h*0.62:.1f}" width="{sw*0.26:.1f}" height="{h*0.38:.1f}" rx="5" fill="#2A2630"/>')
    # coat
    a(f'<path d="M{x-sw/2:.1f},{top+h*0.68:.1f} L{x-sw/2:.1f},{top+h*0.3:.1f} Q{x-sw/2:.1f},{top+h*0.17:.1f} {x:.1f},{top+h*0.16:.1f} Q{x+sw/2:.1f},{top+h*0.17:.1f} {x+sw/2:.1f},{top+h*0.3:.1f} L{x+sw/2:.1f},{top+h*0.68:.1f} Z" fill="{coat}"/>')
    a(f'<rect x="{x-5:.1f}" y="{top+h*0.13:.1f}" width="10" height="{h*0.05:.1f}" fill="{skin}"/>')
    a(f'<circle cx="{x:.1f}" cy="{hy+h*0.02:.1f}" r="{head_r:.1f}" fill="{skin}"/>')
    a(f'<path d="M{x-head_r*0.7:.1f},{hy-head_r*0.6:.1f} Q{x:.1f},{hy-head_r*1.2:.1f} {x+head_r*0.95:.1f},{hy-head_r*0.3:.1f} Q{x+head_r*1.15:.1f},{hy+head_r*0.6:.1f} {x+head_r*0.55:.1f},{hy+head_r*1.05:.1f} Q{x+head_r*0.2:.1f},{hy+head_r*0.2:.1f} {x-head_r*0.2:.1f},{hy-head_r*0.25:.1f} Q{x-head_r*0.6:.1f},{hy-head_r*0.15:.1f} {x-head_r*0.7:.1f},{hy-head_r*0.6:.1f} Z" fill="{hair}"/>')
    a(f'<circle cx="{x-head_r*0.85:.1f}" cy="{hy+head_r*0.15:.1f}" r="{head_r*0.18:.1f}" fill="{skin}"/>')
    if bag:
        a(f'<rect x="{x+sw/2-4:.1f}" y="{top+h*0.45:.1f}" width="{sw*0.4:.1f}" height="{sw*0.45:.1f}" rx="6" fill="#3A2A20"/>')
    if phone:
        a(f'<rect x="{x-sw*0.15:.1f}" y="{top+h*0.33:.1f}" width="{sw*0.22:.1f}" height="{sw*0.32:.1f}" rx="3" fill="#A9D2FF" opacity="0.9"/>')
    if cool:
        pass
xs=[668,724,780,836,892,948,1004,1060]
for i,x in enumerate(xs):
    h=random.choice([282,292,300,308,316,276])
    person(x,h,coats[i%len(coats)],random.choice(skins),random.choice(hairs),bag=(i%3==1),phone=(i%4==2))
# in the doorway and outside: cooler, dimmer
outside=[1118,1178,1238,1298,1358,1418]
for i,x in enumerate(outside):
    h=random.choice([282,292,300,308,276])
    person(x,h,coats[(i+3)%len(coats)],random.choice(skins),random.choice(hairs),phone=(i%2==0))
a(f'<rect x="{DX0}" y="270" width="{W-DX0}" height="{FLOOR-270+8}" fill="#FFF0D6" opacity="0.22"/>')
# door frame on top so people pass through it
a(f'<rect x="{DX0-16}" y="256" width="16" height="{FLOOR-256}" fill="#7A5240"/>')
a(f'<rect x="{DX0-16}" y="256" width="{W-DX0+16}" height="16" fill="#7A5240"/>')
# headline
a('<text x="1206" y="252" text-anchor="end" font-family="Inter Display, Inter, sans-serif" font-weight="800" font-size="64" fill="#FBEFDD" letter-spacing="-1">Busy isn\u2019t efficient.</text>')
a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
a('</svg>')
open('_cover.svg','w').write("\n".join(out))
cairosvg.svg2png(url='_cover.svg', write_to='_cover_raw.png', output_width=W, output_height=H)
# soft film grain for warmth
import numpy as np
from PIL import Image
im=np.asarray(Image.open('_cover_raw.png').convert('RGB')).astype(np.float32)
rng=np.random.default_rng(1); n=rng.normal(0,5.5,im.shape[:2])[...,None]
Image.fromarray(np.clip(im+n,0,255).astype(np.uint8)).save('article_cover.png')
import os; os.remove('_cover.svg'); os.remove('_cover_raw.png'); print('article_cover.png written')
