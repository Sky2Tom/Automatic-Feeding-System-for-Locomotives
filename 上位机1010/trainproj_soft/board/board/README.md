# 项目结构

```c
└─board // 工程根目录
    ├─Core // 核心文件(如逻辑文件、业务文件等，包含main.c)
    │  ├─Inc
    │  └─Src
    ├─Doc // 参考资料文档
    ├─Drivers // 驱动文件
    │  ├─BSP // 板级支持包,外设、中断初始化以及中断服务函数等
    │  ├─CMSIS // ARM提供的CMSIS代码（主要包括各种头文件和启动文件（.s文件））
    │  └─STM32F1xx_HAL_Driver // ST提供的F1xx HAL库驱动代码
    ├─MDK-ARM // ARM工程文件，debug文件等
    └─Middlewares // 中间层，如操作系统、USMART等
```

# 项目内容

包含指示灯和24V开关量接收等内容