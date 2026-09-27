"""peacock_dance.py — Safe peacock dance via iframe."""
import streamlit.components.v1 as components

HTML = """
<!DOCTYPE html><html><head><style>
body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:Arial,sans-serif}
.stage{position:relative;width:100%;height:220px;display:flex;align-items:center;justify-content:center}
.peacock{position:relative;width:160px;height:160px;animation:danceSway 3s ease-in-out infinite}
@keyframes danceSway{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-12px) rotate(3deg)}}
.body{position:absolute;left:50%;bottom:0;width:50px;height:60px;margin-left:-25px;background:linear-gradient(180deg,#0066cc 0%,#00a86b 100%);border-radius:50% 50% 40% 40%;box-shadow:0 0 20px rgba(0,212,255,0.6);z-index:3}
.body::before{content:'';position:absolute;top:-25px;left:50%;width:14px;height:30px;margin-left:-7px;background:linear-gradient(180deg,#0077dd 0%,#0066cc 100%);border-radius:7px;animation:neckBob 1.5s ease-in-out infinite}
@keyframes neckBob{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
.body::after{content:'';position:absolute;top:-38px;left:50%;width:18px;height:18px;margin-left:-9px;background:radial-gradient(circle at 40% 40%,#00d4ff,#0066cc);border-radius:50%;box-shadow:0 0 12px rgba(0,212,255,0.9)}
.feathers{position:absolute;left:50%;bottom:40px;width:0;height:0;z-index:2}
.feather{position:absolute;left:0;bottom:0;width:4px;height:100px;background:linear-gradient(180deg,transparent 0%,#00a86b 20%,#0066cc 60%,#00d4ff 100%);transform-origin:bottom center;border-radius:2px;animation:featherWave 2s ease-in-out infinite}
.f1{transform:rotate(-80deg);animation-delay:0s}
.f2{transform:rotate(-70deg);animation-delay:0.1s}
.f3{transform:rotate(-60deg);animation-delay:0.2s}
.f4{transform:rotate(-50deg);animation-delay:0.3s}
.f5{transform:rotate(-40deg);animation-delay:0.4s}
.f6{transform:rotate(-30deg);animation-delay:0.5s}
.f7{transform:rotate(-20deg);animation-delay:0.6s}
.f8{transform:rotate(-10deg);animation-delay:0.7s}
.f9{transform:rotate(0deg);animation-delay:0.8s}
.f10{transform:rotate(10deg);animation-delay:0.7s}
.f11{transform:rotate(20deg);animation-delay:0.6s}
.f12{transform:rotate(30deg);animation-delay:0.5s}
.f13{transform:rotate(40deg);animation-delay:0.4s}
.f14{transform:rotate(50deg);animation-delay:0.3s}
.f15{transform:rotate(60deg);animation-delay:0.2s}
.f16{transform:rotate(70deg);animation-delay:0.1s}
.f17{transform:rotate(80deg);animation-delay:0s}
@keyframes featherWave{0%,100%{filter:brightness(1) hue-rotate(0deg)}50%{filter:brightness(1.5) hue-rotate(30deg)}}
.feather::before{content:'';position:absolute;top:10px;left:50%;width:14px;height:14px;margin-left:-7px;background:radial-gradient(circle,#ffb547 0%,#00a86b 40%,#0066cc 70%,transparent 100%);border-radius:50%;box-shadow:0 0 8px rgba(255,181,71,0.8);opacity:0.9}
.sparkle{position:absolute;width:4px;height:4px;border-radius:50%;background:#ffb547;box-shadow:0 0 8px #ffb547;opacity:0;animation:sparkleFloat 3s ease-out infinite}
.s1{left:20%;top:60%;animation-delay:0s}
.s2{left:30%;top:40%;animation-delay:0.5s}
.s3{left:70%;top:50%;animation-delay:1s}
.s4{left:80%;top:30%;animation-delay:1.5s}
.s5{left:50%;top:20%;animation-delay:2s}
@keyframes sparkleFloat{0%{opacity:0;transform:translateY(0) scale(0.5)}30%{opacity:1;transform:translateY(-20px) scale(1)}100%{opacity:0;transform:translateY(-50px) scale(0)}}
.shadow{position:absolute;bottom:10px;left:50%;width:100px;height:12px;margin-left:-50px;background:radial-gradient(ellipse,rgba(0,212,255,0.5) 0%,transparent 70%);animation:shadowPulse 3s ease-in-out infinite}
@keyframes shadowPulse{0%,100%{transform:scaleX(1);opacity:0.6}50%{transform:scaleX(0.7);opacity:0.3}}
</style></head><body>
<div class="stage"><div class="peacock">
<div class="feathers">
<div class="feather f1"></div><div class="feather f2"></div><div class="feather f3"></div><div class="feather f4"></div><div class="feather f5"></div><div class="feather f6"></div><div class="feather f7"></div><div class="feather f8"></div><div class="feather f9"></div><div class="feather f10"></div><div class="feather f11"></div><div class="feather f12"></div><div class="feather f13"></div><div class="feather f14"></div><div class="feather f15"></div><div class="feather f16"></div><div class="feather f17"></div>
</div>
<div class="body"></div><div class="shadow"></div>
<div class="sparkle s1"></div><div class="sparkle s2"></div><div class="sparkle s3"></div><div class="sparkle s4"></div><div class="sparkle s5"></div>
</div></div></body></html>
"""

def show_peacock_dance(height=220):
    components.html(HTML, height=height, scrolling=False)
