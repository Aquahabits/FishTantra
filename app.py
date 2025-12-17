from flask import Flask, render_template, request, send_file
import io
from predict_model import predict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

# =========================================================
# ICAR / BFSc LEVEL FISH DATABASE (FULL FOR ALL SPECIES)
# =========================================================

FISH_DATA = {

    "pangasius": {
        "taxonomy": {
            "Kingdom": "Animalia",
            "Phylum": "Chordata",
            "Class": "Actinopterygii",
            "Order": "Siluriformes",
            "Family": "Pangasiidae",
            "Genus": "Pangasius",
            "Species": "Pangasius hypophthalmus",
            "Common Name": "Pangasius / Sutchi catfish"
        },

        "aquaculture": {
            "Culture Systems": "Earthen ponds, cages, tanks, biofloc and RAS",
            "Site Selection": "Clay loam soil, perennial water source, flood-free area",
            "Pond Preparation": "Drying → liming (200–300 kg/ha) → manuring → water filling",
            "Seed Source": "Hatchery-produced fingerlings",
            "Seed Size": "8–10 cm fingerlings",
            "Stocking Density": "10,000–15,000 fingerlings/ha (pond culture)",
            "Stocking Season": "March–June",
            "Feeding": "Floating pelleted feed (28–32% crude protein)",
            "Feeding Rate": "3–5% body weight/day (initial), reduced later",
            "Water Quality": "Temperature 25–32°C, pH 6.5–8.5, DO >3 mg/L",
            "Health Management": "Probiotics, regular water exchange, disease monitoring",
            "Culture Period": "6–8 months",
            "Harvest Size": "800 g – 1.2 kg",
            "Harvesting": "Partial and complete harvesting using seine nets",
            "Production": "15–20 tonnes/ha/year"
        },

        "breeding_hatchery": {
            "Breeding Type": "Induced breeding",
            "Hormones Used": "Ovaprim / WOVA-FH",
            "Spawning Method": "Stripping and fertilisation",
            "Hatchery Type": "FRP circular hatchery",
            "Incubation Period": "24–30 hours",
            "Larval Rearing": "Spawn → fry → fingerlings in nursery ponds"
        }
    },

    "rohu": {
        "taxonomy": {
            "Kingdom": "Animalia",
            "Phylum": "Chordata",
            "Class": "Actinopterygii",
            "Order": "Cypriniformes",
            "Family": "Cyprinidae",
            "Genus": "Labeo",
            "Species": "Labeo rohita",
            "Common Name": "Rohu"
        },

        "aquaculture": {
            "Culture Systems": "Composite carp culture in ponds",
            "Site Selection": "Loamy soil with good water retention",
            "Pond Preparation": "Drying → liming (200–250 kg/ha) → manuring",
            "Seed Source": "Induced breeding hatcheries",
            "Seed Size": "8–10 cm fingerlings",
            "Stocking Density": "4,000–6,000/ha (30–35% of total stock)",
            "Stocking Season": "June–July",
            "Feeding": "Rice bran + oil cake (1:1) or pelleted feed",
            "Feeding Rate": "3–4% body weight/day",
            "Water Quality": "Temperature 22–32°C, pH 6.5–8.5",
            "Health Management": "Argulosis control, water quality maintenance",
            "Culture Period": "10–12 months",
            "Harvest Size": "700 g – 1 kg",
            "Harvesting": "Seine netting",
            "Production": "3–5 tonnes/ha/year"
        },

        "breeding_hatchery": {
            "Breeding Type": "Induced breeding",
            "Hormones Used": "Pituitary gland extract / Ovaprim",
            "Spawning Season": "South-west monsoon",
            "Hatchery Type": "Chinese circular hatchery",
            "Incubation Period": "12–16 hours",
            "Nursery Rearing": "Spawn stocked @ 3–5 million/ha"
        }
    },

    "catla": {
        "taxonomy": {
            "Kingdom": "Animalia",
            "Phylum": "Chordata",
            "Class": "Actinopterygii",
            "Order": "Cypriniformes",
            "Family": "Cyprinidae",
            "Genus": "Catla",
            "Species": "Catla catla",
            "Common Name": "Catla"
        },

        "aquaculture": {
            "Culture Systems": "Composite carp culture",
            "Site Selection": "Large ponds with high plankton productivity",
            "Pond Preparation": "Drying → liming → fertilisation",
            "Seed Source": "Hatchery produced seed",
            "Seed Size": "10–12 cm fingerlings",
            "Stocking Density": "2,000–3,000/ha",
            "Stocking Season": "June–July",
            "Feeding": "Supplementary feed + plankton",
            "Feeding Rate": "2–3% body weight",
            "Water Quality": "Temperature 25–32°C, pH 6.5–8.0",
            "Health Management": "EUS prevention, liming",
            "Culture Period": "10–12 months",
            "Harvest Size": "1–1.5 kg",
            "Harvesting": "Drag netting",
            "Production": "4–6 tonnes/ha/year"
        },

        "breeding_hatchery": {
            "Breeding Type": "Induced breeding",
            "Hormones Used": "Pituitary gland / Ovaprim",
            "Spawning Season": "Monsoon",
            "Hatchery Type": "Chinese hatchery",
            "Incubation Period": "15–18 hours"
        }
    },

    "common carp": {
        "taxonomy": {
            "Kingdom": "Animalia",
            "Phylum": "Chordata",
            "Class": "Actinopterygii",
            "Order": "Cypriniformes",
            "Family": "Cyprinidae",
            "Genus": "Cyprinus",
            "Species": "Cyprinus carpio",
            "Common Name": "Common Carp"
        },

        "aquaculture": {
            "Culture Systems": "Monoculture and polyculture",
            "Site Selection": "Wide tolerance to pond conditions",
            "Pond Preparation": "Drying → liming → organic manuring",
            "Seed Source": "Natural and induced breeding",
            "Seed Size": "8–10 cm fingerlings",
            "Stocking Density": "5,000–8,000/ha",
            "Feeding": "Rice bran, oil cake, farm-made feed",
            "Feeding Rate": "3–5% body weight",
            "Water Quality": "Temperature 20–30°C, pH 6.5–8.5",
            "Health Management": "Fin rot control, water exchange",
            "Culture Period": "8–10 months",
            "Harvest Size": "1–1.5 kg",
            "Harvesting": "Seine netting",
            "Production": "5–7 tonnes/ha/year"
        },

        "breeding_hatchery": {
            "Breeding Type": "Natural and induced breeding",
            "Spawning Method": "Kakaban method",
            "Egg Type": "Adhesive eggs",
            "Incubation Period": "3–5 days"
        }
    },

    "singhi": {
        "taxonomy": {
            "Kingdom": "Animalia",
            "Phylum": "Chordata",
            "Class": "Actinopterygii",
            "Order": "Siluriformes",
            "Family": "Heteropneustidae",
            "Genus": "Heteropneustes",
            "Species": "Heteropneustes fossilis",
            "Common Name": "Singhi"
        },

        "aquaculture": {
            "Culture Systems": "Monoculture in shallow ponds and tanks",
            "Site Selection": "Shallow ponds with minimal water exchange",
            "Pond Preparation": "Heavy liming (300–500 kg/ha)",
            "Seed Source": "Induced breeding",
            "Seed Size": "5–8 cm fingerlings",
            "Stocking Density": "50,000–80,000/ha",
            "Feeding": "High protein feed (35–40%)",
            "Feeding Rate": "5–7% body weight",
            "Water Quality": "Temperature 24–32°C, tolerant to low DO",
            "Health Management": "Bacterial disease control, clean water",
            "Culture Period": "6–8 months",
            "Harvest Size": "80–120 g",
            "Harvesting": "Hand picking and netting",
            "Production": "1.5–2.5 tonnes/ha/year"
        },

        "breeding_hatchery": {
            "Breeding Type": "Induced breeding",
            "Hormones Used": "Ovaprim",
            "Spawning Method": "Stripping",
            "Incubation Period": "20–24 hours"
        }
    }
}

NAME_MAP = {
    "pangasius": "pangasius",
    "pangasius hypophthalmus": "pangasius",
    "rohu": "rohu",
    "labeo rohita": "rohu",
    "catla": "catla",
    "catla catla": "catla",
    "common carp": "common carp",
    "cyprinus carpio": "common carp",
    "singhi": "singhi",
    "heteropneustes fossilis": "singhi"
}

# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict_fish():
    file = request.files["file"]
    image_bytes = io.BytesIO(file.read())
    result = predict(image_bytes)
    predicted = result.get("predicted_class", "").lower()
    key = NAME_MAP.get(predicted)
    fish_info = FISH_DATA.get(key)

    return render_template(
        "result.html",
        fish_name=predicted.title(),
        fish_info=fish_info
    )


@app.route("/download/<fish>")
def download_pdf(fish):
    info = FISH_DATA.get(fish.lower())
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    text = pdf.beginText(40, 800)

    text.textLine(f"FishTantra – {fish.title()}")
    text.textLine("")

    for section, content in info.items():
        text.textLine(section.upper())
        for k, v in content.items():
            text.textLine(f"- {k}: {v}")
        text.textLine("")

    pdf.drawText(text)
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"{fish}.pdf")

if __name__ == "__main__":
    app.run(debug=True)
