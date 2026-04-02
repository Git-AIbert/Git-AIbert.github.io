---
title: "零基础入门 CuTe DSL"
date: 2026-04-01
categories:
  - DSL
description: "Cute DSL 学习笔记"
---

## CuTe DSL是什么？
CuTe 在 CUTLASS 3.x 中被引入，它是一个基于 C++ 模板的领域特定语言（DSL），用于以代数化方式描述 GPU 计算中的数据布局、分块策略和线程映射，并在编译期生成高效的内核访问模式，同时也可以通过 Python 绑定提供更高层的接口。

## 一个 CuTe 示例
```cpp
#include <cute/tensor.hpp>
using namespace cute;

__global__ void copy_8x8_by_tiles(float* A, float* B) {
  // ---------------------------
  // 1) 把原始指针包装成 CuTe Tensor
  //    全局张量形状: 8x8
  //    布局: row-major
  // ---------------------------
  Tensor gA = make_tensor(
      make_gmem_ptr(A),
      make_layout(make_shape(Int<8>{}, Int<8>{}),
                  make_stride(Int<8>{}, Int<1>{}))
  );

  Tensor gB = make_tensor(
      make_gmem_ptr(B),
      make_layout(make_shape(Int<8>{}, Int<8>{}),
                  make_stride(Int<8>{}, Int<1>{}))
  );

  // ---------------------------
  // 2) 定义 CTA 级 tile
  //    每个 block 处理一个 4x4 tile
  // ---------------------------
  auto cta_tiler = make_tile(Int<4>{}, Int<4>{});

  // 当前 CTA 在 tile 网格中的坐标
  // grid = (2, 2) 时:
  // blockIdx.x in [0,1], blockIdx.y in [0,1]
  auto cta_coord = make_coord(blockIdx.y, blockIdx.x);

  // 从全局矩阵中取出当前 CTA 对应的 4x4 tile
  Tensor ctaA = local_tile(gA, cta_tiler, cta_coord);
  Tensor ctaB = local_tile(gB, cta_tiler, cta_coord);

  // ---------------------------
  // 3) 定义线程布局
  //    4 个线程按 2x2 排列
  // ---------------------------
  auto thr_layout = make_layout(make_shape(Int<2>{}, Int<2>{}));

  // 把当前 4x4 CTA tile 再按线程布局切分
  // threadIdx.x = 0,1,2,3
  // 每个线程拿到一个 2x2 的局部视图
  Tensor thrA = local_partition(ctaA, thr_layout, threadIdx.x);
  Tensor thrB = local_partition(ctaB, thr_layout, threadIdx.x);

  // ---------------------------
  // 4) 每个线程处理自己的 2x2 子块
  // ---------------------------
  for (int i = 0; i < size<0>(thrA); ++i) {
    for (int j = 0; j < size<1>(thrA); ++j) {
      thrB(i, j) = thrA(i, j);
    }
  }
}
```

一个对应的启动方式可以是：
```cpp
dim3 grid(2, 2);   // 8x8 / 4x4 = 2x2 个 CTA
dim3 block(4);     // 4 个线程
copy_8x8_by_tiles<<<grid, block>>>(A, B);
```

## CuTe DSL和cutlass、cuda是什么关系？
CUDA 提供底层执行模型，CUTLASS 在其之上实现高性能算子实现库，而 CuTe 作为 CUTLASS 内部的领域特定语言，用于统一描述数据布局、分块策略与线程映射，从而提升内核构建的模块化与可扩展性。

```
CuTe（DSL，基础抽象）
   ↓ 被使用
CUTLASS（kernel库）
   ↓ 运行在
CUDA（执行平台）
```

在 CuTe 出现之前，CUTLASS 主要是基于 CUDA C++ 模板实现的高性能内核库。

CuTe 不生成 CUDA 代码，而是通过编译期模板展开，将抽象直接嵌入并实现为最终的 CUDA kernel。

## CuTe 的编译流程是什么样子的？
```
CuTe DSL（C++模板）
   ↓（模板实例化，编译器内部）
C++ AST（没有源码文件）
   ↓（NVCC编译）
PTX
   ↓（驱动JIT）
SASS（GPU指令）
```

## 为什么看不到模版展开后的代码？
类似于“看不到 C++ 模板完全实例化后的源码”，因为模板展开发生在编译器内部，并不会生成一个可读的中间代码表示。

## 为什么 CuTe 能够称之为 DSL？
虽然 CuTe 是通过 C++ 模板实现、且不依赖专用编译器（不同于 Triton），但它仍可被视为一种嵌入式 DSL，因为其核心不在于实现形式，而在于构建了独立于 C++ 的领域语义体系：它以 layout algebra 为基础，提供了如 shape、stride、tile 等抽象，并支持 partition、compose 等结构化变换，从而用于描述数据布局与计算映射关系，而非单纯的程序执行逻辑。

## 应该如何理解 CuTe 做了什么？
- 画 thread → tile 映射
- `print(layout);`
- PTX 看访存
- 使用Nsight Compute看
   - memory throughput
   - warp efficiency
   - Tensor Core 利用率

