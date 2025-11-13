# FIX: Model Loading Error - L2 Normalization Function

## Problem
When loading the trained FaceID model (`faceid_model_tf.h5` or `faceid_model_tf_best.h5`), the following error occurred:

```
TypeError: Could not locate function 'l2_normalize_func'. 
Make sure custom classes are decorated with `@keras.saving.register_keras_serializable()`.
```

This error happens because the model uses a custom Lambda layer with the `l2_normalize_func` function for L2 normalization of embeddings. When loading the model, Keras cannot find this function unless we explicitly provide it.

## Root Cause
In `train_faceid_improved_v2.py`, the model was built with a Lambda layer:

```python
# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function - chuẩn hóa vector về unit vector"""
    return tf.nn.l2_normalize(x, axis=1)

# Lambda layer sử dụng function này
embedding_normalized = layers.Lambda(
    l2_normalize_func, 
    output_shape=(128,),
    name='embedding_normalized'
)(embedding)
```

When loading the model with `tf.keras.models.load_model()`, we MUST provide the custom function via the `custom_objects` parameter.

## Solution
Add the custom function definition and pass it as `custom_objects` when loading the model:

```python
import tensorflow as tf

# Define the custom function (must match training code)
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# Load model with custom_objects
model = tf.keras.models.load_model(
    'faceid_model_tf.h5', 
    custom_objects={'l2_normalize_func': l2_normalize_func}
)
```

## Files Fixed
The following files have been updated with the fix:

1. **DACN/faceid_desktop/main.py** - Desktop application
2. **DACN/AI/app.py** - Flask API (production)
3. **DACN/AI/app_improved.py** - Flask API (improved version)
4. **DACN/AI/app_old.py** - Flask API (legacy version)
5. **DACN/AI/check_model.py** - Model inspection tool
6. **DACN/AI/import_to_mysql.py** - Database import script
7. **DACN/AI/import_faces_direct.py** - Face import script
8. **DACN/AI/debug_embedding.py** - Debugging tool
9. **DACN/AI/fix_model.py** - Model fixing script

## Usage Examples

### Desktop Application (main.py)
```python
model_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_model_tf.h5')
model = tf.keras.models.load_model(
    model_path, 
    custom_objects={'l2_normalize_func': l2_normalize_func}
)
```

### Flask API (app.py)
```python
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'faceid_model_tf_best.h5')
FULL_MODEL = tf.keras.models.load_model(
    MODEL_PATH, 
    custom_objects={'l2_normalize_func': l2_normalize_func}
)
```

## Testing
A test script has been created at `test_model_load.py` to verify the fix works:

```bash
cd D:\DACN
python test_model_load.py
```

Expected output:
```
✅ Model loaded successfully!
📊 Model input shape: (None, 160, 160, 3)
📊 Model output shape: (None, 6)
✅ Fix is working! Model can be loaded without errors.
```

## Important Notes

1. **Always include the custom function**: Whenever you load the model, you MUST include the `l2_normalize_func` definition and pass it via `custom_objects`.

2. **Function must match training code**: The function definition must be identical to the one used during training.

3. **No need to retrain**: This fix does not require retraining the model. The existing `.h5` files work correctly with this fix.

4. **Both models affected**: Both `faceid_model_tf.h5` and `faceid_model_tf_best.h5` require this fix.

## Verified Fix
The fix has been tested and verified to work correctly. The desktop application (`main.py`) and all API endpoints should now load the model without errors.

Date: November 12, 2025
