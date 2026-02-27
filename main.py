from src.inference.predict import process_prescription

if __name__ == "__main__":
    result = process_prescription("sample_prescription.jpg")
    print(result)