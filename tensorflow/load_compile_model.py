import tensorflow
from tensorflow.keras.models import load_model

def load_compile_model(model_dir):
    # Model Generation
    model = load_model(model_dir)
    #----------------------------------------------------
    # A necessary step if the model was trained using multiple GPUs.
    # Adjust parameters if you used different ones while training
    optimizer = tensorflow.keras.optimizers.Adam(lr=0.001, decay=1e-6)
    model.compile(optimizer=optimizer, 
                loss="categorical_crossentropy", 
                metrics=["accuracy"]) 
    print("Model compiled.")
    #----------------------------------------------------
    return model