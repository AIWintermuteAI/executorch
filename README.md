# ExecuTorch

To reproduce:

Install everything needed:
```
sh install_requirements.sh #for flatc issue
cd examples/arm
./setup.sh --i-agree-to-the-contained-eula build-dir
```
Softmax builds and runs normally
```
cd examples/arm
./run.sh --build_only --scratch-dir=build-dir --model_name=softmax --aot_arm_compiler_flags=""

I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:386] Model in 200014B0
I [executorch:arm_executor_runner.cpp:388] Model PTE file loaded. Size: 960 bytes.
I [executorch:arm_executor_runner.cpp:398] Model buffer loaded, has 1 methods
I [executorch:arm_executor_runner.cpp:406] Running method forward
I [executorch:arm_executor_runner.cpp:417] Setup Method allocator pool. Size: 1024 bytes.
I [executorch:arm_executor_runner.cpp:434] Setting up planned buffer 0, size 32.
I [executorch:arm_executor_runner.cpp:467] Method loaded.
I [executorch:arm_executor_runner.cpp:469] Preparing inputs...
I [executorch:arm_executor_runner.cpp:483] Input prepared.
I [executorch:arm_executor_runner.cpp:485] Starting the model execution...
I [executorch:arm_executor_runner.cpp:492] model_pte_loaded_size:     960 bytes.
I [executorch:arm_executor_runner.cpp:506] method_allocator_used:     342 / 1024  free: 682 ( used: 33 % )
I [executorch:arm_executor_runner.cpp:513] method_allocator_planned:  32 bytes
I [executorch:arm_executor_runner.cpp:515] method_allocator_loaded:   290 bytes
I [executorch:arm_executor_runner.cpp:516] method_allocator_input:    20 bytes
I [executorch:arm_executor_runner.cpp:517] method_allocator_executor: 0 bytes
I [executorch:arm_executor_runner.cpp:520] temp_allocator_used:       0 / 1024 free: 1024 ( used: 0 % )
I [executorch:arm_executor_runner.cpp:536] Model executed successfully.
I [executorch:arm_executor_runner.cpp:540] 1 outputs:
Output[0][0]: 0.500000
Output[0][1]: 0.500000
Output[0][2]: 0.500000
Output[0][3]: 0.500000
I [executorch:arm_executor_runner.cpp:577] Program complete, exiting.
I [executorch:arm_executor_runner.cpp:581]
```
Linear and add hang at Starting the model execution.
```
cd examples/arm
./run.sh --build_only --scratch-dir=build-dir --model_name=linear --aot_arm_compiler_flags=""

I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:386] Model in 200014B0 <
I [executorch:arm_executor_runner.cpp:388] Model PTE file loaded. Size: 1596 bytes.
I [executorch:arm_executor_runner.cpp:398] Model buffer loaded, has 1 methods
I [executorch:arm_executor_runner.cpp:406] Running method forward
I [executorch:arm_executor_runner.cpp:417] Setup Method allocator pool. Size: 1024 bytes.
I [executorch:arm_executor_runner.cpp:434] Setting up planned buffer 0, size 144.
I [executorch:arm_executor_runner.cpp:467] Method loaded.
I [executorch:arm_executor_runner.cpp:469] Preparing inputs...
I [executorch:arm_executor_runner.cpp:483] Input prepared.
I [executorch:arm_executor_runner.cpp:485] Starting the model execution...
```
Quantized MobileNetv2 alpha 0.05 96x96x3 requires allocation of 1.45 Mb of RAM.
```
cd examples/arm
./run.sh --build_only --scratch-dir=build-dir --model_name=mv2_untrained --aot_arm_compiler_flags="--quantize"

I [executorch:arm_executor_runner.cpp:325] BLINK
I [executorch:arm_executor_runner.cpp:386] Model in 200014B0 <
I [executorch:arm_executor_runner.cpp:388] Model PTE file loaded. Size: 175008 bytes.
I [executorch:arm_executor_runner.cpp:398] Model buffer loaded, has 1 methods
I [executorch:arm_executor_runner.cpp:406] Running method forward
I [executorch:arm_executor_runner.cpp:417] Setup Method allocator pool. Size: 1024 bytes.
I [executorch:arm_executor_runner.cpp:434] Setting up planned buffer 0, size 1785600.
E [executorch:memory_allocator.h:88] Memory allocation failed: 1785600B requested (adjusted for alignment), 1024B available
E [executorch:memory_allocator.h:88] Memory allocation failed: 68208B requested (adjusted for alignment), 1024B available
I [executorch:arm_executor_runner.cpp:459] Loading of method forward failed with status 0x21
I [executorch:arm_executor_runner.cpp:467] Method loaded.
I [executorch:arm_executor_runner.cpp:469] Preparing inputs...
F [executorch:result.h:165] In function CheckOk(), assert failed: hasValue_
```

**ExecuTorch** is an end-to-end solution for enabling on-device inference
capabilities across mobile and edge devices including wearables, embedded
devices and microcontrollers. It is part of the PyTorch Edge ecosystem and
enables efficient deployment of PyTorch models to edge devices.

Key value propositions of ExecuTorch are:

- **Portability:** Compatibility with a wide variety of computing platforms,
  from high-end mobile phones to highly constrained embedded systems and
  microcontrollers.
- **Productivity:** Enabling developers to use the same toolchains and Developer
  Tools from PyTorch model authoring and conversion, to debugging and deployment
  to a wide variety of platforms.
- **Performance:** Providing end users with a seamless and high-performance
  experience due to a lightweight runtime and utilizing full hardware
  capabilities such as CPUs, NPUs, and DSPs.

For a comprehensive technical overview of ExecuTorch and step-by-step tutorials,
please visit our documentation website [for the latest release](https://pytorch.org/executorch/stable/index.html) (or the [main branch](https://pytorch.org/executorch/main/index.html)).

Check out the [Getting Started](https://pytorch.org/executorch/stable/getting-started-setup.html#quick-setup-colab-jupyter-notebook-prototype) page for a quick spin.

Check out the examples of [Llama](./examples/models/llama/README.md), [Llava](./examples/models/llava/README.md) and [other models](./examples/README.md) running on edge devices using ExecuTorch.


**[UPDATE - 10/24]** We have added support for running [Llama 3.2 Quantized 1B/3B](./examples/models/llama/README.md) models via ExecuTorch.

## Feedback

We welcome any feedback, suggestions, and bug reports from the community to help
us improve our technology. Please use the [PyTorch
Forums](https://discuss.pytorch.org/c/executorch) for discussion and feedback
about ExecuTorch using the **ExecuTorch** category, and our [GitHub
repository](https://github.com/pytorch/executorch/issues) for bug reporting.

We recommend using the latest release tag from the
[Releases](https://github.com/pytorch/executorch/releases) page when developing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details about issues, PRs, code
style, CI jobs, and other development topics.

To connect with us and other community members, we invite you to join PyTorch Slack community by filling out this [form](https://docs.google.com/forms/d/e/1FAIpQLSeADnUNW36fjKjYzyHDOzEB_abKQE9b6gqqW9NXse6O0MWh0A/viewform). Once you've joined, you can:
* Head to the `#executorch-general` channel for general questions, discussion, and community support.
* Join the `#executorch-contributors` channel if you're interested in contributing directly to project development.


## Directory Structure

```
executorch
├── backends                        #  Backend delegate implementations.
├── build                           #  Utilities for managing the build system.
├── codegen                         #  Tooling to autogenerate bindings between kernels and the runtime.
├── configurations
├── docs                            #  Static docs tooling.
├── examples                        #  Examples of various user flows, such as model export, delegates, and runtime execution.
├── exir                            #  Ahead-of-time library: model capture and lowering APIs.
|   ├── _serialize                  #  Serialize final export artifact.
|   ├── backend                     #  Backend delegate ahead of time APIs
|   ├── capture                     #  Program capture.
|   ├── dialects                    #  Op sets for various dialects in the export process.
|   ├── emit                        #  Conversion from ExportedProgram to ExecuTorch execution instructions.
|   ├── operator                    #  Operator node manipulation utilities.
|   ├── passes                      #  Built-in compiler passes.
|   ├── program                     #  Export artifacts.
|   ├── serde                       #  Graph module
serialization/deserialization.
|   ├── verification                #  IR verification.
├── extension                       #  Extensions built on top of the runtime.
|   ├── android                     #  ExecuTorch wrappers for Android apps.
|   ├── apple                       #  ExecuTorch wrappers for iOS apps.
|   ├── aten_util                   #  Converts to and from PyTorch ATen types.
|   ├── data_loader                 #  1st party data loader implementations.
|   ├── evalue_util                 #  Helpers for working with EValue objects.
|   ├── gguf_util                   #  Tools to convert from the GGUF format.
|   ├── kernel_util                 #  Helpers for registering kernels.
|   ├── memory_allocator            #  1st party memory allocator implementations.
|   ├── module                      #  A simplified C++ wrapper for the runtime.
|   ├── parallel                    #  C++ threadpool integration.
|   ├── pybindings                  #  Python API for executorch runtime.
|   ├── pytree                      #  C++ and Python flattening and unflattening lib for pytrees.
|   ├── runner_util                 #  Helpers for writing C++ PTE-execution
tools.
|   ├── testing_util                #  Helpers for writing C++ tests.
|   ├── training                    #  Experimental libraries for on-device training
├── kernels                         #  1st party kernel implementations.
|   ├── aten
|   ├── optimized
|   ├── portable                    #  Reference implementations of ATen operators.
|   ├── prim_ops                    #  Special ops used in executorch runtime for control flow and symbolic primitives.
|   ├── quantized
├── profiler                        #  Utilities for profiling runtime execution.
├── runtime                         #  Core C++ runtime.
|   ├── backend                     #  Backend delegate runtime APIs.
|   ├── core                        #  Core structures used across all levels of the runtime.
|   ├── executor                    #  Model loading, initialization, and execution.
|   ├── kernel                      #  Kernel registration and management.
|   ├── platform                    #  Layer between architecture specific code and portable C++.
├── schema                          #  ExecuTorch PTE file format flatbuffer
schemas.
├── scripts                         #  Utility scripts for size management, dependency management, etc.
├── devtools                        #  Model profiling, debugging, and introspection.
├── shim                            #  Compatibility layer between OSS and Internal builds
├── test                            #  Broad scoped end-to-end tests.
├── third-party                     #  Third-party dependencies.
├── util                            #  Various helpers and scripts.
```

## License
ExecuTorch is BSD licensed, as found in the LICENSE file.
