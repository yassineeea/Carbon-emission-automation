# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

# ✅ Load BERT model as embedding generator
embedding_model = SentenceTransformer("kuro-08/bert-transaction-categorization")

# ✅ Define your categories (Cat1EN, Cat2EN, Description)

# Dummy reference categories (replace with your real categories or load CSV)
ref_data = pd.DataFrame({ "Cat1EN": [ "Purchase of goods","Purchase of goods","Purchase of goods","Purchase of goods", "Purchase of goods","Purchase of goods","Purchase of goods","Purchase of goods", "Purchase of goods","Purchase of goods","Purchase of materials","Purchase of materials", "Purchase of materials","Purchase of materials","Purchase of materials","Purchase of materials", "Purchase of services","Purchase of services","Purchase of services","Purchase of services", "Purchase of services","Purchase of services","Purchase of services","Purchase of services", "Purchase of services","Purchase of services","Purchase of services","Purchase of services", "Purchase of services","Purchase of services","Food & beverages","Food & beverages", "Food & beverages","Food & beverages","Food & beverages","Food & beverages", "Food & beverages","Food & beverages","Food & beverages","Food & beverages", "Heating and air conditioning","Heating and air conditioning","Fuels","Fuels","Fuels","Fuels", "Fuels","Fuels", "Mobility (freight)","Mobility (freight)","Mobility (freight)","Mobility (freight)", "Mobility (freight)", "Mobility (passengers)","Mobility (passengers)","Mobility (passengers)", "Mobility (passengers)","Mobility (passengers)","Mobility (passengers)","Mobility (passengers)", "Mobility (passengers)","Mobility (passengers)","Mobility (passengers)","Mobility (passengers)", "Process and fugitive emissions","Process and fugitive emissions", "Process and fugitive emissions", "Waste treatment","Waste treatment","Waste treatment", "Waste treatment","Waste treatment","Waste treatment","Waste treatment","Waste treatment", "Waste treatment","Waste treatment","Waste treatment","Waste treatment", "Use of electricity","Use of electricity","Use of electricity" ], 
                         
                         "Cat2EN": [ "Sporting goods","Buildings","Office supplies","Water consumption", "Household appliances","Electrical equipment","Machinery and equipment","Furniture", "Textiles and clothing","Vehicles","Construction materials","Organic materials", "Paper and cardboard","Plastics and rubber","Chemicals","Refrigerants and others", "Equipment rental","Building rental","Furniture rental","Vehicle rental and maintenance", "Information and cultural services","Catering services","Health services","Specialized craft services", "Administrative / consulting services","Cleaning services","IT services","Logistics services", "Marketing / advertising services","Technical services","Alcoholic beverages","Non-alcoholic beverages", "Condiments","Desserts","Fruits and vegetables","Fats and oils","Prepared / cooked meals", "Animal products","Cereal products","Dairy products","Heat and steam","Air conditioning and refrigeration", "Fossil fuels","Mobile fossil fuels","Organic fuels","Gaseous fossil fuels","Liquid fossil fuels", "Solid fossil fuels", "Air transport","Ship transport","Truck transport","Combined transport", "Train transport", "Air transport","Coach / Urban bus","Ship transport","Combined transport", "E-Bike","Accommodation / Events","Soft mobility","Motorcycle / Scooter","Train transport", "Public transport","Car", "Agriculture","Global warming potential","Industrial processes", "Commercial and industrial","Wastewater","Electrical equipment","Households and similar", "Metal","Organic materials","Paper and cardboard","Batteries and accumulators","Plastics", "Fugitive process emissions","Textiles","Glass", "Electricity for electric vehicles","Renewables","Standard" ], 
                         
                         "DescriptionCat2EN": [ "Goods purchase - sports","Goods purchase - buildings","Goods purchase - office items","Goods purchase - water", "Goods purchase - appliances","Goods purchase - electricals","Goods purchase - machinery","Goods purchase - furniture", "Goods purchase - textiles","Goods purchase - vehicles","Material purchase - construction","Material purchase - organic", "Material purchase - paper","Material purchase - plastics","Material purchase - chemicals","Material purchase - refrigerants", "Service - equipment rental","Service - building rental","Service - furniture rental","Service - vehicles", "Service - info/culture","Service - catering","Service - healthcare","Service - crafts", "Service - admin/consulting","Service - cleaning","Service - IT","Service - logistics", "Service - marketing","Service - technical","Beverages - alcoholic","Beverages - non-alcoholic", "Food condiments","Food desserts","Food fruits & vegetables","Food fats & oils","Prepared meals", "Animal-based food","Cereal-based food","Dairy products","Heating - heat & steam","Heating - cooling/refrigeration", "Fuel - fossil","Fuel - mobile fossil","Fuel - organic","Fuel - gaseous","Fuel - liquid","Fuel - solid", "Freight transport - air","Freight transport - ship","Freight transport - truck","Freight transport - combined", "Freight transport - train", "Passenger transport - air","Passenger transport - bus","Passenger transport - ship", "Passenger transport - combined","Passenger transport - e-bike","Passenger transport - accommodation/events", "Passenger transport - soft mobility","Passenger transport - scooter/motorbike","Passenger transport - train", "Passenger transport - public","Passenger transport - car", "Emissions - agriculture","Emissions - warming potential", "Emissions - industry", "Waste - commercial/industrial","Waste - wastewater","Waste - electricals", "Waste - households","Waste - metals","Waste - organics","Waste - paper","Waste - batteries", "Waste - plastics","Waste - fugitive","Waste - textiles","Waste - glass", "Electricity - EVs","Electricity - renewables","Electricity - standard" ] 
                        
                        })

# ✅ Precompute embeddings for categories
ref_data["combined"] = ref_data[["Cat1EN", "Cat2EN", "DescriptionCat2EN"]].agg(" ".join, axis=1)
ref_embeddings = embedding_model.encode(ref_data["combined"].tolist(), convert_to_tensor=True)

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Transaction Mapping API is running. Use POST /map_categories"
    }

# ✅ Request schema
class TransactionsRequest(BaseModel):
    transactions: List[str]

@app.post("/map_categories")
def map_categories(request: TransactionsRequest):
    results = []
    for text in request.transactions:
        # Encode transaction text
        trans_emb = embedding_model.encode(text, convert_to_tensor=True)

        # Compute cosine similarity with reference embeddings
        scores = util.pytorch_cos_sim(trans_emb, ref_embeddings).flatten()

        # Best match
        best_idx = torch.argmax(scores).item()
        results.append({
            "input_text": text,
            "best_Cat1": ref_data.iloc[best_idx]["Cat1EN"],
            "best_Cat2": ref_data.iloc[best_idx]["Cat2EN"],
            "similarity": float(scores[best_idx])
        })
    return {"matches": results}


