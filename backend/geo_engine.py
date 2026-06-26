# geo_engine.py
# محرك تحليل ملفات Raster

import rasterio
from pyproj import Transformer
from species_manager import get_raster_path, classify_suitability

# تحويل الإحداثيات من WGS84 إلى UTM Zone 32N
transformer = Transformer.from_crs(
    "EPSG:4326",      # WGS84 (خط الطول والعرض)
    "EPSG:32632",     # UTM Zone 32N (مناسب لشمال أفريقيا)
    always_xy=True
)

def extract_value(lat, lng, species_id):
    """
    استخراج قيمة الملاءمة من ملف Raster
    
    المعاملات:
        lat: خط العرض
        lng: خط الطول
        species_id: معرف النوع (مثال: "Acacia_spp")
    
    المخرجات:
        dict: يحتوي على القيمة والتصنيف واللون
    """
    
    # 1. الحصول على مسار ملف Raster
    raster_path = get_raster_path(species_id)
    
    if not raster_path:
        raise Exception(f"لا يوجد ملف Raster للنوع: {species_id}")
    
    # 2. تحويل الإحداثيات من (lat, lng) إلى (x, y)
    x, y = transformer.transform(lng, lat)
    
    # 3. فتح ملف Raster واستخراج القيمة
    try:
        with rasterio.open(raster_path) as src:
            # تحويل الإحداثيات إلى صف وعمود
            row, col = src.index(x, y)
            
            # قراءة القيمة
            value = src.read(1)[row, col]
            
            # التحقق من القيم الفارغة
            if src.nodata is not None and value == src.nodata:
                return {
                    "value": None,
                    "classification_arabic": "لا توجد بيانات",
                    "classification_english": "No Data",
                    "color": "#9ca3af"
                }
            
            # تصنيف القيمة
            arabic_class, english_class, color = classify_suitability(value)
            
            return {
                "value": float(value),
                "classification_arabic": arabic_class,
                "classification_english": english_class,
                "color": color
            }
            
    except Exception as e:
        raise Exception(f"خطأ في قراءة ملف Raster: {str(e)}")

def analyze_all_species(lat, lng):
    """
    تحليل جميع الأنواع لنقطة معينة
    يستخدم لتوليد تقرير PDF كامل
    """
    from species_manager import get_species_list, get_arabic_name, get_latin_name
    
    results = {
        "high": [],    # ملائم ممتاز
        "medium": [],  # ملائم متوسط
        "low": []      # غير ملائم
    }
    
    for species_id in get_species_list():
        try:
            result = extract_value(lat, lng, species_id)
            
            species_result = {
                "id": species_id,
                "arabic_name": get_arabic_name(species_id),
                "latin_name": get_latin_name(species_id),
                "value": result["value"],
                "classification": result["classification_arabic"],
                "color": result["color"]
            }
            
            # تصنيف حسب فئة الملاءمة
            if "ممتاز" in result["classification_arabic"]:
                results["high"].append(species_result)
            elif "متوسط" in result["classification_arabic"]:
                results["medium"].append(species_result)
            else:
                results["low"].append(species_result)
                
        except Exception as e:
            print(f"خطأ في تحليل {species_id}: {e}")
            continue
    
    # ترتيب النتائج تنازلياً حسب القيمة
    results["high"].sort(key=lambda x: x["value"] if x["value"] else 0, reverse=True)
    results["medium"].sort(key=lambda x: x["value"] if x["value"] else 0, reverse=True)
    results["low"].sort(key=lambda x: x["value"] if x["value"] else 0, reverse=True)
    
    return results