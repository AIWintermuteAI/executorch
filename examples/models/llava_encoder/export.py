# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from model import LlavaModel
import torch

from executorch.examples.models.llama2.builder import LlamaEdgeManager, DType
from executorch.examples.models.llama2.export_llama_lib import WeightType
from executorch.examples.models.llama2.lib.partitioner_lib import get_xnnpack_partitioner
from executorch.examples.models.llama2.source_transformation.sdpa import replace_sdpa_with_custom_op
from executorch.examples.models.llama2.source_transformation.quantize import get_quant_weight_transform
from executorch.examples.models.llama2.export_llama_lib import build_args_parser, get_quantizer_and_quant_params
from executorch.exir import to_edge, EdgeCompileConfig
from llava.constants import (
    IMAGE_TOKEN_INDEX,
)

def export_text_model(llava):
    llava_text_model = llava.text_model

    dim = torch.export.Dim("token_dim", min=1, max=llava.text_model_args.max_seq_len - 1)
    pos_dim = 1
    text_model_dynamic_shapes = ({1: dim}, {0: pos_dim})

    class LlavaEdgeManager(LlamaEdgeManager):
        def __init__(self, model, modelname, weight_type, dtype, use_kv_cache, use_sdpa_with_kv_cache, example_inputs):
            super().__init__(model, modelname, weight_type, dtype, use_kv_cache, use_sdpa_with_kv_cache, example_inputs)
        
        def _get_dynamic_shape(self) -> torch.Any:
            return text_model_dynamic_shapes
        
    text_model_em = LlavaEdgeManager(
        model=llava_text_model,
        modelname="llava_text_model",
        weight_type=WeightType.LLAMA,
        dtype=DType.fp32,
        use_kv_cache=True,
        use_sdpa_with_kv_cache=True,
        example_inputs=(embeddings, torch.tensor([0], dtype=torch.int64))
    )

    dtype_override = DType.fp32
    parser = build_args_parser()
    args = parser.parse_args(['-X', '-qmode', '8da4w', '--group_size', '128', '--embedding-quantize', '4,32'])
    quant_transform = get_quant_weight_transform(args, dtype_override, False)
    pt2e_quant_params, quantizers, quant_dtype = get_quantizer_and_quant_params(args)

    manager = (
        text_model_em
        .set_output_dir("./")
        .to_dtype(dtype_override)
        .source_transform([replace_sdpa_with_custom_op, quant_transform])
        .capture_pre_autograd_graph()
        .pt2e_quantize(quantizers)
    )

    with torch.no_grad():
        text_model_ep = torch.export.export(manager.pre_autograd_graph_module, manager.example_inputs, dynamic_shapes=manager._get_dynamic_shape())
    return text_model_ep


def export_image_encoder(llava, input_ids, imagr):
    index = torch.where(input_ids==IMAGE_TOKEN_INDEX)[1]
    prompt_before_image = input_ids[:, :index]
    prompt_after_image = input_ids[:, index+1:]
    class LlavaImageEncode(torch.nn.Module):
        """ Takes images and prompts and encode them into embeddings. Result will be sent to the text model LlavaTextModel."""
        def __init__(self, llava):
            super().__init__()
            self.llava = llava

        def forward(self, image):
            return self.llava.image_embedding(image)
        
    llava_image_encode = LlavaImageEncode(llava)
    ratio = max(imagr.shape[1], imagr.shape[2]) / image_processor.crop_size["height"]
    output_size = (int(imagr.shape[1] / ratio), int(imagr.shape[2] / ratio))
    resized = torchvision.transforms.Resize(size=output_size)(imagr)
    from executorch.exir import to_edge, EdgeCompileConfig

    with torch.no_grad():
        image_encode_ep = torch.export.export(llava_image_encode, (resized,), dynamic_shapes=dynamic_shapes, strict=False)
    return image_encode_ep

def main():
    llava_model = LlavaModel()
    llava = llava_model.get_eager_model()

    llava = llava.to(torch.float32)  # overflow error with fp16


    class LlavaPrefillEmbedding(torch.nn.Module):
        """ Takes images and prompts and encode them into embeddings. Result will be sent to the text model LlavaTextModel."""
        def __init__(self):
            super().__init__()

        def forward(self, prompt_before_image, imagr, prompt_after_image):
            return llava.prefill_embedding(prompt_before_image, imagr, prompt_after_image)
        
    class LlavaTokenEmbedding(torch.nn.Module):
        """ Takes a token and returns the token embedding. Result will be sent to the text model LlavaTextModel."""
        def __init__(self):
            super().__init__()

        def forward(self, token):
            return llava.token_embedding(token)
        
    # export LlavaPrefillEmbedding
    llava_prefill = LlavaPrefillEmbedding()
    inputs = llava_model.get_example_inputs()

    dynamic_shapes = llava_model.get_dynamic_shapes()
    with torch.no_grad():
        prefill_ep = torch.export.export(llava_prefill, inputs, dynamic_shapes=dynamic_shapes, strict=False)
    prefill_program = to_edge(prefill_ep, compile_config=EdgeCompileConfig(_check_ir_validity=False)).to_executorch()
    with open("llava_prefill.pte", "wb") as f:
        prefill_program.write_to_file(f)
    # export LlavaTokenEmbedding
    llava_token_embedding = LlavaTokenEmbedding()
    token = torch.tensor([0])
    token_embedding_ep = torch.export.export(llava_token_embedding, (token,), strict=False)
    embedding_program = to_edge(token_embedding_ep, compile_config=EdgeCompileConfig(_check_ir_validity=False)).to_executorch()
    with open("llava_embedding.pte", "wb") as f:
        embedding_program.write_to_file(f)

    # export LlavaTextModel
    embeddings = llava_prefill(*inputs)
    print(embeddings.shape)
    llava_text_model = llava.text_model

    dim = torch.export.Dim("token_dim", min=1, max=llava.text_model_args.max_seq_len - 1)
    text_model_dynamic_shapes = ({1: dim}, None)

    class LlavaEdgeManager(LlamaEdgeManager):
        def __init__(self, model, modelname, weight_type, dtype, use_kv_cache, use_sdpa_with_kv_cache, example_inputs):
            super().__init__(model, modelname, weight_type, dtype, use_kv_cache, use_sdpa_with_kv_cache, example_inputs)
        
        def _get_dynamic_shape(self) -> torch.Any:
            return text_model_dynamic_shapes
        
    text_model_em = LlavaEdgeManager(
        model=llava_text_model,
        modelname="llava_text_model",
        weight_type=WeightType.LLAMA,
        dtype=DType.fp32,
        use_kv_cache=True,
        use_sdpa_with_kv_cache=True,
        example_inputs=(embeddings, torch.tensor([0], dtype=torch.int64))
    )

    dtype_override = DType.fp32
    parser = build_args_parser()
    args = parser.parse_args(['-X', '-qmode', '8da4w', '--group_size', '128', '--embedding-quantize', '4,32'])
    quant_transform = get_quant_weight_transform(args, dtype_override, False)
    pt2e_quant_params, quantizers, quant_dtype = get_quantizer_and_quant_params(args)

    edge_program = (
        text_model_em
        .set_output_dir("./")
        .to_dtype(dtype_override)
        .source_transform([replace_sdpa_with_custom_op, quant_transform])
        .capture_pre_autograd_graph()
        .pt2e_quantize(quantizers)
        .export_to_edge()
    )
    partitioners = [get_xnnpack_partitioner()]
    print(f"Using partitioners: {partitioners}")
    executorch_program = edge_program.to_backend(partitioners).to_executorch()
    executorch_program.save_to_pte("llava_text_model.pte")

if __name__ == "__main__":
    main()
