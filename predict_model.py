import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import torch.nn.functional as F

# --- 1. Constants (Must match your training notebook) ---
NUM_CLASSES = 5
MODEL_PATH = 'fish_classifier_resnet50_pytorch.pth'
IMAGE_SIZE = 224
CLASS_NAMES = ['Catla', 'Common carp', 'Pangasius', 'Rohu', 'Singi'] # Verify correct order

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# --- 2. Model Loading Function ---
def load_model(model_path):
    # Re-create ResNet50 base
    model = models.resnet50(weights='IMAGENET1K_V1')
    
    # Modify the final layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, NUM_CLASSES)
    
    # Load weights
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    
    model.eval()
    return model.to(device)

# Load the model globally once
try:
    LOADED_MODEL = load_model(MODEL_PATH)
except FileNotFoundError:
    print(f"ERROR: Model file not found at {MODEL_PATH}. Make sure it's in the same directory.")
    LOADED_MODEL = None # Handle this gracefully

# --- 3. Preprocessing Function (from your notebook) ---
def preprocess_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_bytes).convert('RGB')
    tensor = transform(image).unsqueeze(0)
    return tensor.to(device)

# --- 4. Prediction Function ---
def predict(image_bytes):
    if LOADED_MODEL is None:
        return {"error": "Model failed to load."}
        
    input_tensor = preprocess_image(image_bytes)
    
    with torch.no_grad():
        output = LOADED_MODEL(input_tensor)
        probabilities = F.softmax(output, dim=1).squeeze()
        
    probs = probabilities.tolist()
    
    # Map probabilities to class names
    prediction = dict(zip(CLASS_NAMES, probs))
    
    # Find the top prediction
    sorted_pred = sorted(prediction.items(), key=lambda item: item[1], reverse=True)
    
    return {
        "predicted_class": sorted_pred[0][0],
        "confidence": f"{sorted_pred[0][1] * 100:.2f}%",
        "probabilities": [
            {"class": c, "prob": f"{p:.4f}"} for c, p in sorted_pred
        ]
    }
