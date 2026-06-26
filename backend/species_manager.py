# species_manager.py
# ربط الأنواع الشجرية بملفات Raster وطبقات GeoServer

SPECIES_LAYERS = {
    "Acacia_spp": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Acacia_spp_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Acacia_spp_Fixed.tif",
        "arabic_name": "الأكاسيا",
        "latin_name": "Acacia spp"
    },
    "Atriplex_spp": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Atriplex_spp_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Atriplex_spp_Fixed.tif",
        "arabic_name": "القطف",
        "latin_name": "Atriplex spp"
    },
    "Ceratonia_siliqua": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Ceratonia_siliqua_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Ceratonia_siliqua_Fixed.tif",
        "arabic_name": "الخروب",
        "latin_name": "Ceratonia siliqua"
    },
    "Ficus_carica": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Ficus_carica_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Ficus_carica_Fixed.tif",
        "arabic_name": "التين",
        "latin_name": "Ficus carica"
    },
    "Olea_europaea": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Olea_europaea_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Olea_europaea_Fixed.tif",
        "arabic_name": "الزيتون",
        "latin_name": "Olea europaea"
    },
    "Opuntia_ficus-indica": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Opuntia_ficus-indica_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Opuntia_ficus-indica_Fixed.tif",
        "arabic_name": "التين الشوكي",
        "latin_name": "Opuntia ficus-indica"
    },
    "Pistacia_atlantica": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Pistacia_atlantica_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Pistacia_atlantica_Fixed.tif",
        "arabic_name": "البطوم",
        "latin_name": "Pistacia atlantica"
    },
    "Prunus_armeniaca": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Prunus_armeniaca_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Prunus_armeniaca_Fixed.tif",
        "arabic_name": "المشمش",
        "latin_name": "Prunus armeniaca"
    },
    "Prunus_dulcis": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Prunus_dulcis_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Prunus_dulcis_Fixed.tif",
        "arabic_name": "اللوز",
        "latin_name": "Prunus dulcis"
    },
    "Punica_granatum": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Punica_granatum_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Punica_granatum_Fixed.tif",
        "arabic_name": "الرمان",
        "latin_name": "Punica granatum"
    },
    "Ziziphus_lotus": {
        "geoserver_layer": "Mod-Space:Aptitude_Finale_Ziziphus_lotus_Fixed",
        "raster": r"C:\Users\LaptopCaba Khenchela\Desktop\Agroforestry_Geo\geodata\Aptitude_Finale_Ziziphus_lotus_Fixed.tif",
        "arabic_name": "السدر",
        "latin_name": "Ziziphus lotus"
    }
}

# ============================================
# دوال مساعدة
# ============================================

def get_species_list():
    """إرجاع قائمة بجميع الأنواع"""
    return list(SPECIES_LAYERS.keys())

def get_species_info(species_id):
    """إرجاع معلومات نوع محدد"""
    return SPECIES_LAYERS.get(species_id)

def get_arabic_name(species_id):
    """إرجاع الاسم العربي"""
    info = SPECIES_LAYERS.get(species_id, {})
    return info.get("arabic_name", species_id)

def get_latin_name(species_id):
    """إرجاع الاسم العلمي"""
    info = SPECIES_LAYERS.get(species_id, {})
    return info.get("latin_name", species_id)

def get_geoserver_layer(species_id):
    """إرجاع اسم الطبقة في GeoServer"""
    info = SPECIES_LAYERS.get(species_id, {})
    return info.get("geoserver_layer")

def get_raster_path(species_id):
    """إرجاع مسار ملف Raster المحلي"""
    info = SPECIES_LAYERS.get(species_id, {})
    return info.get("raster")

def classify_suitability(value):
    """تصنيف قيمة الملاءمة إلى فئة نصية ولون"""
    if value is None:
        return "لا توجد بيانات", "No Data", "#9ca3af"
    if value < 0.3:
        return "غير ملائم ❌", "Low", "#ef4444"
    elif value < 0.6:
        return "ملائم متوسط ⚠️", "Medium", "#f59e0b"
    else:
        return "ملائم ممتاز ✅", "High", "#10b981"