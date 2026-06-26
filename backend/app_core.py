# app_core.py - النسخة النهائية مع إصلاح جميع المشاكل

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import rasterio
from pyproj import Transformer
import os
import io
import base64
from urllib.parse import quote
import qrcode
from PIL import Image as PILImage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== مسار مجلد geodata ====================
GEO_DATA_PATH = r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata"

# ==================== بيانات الأنواع ====================
SPECIES_DATA = {
    "Aptitude_Finale_Acacia_spp": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Acacia_spp_Fixed.tif"),
        "arabic_name": "الأكاسيا",
        "latin_name": "Acacia spp"
    },
    "Aptitude_Finale_Atriplex_spp": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Atriplex_spp_Fixed.tif"),
        "arabic_name": "القطف",
        "latin_name": "Atriplex spp"
    },
    "Aptitude_Finale_Ceratonia_siliqua": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Ceratonia_siliqua_Fixed.tif"),
        "arabic_name": "الخروب",
        "latin_name": "Ceratonia siliqua"
    },
    "Aptitude_Finale_Ficus_carica": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Ficus_carica_Fixed.tif"),
        "arabic_name": "التين",
        "latin_name": "Ficus carica"
    },
    "Aptitude_Finale_Olea_europaea": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Olea_europaea_Fixed.tif"),
        "arabic_name": "الزيتون",
        "latin_name": "Olea europaea"
    },
    "Aptitude_Finale_Opuntia_ficus-indica": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Opuntia_ficus-indica_Fixed.tif"),
        "arabic_name": "التين الشوكي",
        "latin_name": "Opuntia ficus-indica"
    },
    "Aptitude_Finale_Pistacia_atlantica": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Pistacia_atlantica_Fixed.tif"),
        "arabic_name": "البطوم",
        "latin_name": "Pistacia atlantica"
    },
    "Aptitude_Finale_Prunus_armeniaca": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Prunus_armeniaca_Fixed.tif"),
        "arabic_name": "المشمش",
        "latin_name": "Prunus armeniaca"
    },
    "Aptitude_Finale_Prunus_dulcis": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Prunus_dulcis_Fixed.tif"),
        "arabic_name": "اللوز",
        "latin_name": "Prunus dulcis"
    },
    "Aptitude_Finale_Punica_granatum": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Punica_granatum_Fixed.tif"),
        "arabic_name": "الرمان",
        "latin_name": "Punica granatum"
    },
    "Aptitude_Finale_Ziziphus_lotus": {
        "raster": os.path.join(GEO_DATA_PATH, "Aptitude_Finale_Ziziphus_lotus_Fixed.tif"),
        "arabic_name": "السدر",
        "latin_name": "Ziziphus lotus"
    }
}

# محول الإحداثيات
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)

def get_classification(value):
    """إرجاع التصنيف واللون المناسب"""
    if value >= 3.8:
        return "ممتازة جداً", "#10b981"
    elif value >= 3.2:
        return "ممتازة", "#34d399"
    elif value >= 2.5:
        return "جيدة", "#f59e0b"
    elif value >= 1.8:
        return "متوسطة", "#f97316"
    else:
        return "ضعيفة", "#ef4444"

def get_raster_value(lat, lng, species_id):
    raster_path = SPECIES_DATA[species_id]["raster"]
    if not os.path.exists(raster_path):
        return 0
    try:
        x, y = transformer.transform(lng, lat)
        with rasterio.open(raster_path) as src:
            row, col = src.index(x, y)
            if row < 0 or row >= src.height or col < 0 or col >= src.width:
                return 0
            value = src.read(1)[row, col]
            if value == 0 or value == src.nodata:
                return 0
            return float(value)
    except:
        return 0

# ==================== دالة إنشاء QR Code ====================
def generate_qr_code(data):
    """إنشاء QR Code كصورة base64"""
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#064e3b", back_color="white")
        
        # تحويل إلى base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    except:
        return None

class AnalyzeRequest(BaseModel):
    lat: float
    lng: float
    species_id: str

class ChatRequest(BaseModel):
    query: str

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    value = get_raster_value(request.lat, request.lng, request.species_id)
    if value == 0:
        raise HTTPException(status_code=400, detail="الموقع خارج منطقة الدراسة")
    species = SPECIES_DATA[request.species_id]
    classification, color = get_classification(value)
    return {
        "status": "success",
        "species": {
            "id": request.species_id,
            "arabic_name": species["arabic_name"],
            "latin_name": species["latin_name"]
        },
        "coordinates": {"lat": request.lat, "lng": request.lng},
        "suitability": {
            "value": value,
            "classification": classification,
            "color": color
        }
    }

@app.get("/api/analyze")
async def analyze_get(lat: float, lng: float, species_id: str):
    value = get_raster_value(lat, lng, species_id)
    if value == 0:
        raise HTTPException(status_code=400, detail="الموقع خارج منطقة الدراسة")
    species = SPECIES_DATA[species_id]
    classification, color = get_classification(value)
    return {
        "status": "success",
        "species": {
            "id": species_id,
            "arabic_name": species["arabic_name"],
            "latin_name": species["latin_name"]
        },
        "coordinates": {"lat": lat, "lng": lng},
        "suitability": {
            "value": value,
            "classification": classification,
            "color": color
        }
    }

@app.get("/api/species")
async def list_species():
    species_list = []
    for sid, info in SPECIES_DATA.items():
        species_list.append({
            "id": sid,
            "arabic_name": info["arabic_name"],
            "latin_name": info["latin_name"]
        })
    return {"status": "success", "count": len(species_list), "species": species_list}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "species_count": len(SPECIES_DATA), "server_time": datetime.now().isoformat()}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    query = request.query.lower()
    if "اكاسيا" in query:
        reply = "الأكاسيا مناسبة للمناطق شبه القاحلة، تتحمل الجفاف وتثبت النيتروجين في التربة."
    elif "زيتون" in query:
        reply = "الزيتون ممتاز في مناطق خنشلة، يحتاج ري تكميلي في السنوات الأولى."
    elif "خروب" in query:
        reply = "الخروب شجرة مقاومة للجفاف، ملاءمتها عالية في المناطق الجبلية."
    else:
        reply = "أنا مساعد Mod-Space. اسأل عن الأكاسيا، الزيتون، الخروب، التين، الرمان، أو اللوز"
    return {"reply": reply}

# ==================== تقرير HTML ====================
@app.post("/api/generate-report")
async def generate_report(request: AnalyzeRequest):
    value = get_raster_value(request.lat, request.lng, request.species_id)
    if value == 0:
        raise HTTPException(status_code=400, detail="لا توجد بيانات في هذا الموقع")
    
    species = SPECIES_DATA[request.species_id]
    classification, color = get_classification(value)
    percent = round((value / 4.0) * 100, 1)
    report_id = f"MS-{datetime.now().strftime('%Y%m%d%H%M')}"
    report_date = datetime.now().strftime('%Y-%m-%d')
    report_time = datetime.now().strftime('%H:%M')
    
    # إنشاء QR Code
    qr_url = f"https://mod-space.com/report/{report_id}"
    qr_img = generate_qr_code(qr_url)
    
    if value >= 3.5:
        recommendation = f"يُوصى بشدة بزراعة {species['arabic_name']} في هذا الموقع. الظروف البيئية مثالية للاستثمار الزراعي."
    elif value >= 2.5:
        recommendation = f"يُوصى بزراعة {species['arabic_name']} مع تحسين التربة واعتماد نظام ري تكميلي."
    else:
        recommendation = f"لا يُوصى بزراعة {species['arabic_name']} في هذا الموقع. يُنصح باختيار أنواع أخرى أكثر تحملاً."

    # إنشاء QR Code HTML
    qr_html = f'<img src="{qr_img}" width="80" height="80" alt="QR Code">' if qr_img else '<div class="qr-placeholder">◼◼◼ QR ◼◼◼</div>'

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير Mod-Space</title>
        <style>
            @page {{
                size: A4;
                margin: 1.5cm;
            }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
                background: white;
                color: #1e293b;
                line-height: 1.5;
            }}
            .report {{
                max-width: 100%;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #064e3b;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .logo {{
                font-size: 24px;
                font-weight: bold;
                color: #064e3b;
            }}
            .logo span {{
                color: #10b981;
            }}
            .subtitle {{
                font-size: 12px;
                color: #047857;
                margin-top: 5px;
            }}
            .report-title {{
                font-size: 18px;
                font-weight: bold;
                color: #064e3b;
                margin: 15px 0 8px;
            }}
            .report-id {{
                font-size: 10px;
                color: #64748b;
            }}
            .two-columns {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .column {{
                flex: 1;
            }}
            .info-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                height: 100%;
            }}
            .card-title {{
                font-size: 14px;
                font-weight: bold;
                color: #064e3b;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 8px;
                margin-bottom: 12px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .info-table td {{
                padding: 6px 0;
                border-bottom: 1px solid #e2e8f0;
                font-size: 11px;
            }}
            .info-table td:first-child {{
                width: 40%;
                font-weight: bold;
                color: #475569;
            }}
            .mini-map {{
                background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
                height: 160px;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: #475569;
            }}
            .map-marker {{
                font-size: 32px;
                margin-bottom: 8px;
            }}
            .score-card {{
                background: {color};
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .score-value {{
                font-size: 52px;
                font-weight: bold;
                color: white;
            }}
            .score-label {{
                font-size: 14px;
                color: rgba(255,255,255,0.9);
                margin-top: 8px;
            }}
            .results-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .results-table th {{
                background: #064e3b;
                color: white;
                padding: 10px;
                font-size: 12px;
            }}
            .results-table td {{
                border: 1px solid #e2e8f0;
                padding: 10px;
                text-align: center;
                font-size: 12px;
            }}
            .recommendation-box {{
                background: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .recommendation-title {{
                font-weight: bold;
                margin-bottom: 8px;
                color: #064e3b;
            }}
            .qr-section {{
                text-align: center;
                padding: 15px;
                background: #f8fafc;
                border-radius: 12px;
                margin-bottom: 20px;
            }}
            .footer {{
                text-align: center;
                font-size: 9px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
                padding-top: 15px;
                margin-top: 10px;
            }}
            @media print {{
                body {{ margin: 0; padding: 0; }}
                .no-print {{ display: none; }}
            }}
            .print-btn {{
                background: #064e3b;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 12px;
                margin-bottom: 15px;
                display: inline-block;
            }}
            .print-btn:hover {{
                background: #047857;
            }}
        </style>
    </head>
    <body>
        <div class="report">
            <div style="text-align: left; margin-bottom: 15px;">
                <button onclick="window.print();" class="print-btn no-print">🖨️ طباعة التقرير / حفظ PDF</button>
            </div>
            
            <div class="header">
                <div class="logo">Mod-<span>Space</span></div>
                <div class="subtitle">نظام التحليل المكاني الذكي</div>
                <div class="report-title">تقرير تقييم الملاءمة الزراعية</div>
                <div class="report-id">رقم التقرير: {report_id} | تاريخ الإصدار: {report_date}</div>
            </div>
            
            <div class="two-columns">
                <div class="column">
                    <div class="info-card">
                        <div class="card-title">معلومات الموقع</div>
                        <table class="info-table">
                            <tr><td>الإحداثيات</td><td>{request.lat:.6f}°, {request.lng:.6f}°</td></tr>
                            <tr><td>الولاية</td><td>خنشلة</td></tr>
                            <tr><td>البلدية</td><td>خنشلة</td></tr>
                            <tr><td>الارتفاع</td><td>850 - 1200 متر</td></tr>
                            <tr><td>نوع التربة</td><td>كلسية - طميية</td></tr>
                            <tr><td>الانحدار</td><td>5 - 15 %</td></tr>
                        </table>
                    </div>
                </div>
                <div class="column">
                    <div class="info-card">
                        <div class="card-title">خريطة الموقع</div>
                        <div class="mini-map">
                            <div class="map-marker">🗺️ 📍</div>
                            <div>موقع {species['arabic_name']}</div>
                            <div style="font-size: 10px; margin-top: 5px;">{request.lat:.4f}°, {request.lng:.4f}°</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="score-card">
                <div class="score-value">{percent}%</div>
                <div class="score-label">نسبة الملاءمة الزراعية</div>
            </div>
            
            <table class="results-table">
                <thead>
                    <tr><th>النوع الشجري</th><th>الدرجة</th><th>التصنيف</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{species['arabic_name']}<br><span style="font-size:10px; color:#64748b;">{species['latin_name']}</span></td>
                        <td>{value:.1f} / 4.0</td>
                        <td style="color:{color}; font-weight:bold;">{classification}</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="recommendation-box">
                <div class="recommendation-title">📋 التوصيات الزراعية</div>
                <div>{recommendation}</div>
            </div>
            
            <div class="qr-section">
                {qr_html}
                <div style="font-size: 9px; margin-top: 5px;">{qr_url}</div>
            </div>
            
            <div class="footer">
                إعداد وتطوير وإشراف: محمد الأمين أم هاني | بمساعدة: رضوان حموته<br>
                جميع الحقوق محفوظة © منصة Mod-Space
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, media_type="text/html")

@app.get("/api/generate-report")
async def generate_report_get(lat: float, lng: float, species_id: str):
    """توليد تقرير HTML (طريقة GET)"""
    request = AnalyzeRequest(lat=lat, lng=lng, species_id=species_id)
    return await generate_report(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)