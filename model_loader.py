from transformers import AutoModelForCausalLM, AutoTokenizer ,BitsAndBytesConfig
import torch
import os

class TinyLlamaModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.initialized = False
        
    def load_model(self):
        """Load the TinyLlama model with optimizations for lower resource usage"""
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        hf_token = "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"
        
        print("Loading TinyLlama tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)
        
        print("Loading TinyLlama model...")
                # Define the quantization configuration
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,  # Use 4-bit quantization
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )

        # Load the model with the new configuration
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            use_auth_token=hf_token
        )
        
        self.initialized = True
        print("TinyLlama model loaded successfully")
    
    def generate_response(self, prompt, max_new_tokens=512):
        """Generate a response from the model"""
        if not self.initialized:
            self.load_model()
        
        # Format prompt for TinyLlama chat format
        formatted_prompt = f"<|user|>\n{prompt}\n<|assistant|>\n"
        
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)
        
        # Generate with reasonable parameters
        output = self.model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2
        )
        
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        response = generated_text.split("<|assistant|>")[-1].strip()
        
        return response

# Create a singleton instance
llm = TinyLlamaModel()
