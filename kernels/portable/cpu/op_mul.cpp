/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

#include <executorch/kernels/portable/cpu/op_mul_impl.h>

namespace torch {
namespace executor {
namespace native {

Tensor& mul_out(
    KernelRuntimeContext& ctx,
    const Tensor& a,
    const Tensor& b,
    Tensor& out) {
  return mul_out_impl(ctx, a, b, out);
}

Tensor& mul_scalar_out(
    KernelRuntimeContext& ctx,
    const Tensor& a,
    const Scalar& b,
    Tensor& out) {
  return mul_scalar_out_impl(ctx, a, b, out);
}

} // namespace native
} // namespace executor
} // namespace torch
