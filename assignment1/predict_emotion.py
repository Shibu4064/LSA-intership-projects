import sys
try:
    import joblib
except Exception as e:
    print('ERROR: joblib not available:', e)
    sys.exit(2)

text = "I can't believe you did that, I am speechless"
model_path = 'emotion_model.joblib'
labels_path = 'label_names.txt'

try:
    model = joblib.load(model_path)
except Exception as e:
    print(f'ERROR: failed to load model at {model_path}:', e)
    sys.exit(3)

labels = None
try:
    with open(labels_path, 'r') as f:
        labels = [line.strip() for line in f if line.strip()]
except Exception:
    labels = None

# Prepare input
X = [text]

# Predict
try:
    pred = model.predict(X)
except Exception as e:
    print('ERROR: prediction failed:', e)
    sys.exit(4)

print('Raw prediction:', repr(pred))

# Try to map labels
try:
    mapped = None
    if labels is not None:
        # If pred contains integers or bytes
        mapped = []
        for p in pred:
            try:
                idx = int(p)
                mapped.append(labels[idx])
            except Exception:
                mapped.append(str(p))
    else:
        mapped = [str(p) for p in pred]
    print('Mapped prediction:', mapped)
except Exception as e:
    print('ERROR mapping labels:', e)

# Predict probs if available
try:
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X)[0]
        if labels is not None and len(labels) == len(probs):
            print('Probabilities:')
            for lab, p in zip(labels, probs):
                print(f'  {lab}: {p:.4f}')
        else:
            print('Probabilities (index:prob):')
            for i,p in enumerate(probs):
                print(f'  {i}: {p:.4f}')
    else:
        print('No predict_proba available for this model.')
except Exception as e:
    print('ERROR computing probabilities:', e)

# Print input for reference
print('\nInput:')
print(text)
