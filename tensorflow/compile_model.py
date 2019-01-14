import tensorflow
from yaml import load 

def compile_model(model):
    
    optimizer = tensorflow.keras.optimizers.Adam(lr=0.001, decay=1e-6)
    model.compile(optimizer=optimizer, 
                loss="categorical_crossentropy", 
                metrics=["accuracy"]) 
    print("Model compiled.")
    #----------------------------------------------------
    return model