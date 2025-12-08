"""
Convert RoBERTa AI detector model to ONNX format for faster inference.

Usage:
    python convert_roberta_to_onnx.py --model <model_name> --output <output_path>

Example:
    python convert_roberta_to_onnx.py --model Hello-SimpleAI/chatgpt-detector-roberta --output app/models/ai_detector.onnx
"""

import argparse
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path


def convert_to_onnx(model_name: str, output_path: str, opset_version: int = 14):
    """
    Convert a HuggingFace RoBERTa model to ONNX format.
    
    Args:
        model_name: HuggingFace model identifier (e.g., "Hello-SimpleAI/chatgpt-detector-roberta")
        output_path: Path to save the ONNX model
        opset_version: ONNX opset version (default: 14)
    """
    print(f"Loading model: {model_name}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    
    # Create dummy input for tracing
    dummy_text = "This is a sample text for model conversion."
    inputs = tokenizer(
        dummy_text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )
    
    # Get input names
    input_names = list(inputs.keys())
    
    # Create output path
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting to ONNX format...")
    print(f"  Input names: {input_names}")
    print(f"  Opset version: {opset_version}")
    
    # Export to ONNX
    torch.onnx.export(
        model,
        tuple(inputs.values()),
        str(output_file),
        input_names=input_names,
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"}
        },
        opset_version=opset_version,
        do_constant_folding=True,
        verbose=False
    )
    
    print(f"✓ Model converted successfully!")
    print(f"  Saved to: {output_file}")
    print(f"  Size: {output_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Test the converted model
    print(f"\nTesting ONNX model...")
    import onnxruntime as ort
    
    session = ort.InferenceSession(str(output_file), providers=["CPUExecutionProvider"])
    
    # Prepare inputs for ONNX
    onnx_inputs = {k: v.numpy() for k, v in inputs.items()}
    
    # Run inference
    outputs = session.run(None, onnx_inputs)
    logits = outputs[0]
    
    # Compare with PyTorch
    with torch.no_grad():
        torch_outputs = model(**inputs)
        torch_logits = torch_outputs.logits.numpy()
    
    # Calculate difference
    max_diff = abs(logits - torch_logits).max()
    print(f"  Max difference between PyTorch and ONNX: {max_diff:.6f}")
    
    if max_diff < 1e-3:
        print(f"  ✓ Conversion verified - outputs match!")
    else:
        print(f"  ⚠ Warning: Outputs differ by {max_diff:.6f}")
    
    # Quantize the model for even better performance
    quantized_path = output_file.with_suffix('.quant.onnx')
    print(f"\nQuantizing model for faster inference...")
    
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        quantize_dynamic(
            str(output_file),
            str(quantized_path),
            weight_type=QuantType.QUInt8
        )
        
        print(f"✓ Quantized model saved!")
        print(f"  Saved to: {quantized_path}")
        print(f"  Size: {quantized_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"  Reduction: {(1 - quantized_path.stat().st_size / output_file.stat().st_size) * 100:.1f}%")
    except Exception as e:
        print(f"  ⚠ Quantization failed: {e}")
    
    return output_file, quantized_path if quantized_path.exists() else None


def main():
    parser = argparse.ArgumentParser(description="Convert RoBERTa model to ONNX format")
    parser.add_argument(
        "--model",
        type=str,
        default="Hello-SimpleAI/chatgpt-detector-roberta",
        help="HuggingFace model name (default: Hello-SimpleAI/chatgpt-detector-roberta)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="app/models/ai_detector.onnx",
        help="Output path for ONNX model (default: app/models/ai_detector.onnx)"
    )
    parser.add_argument(
        "--opset",
        type=int,
        default=14,
        help="ONNX opset version (default: 14)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("RoBERTa to ONNX Converter")
    print("=" * 70)
    
    convert_to_onnx(args.model, args.output, args.opset)
    
    print("\n" + "=" * 70)
    print("Conversion complete!")
    print("=" * 70)
    print("\nTo use the ONNX model, set the environment variable:")
    print(f'  AI_DETECTOR_MODEL_ONNX="{args.output}"')


if __name__ == "__main__":
    main()
