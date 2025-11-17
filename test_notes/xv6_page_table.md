# xv6 页表机制

## 概述

xv6 使用 RISC-V 架构的页表机制来实现虚拟内存。每个进程都有自己独立的页表，提供了进程之间的隔离。

## 页表结构

### 三级页表

RISC-V 使用三级页表结构：
- L2: 一级页表（Page Directory）
- L1: 二级页表（Page Middle Directory）
- L0: 三级页表（Page Table Entry）

每一级都包含 512 个条目，每个条目 8 字节（64位）。

### 虚拟地址结构

```
39位虚拟地址划分：
[38:30] - L2 索引 (9 bits)
[29:21] - L1 索引 (9 bits)
[20:12] - L0 索引 (9 bits)
[11:0]  - 页内偏移 (12 bits)
```

## 页表项（PTE）

每个页表项包含：
- **PPN**: 物理页号（Physical Page Number）
- **标志位**:
  - V (Valid): 有效位
  - R (Read): 可读
  - W (Write): 可写
  - X (Execute): 可执行
  - U (User): 用户模式可访问
  - G (Global): 全局映射
  - A (Accessed): 已访问
  - D (Dirty): 已修改

## 地址转换过程

1. CPU 读取 SATP 寄存器获取根页表物理地址
2. 使用虚拟地址的 L2 索引查找一级页表
3. 使用 L1 索引查找二级页表
4. 使用 L0 索引查找最终的物理页号
5. 物理页号 + 页内偏移 = 物理地址

## xv6 中的关键函数

### walk()

```c
pte_t *
walk(pagetable_t pagetable, uint64 va, int alloc)
{
  if(va >= MAXVA)
    panic("walk");

  for(int level = 2; level > 0; level--) {
    pte_t *pte = &pagetable[PX(level, va)];
    if(*pte & PTE_V) {
      pagetable = (pagetable_t)PTE2PA(*pte);
    } else {
      if(!alloc || (pagetable = (pde_t*)kalloc()) == 0)
        return 0;
      memset(pagetable, 0, PGSIZE);
      *pte = PA2PTE(pagetable) | PTE_V;
    }
  }
  return &pagetable[PX(0, va)];
}
```

这个函数遍历页表找到对应虚拟地址的 PTE。如果 alloc 为真，会分配缺失的页表页。

### mappages()

```c
int
mappages(pagetable_t pagetable, uint64 va, uint64 size, uint64 pa, int perm)
{
  uint64 a, last;
  pte_t *pte;

  a = PGROUNDDOWN(va);
  last = PGROUNDDOWN(va + size - 1);
  for(;;){
    if((pte = walk(pagetable, a, 1)) == 0)
      return -1;
    if(*pte & PTE_V)
      panic("remap");
    *pte = PA2PTE(pa) | perm | PTE_V;
    if(a == last)
      break;
    a += PGSIZE;
    pa += PGSIZE;
  }
  return 0;
}
```

映射一段虚拟地址到物理地址。

## 内核页表 vs 用户页表

### 内核页表
- 直接映射：虚拟地址 = 物理地址
- 全局唯一，所有 CPU 共享
- 包含内核代码、数据、设备地址

### 用户页表
- 每个进程独立
- 地址空间从 0 开始
- 用户代码在低地址，内核映射在高地址（trampoline）

## TLB（Translation Lookaside Buffer）

TLB 是页表缓存，加速地址转换：
- 缓存最近使用的虚拟地址到物理地址映射
- 上下文切换时需要刷新 TLB
- RISC-V 使用 `sfence.vma` 指令刷新

## 关键概念

1. **分页大小**: xv6 使用 4KB (4096 字节) 页
2. **页表隔离**: 每个进程有独立的页表，保证安全性
3. **按需分配**: walk() 可以在遍历时分配缺失的页表页
4. **权限控制**: 通过 PTE 标志位控制访问权限

## 调试技巧

使用 GDB 查看页表：
```bash
(gdb) p/x *pagetable@512
```

打印某个虚拟地址的映射：
```c
pte_t *pte = walk(pagetable, va, 0);
if (pte && (*pte & PTE_V)) {
  printf("va %p -> pa %p\n", va, PTE2PA(*pte));
}
```
