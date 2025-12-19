/*
 * ModBus_content.h
 *
 *  Created on: 2024年3月20日
 *      Author: ziyou
 */

#ifndef MODBUS_CONTENT_H_
#define MODBUS_CONTENT_H_
#include "stm32f1xx_hal.h"

typedef struct
{
    uint8_t        working_channel:1;        //工作备用通道标志位 下传或设定值  0 备用　 1 工作
    uint8_t        pulse_off:1;        //脉冲封锁标志位 下传或设定值  0 未锁　 1 封锁
    uint8_t        changeover:1;        //切换，新增加的
    uint8_t        manual_on:1;        //手动开环/自动闭环标志位    下传或设定值  0 自动　 1 手动
    uint8_t        forbid_hot_standby:1;    //禁用热备标志位  下传或设定值  0 允许　 1 禁用
    uint8_t        None5:1;    //
    uint8_t        button_sound:1;        //按钮音响标志位        0 有音   1 静音
    uint8_t        None7:1;    //
}CoilByte0;
typedef struct
{
   uint8_t        control_angle_display:1;        //控制角显示标志位  下传或设定值  0 控制角　1 导通角
   uint8_t        trigger_reverse:1;        //触发旋向标志位 下传或设定值  0 正向　   1 反向
   uint8_t        AC_display:1;        //交流显示有效 下传或设定值  0 无效　　 1 有效
   uint8_t        AC_feedback_first:1;        //主反馈交直选择标志位    下传或设定值  0 直流　　 1 交流
   uint8_t        two_feedback:1;    //单双反馈选择标志位    下传或设定值  0 单反馈　 1 双反馈
   uint8_t        display_filter:1;    //显示滤波   下传或设定值  0 无效　　 1 有效
   uint8_t        None6:1;        //
   uint8_t        None7:1;        //
}CoilByte1;
typedef struct
{


    uint8_t        error_reset:1;        //故障复位   —   置1位后，自动复位
    uint8_t        password_default:1;        //操作密码恢复缺省。   —   置1位后，自动复位
    uint8_t        None2:1;        //占空位的，不存数据
    uint8_t        None3:1;        //占空位的，不存数据
    uint8_t        None4:1;        //占空位的，不存数据
    uint8_t        None5:1;    //占空位的，不存数据
    uint8_t        None6:1;    //占空位的，不存数据
    uint8_t        None7:1;        //占空位的，不存数据
}CoilByte2;
typedef struct
{
    uint8_t        None0:1;        //占空位的，不存数据
    uint8_t        None1:1;        //占空位的，不存数据
    uint8_t        None2:1;        //占空位的，不存数据
    uint8_t        None3:1;        //占空位的，不存数据
    uint8_t        None4:1;        //占空位的，不存数据
    uint8_t        None5:1;    //占空位的，不存数据
    uint8_t        None6:1;    //占空位的，不存数据
    uint8_t        None7:1;        //占空位的，不存数据
}CoilByte3;
union CoilByte0_u {
   uint8_t          all;
   CoilByte0      bit;
};
union CoilByte1_u {
   uint8_t          all;
   CoilByte1      bit;
};
union CoilByte2_u {
   uint8_t          all;
   CoilByte2      bit;
};
union CoilByte3_u {
   uint8_t          all;
   CoilByte3      bit;
};
typedef struct  CoilRegister_t
{
    union CoilByte0_u               Coil0;      //共4个8bit的线圈，相当于32个线圈
    union CoilByte1_u               Coil1;      //
    union CoilByte2_u               Coil2;      //
    union CoilByte3_u               Coil3;      //
}CoilRegister;




//typedef struct
//{
//    uint8_t        pulse_off:1;        //封锁脉冲   与DI 锁脉冲或软件锁对应   0 无　　1 有
//    uint8_t        extern_current_drop:1;        //外部降电流 与DI 降电流对应   0 无　　1 有
//    uint8_t        None2:1;        //
//    uint8_t        simu_given:1;        //模拟给定   当前给定为模拟给定   0 不是　1 是
//    uint8_t        given_is_zero:1;        //给定回零    与DO对应，给定小于1.5%  0 非零　1 回零
//    uint8_t        hot_standby:1;    //热备用状态    当前备用通道进入热备标志    0 不是　1 是
//    uint8_t        auto_DC_feedback :1;    //自动直流反馈运行状态 当前工作通道自动反馈为直流   0 不是　1 是
//    uint8_t        auto_AC_feedback:1;        //自动交流反馈运行状态 当前工作通道自动反馈为交流   0 不是　1 是
//}DisByte0;
//typedef struct
//{
//    uint8_t        manual:1;        //手动运行状态 当前工作通道处手动运行状态   0 不是　1 是
//    uint8_t        two_feedbacking:1;        //双路反馈  当前是否开启双路反馈监视    0 单反馈　1 双反馈
//    uint8_t        host_normal:1;        //本机正常    与DO对应，通道上电正常接通  0 不是　1 是
//    uint8_t        pulsing:1;        //脉冲工作   与面板脉冲工作指示灯对应，表明当前通道在发脉冲  0 不是　1 是
//    uint8_t        ABconnected:1;        //主备连接    Link_OK　有效  0 不是　1 是
//    uint8_t        ABcommunicating:1;    //主备通讯     0 无　　1 正常
//    uint8_t        current_limiting:1;    //限流     0 不是　1 是
//    uint8_t        pulse_reverse:1;        //输出反向       0 正向  1 反向
//}DisByte1;
//typedef struct
//{
//    uint8_t        intern_error:1;        //数控器内部故障    与面板指示对应，与DO对应所有内部（I）故障综合 0 无　　1 有
//    uint8_t        exern_error:1;        //数控器外部故障   与面板指示对应，所有外部（O）故障综合 0 无　　1 有
//    uint8_t        sync_error:1;        //同步异常    O＿2＿A　与DO　对应    0 无　　1 有
//    uint8_t        feedback_error:1;        //反馈异常   O＿3＿A　与DO　对应    0 无　　1 有
//    uint8_t        None4:1;        //
//    uint8_t        None5:1;    //
//    uint8_t        DC_exceeding:1;    //直流电流越限 O＿3＿A　与DO　对应    0 无　　1 有
//    uint8_t        DC_error:1;        //直流电路故障 I＿3＿B   0 无　　1 有
//}DisByte2;
//typedef struct
//{
//    uint8_t        AC_error:1;        //交流电路故障 I＿3＿B   0 无　　1 有
//    uint8_t        given_error:1;        //模拟给定电路故障  I＿3＿B   0 无　　1 有
//    uint8_t        commu_error:1;        //主控通讯故障  I＿3＿A   0 无　　1 有
//    uint8_t        EPROM_error:1;        //EPROM故障    I＿3＿A   0 无　　1 有
//    uint8_t        memory_error:1;        //双口存储故障  I＿2＿A   0 无　　1 有
//    uint8_t        None5:1;    //
//    uint8_t        key_error:1;    //键盘故障   I＿3＿A   0 无　　1 有
//    uint8_t        _196_error:1;        //196故障  I＿1＿A   0 无　　1 有
//}DisByte3;
//typedef struct
//{
//    uint8_t        pulse_error:1;        //脉冲故障   I＿1＿B   0 无　  1 有
//    uint8_t        None1:1;        //
//    uint8_t        None2:1;        //
//    uint8_t        None3:1;        //
//    uint8_t        None4:1;        //
//    uint8_t        None5:1;    //
//    uint8_t        None6:1;    //
//    uint8_t        pulse_cut:1;        //脉冲断线   O＿1＿B   0 无　  1 有
//}DisByte4;
//typedef struct
//{
//    uint8_t        None0:1;        //
//    uint8_t        None1:1;         //
//    uint8_t        None2:1;         //
//    uint8_t        None3:1;         //
//    uint8_t        None4:1;        //
//    uint8_t        None5:1;     //
//    uint8_t        loss_strong_trigger:1;    //失强触发电源 O＿1＿B   0 无　  1 有
//    uint8_t        None7:1;       //
//}DisByte5;
//typedef struct
//{
//    uint8_t        None0:1;        //
//    uint8_t        working_channel:1;        //工作备用通道标志位 下传或设定值  0 备用　 1 工作
//    uint8_t        pulse_off:1;        //脉冲封锁标志位 下传或设定值  0 未锁　 1 封锁
//    uint8_t        None3:1;        //
//    uint8_t        manual_on:1;        //手动开环/自动闭环标志位    下传或设定值  0 自动　 1 手动
//    uint8_t        forbid_hot_standby:1;    //禁用热备标志位  下传或设定值  0 允许　 1 禁用
//    uint8_t        None6:1;    //
//    uint8_t        button_sound:1;        //按钮音响标志位        0 有音   1 静音
//}DisByte6;
//typedef struct
//{
//    uint8_t        None0:1;        //占空位的，不存数据
//        uint8_t        None1:1;        //占空位的，不存数据
//        uint8_t        None2:1;        //占空位的，不存数据
//        uint8_t        None3:1;        //占空位的，不存数据
//        uint8_t        None4:1;        //占空位的，不存数据
//        uint8_t        None5:1;    //占空位的，不存数据
//        uint8_t        None6:1;    //占空位的，不存数据
//        uint8_t        None7:1;        //占空位的，不存数据
//}DisByte7;
//typedef struct
//{
//    uint8_t        None0:1;        //
//    uint8_t        control_angle_display:1;        //控制角显示标志位  下传或设定值  0 控制角　1 导通角
//    uint8_t        trigger_reverse:1;        //触发旋向标志位 下传或设定值  0 正向　   1 反向
//    uint8_t        AC_display:1;        //交流显示有效 下传或设定值  0 无效　　 1 有效
//    uint8_t        AC_feedback:1;        //主反馈交直选择标志位    下传或设定值  0 直流　　 1 交流
//    uint8_t        two_feedback:1;    //单双反馈选择标志位    下传或设定值  0 单反馈　 1 双反馈
//    uint8_t        display_filter:1;    //显示滤波   下传或设定值  0 无效　　 1 有效
//    uint8_t        None7:1;        //
//}DisByte8;
//typedef struct
//{
//    uint8_t        None0:1;        //占空位的，不存数据
//    uint8_t        None1:1;        //占空位的，不存数据
//    uint8_t        None2:1;        //占空位的，不存数据
//    uint8_t        None3:1;        //占空位的，不存数据
//    uint8_t        None4:1;        //占空位的，不存数据
//    uint8_t        None5:1;    //占空位的，不存数据
//    uint8_t        None6:1;    //占空位的，不存数据
//    uint8_t        None7:1;        //占空位的，不存数据
//}DisByte9;
//union DisByte0_u {
//   uint8_t          all;
//   DisByte0      bit;
//};
//union DisByte1_u {
//   uint8_t          all;
//   DisByte1      bit;
//};
//union DisByte2_u {
//   uint8_t          all;
//   DisByte2      bit;
//};
//union DisByte3_u {
//   uint8_t          all;
//   DisByte3      bit;
//};
//union DisByte4_u {
//   uint8_t          all;
//   DisByte4      bit;
//};
//union DisByte5_u {
//   uint8_t          all;
//   DisByte5      bit;
//};
//union DisByte6_u {
//   uint8_t          all;
//   DisByte6      bit;
//};
//union DisByte7_u {
//   uint8_t          all;
//   DisByte7      bit;
//};
//union DisByte8_u {
//   uint8_t          all;
//   DisByte8      bit;
//};
//union DisByte9_u {
//   uint8_t          all;
//   DisByte9      bit;
//};
//typedef struct  DiscreteInputRegister_t //离散输入寄存器结构体
//{
//    union DisByte0_u               Dis0;      //共10个8bit的线圈，相当于80个线圈
//    union DisByte1_u               Dis1;      //
//    union DisByte2_u               Dis2;      //
//    union DisByte3_u               Dis3;      //
//    union DisByte4_u               Dis4;      //
//    union DisByte5_u               Dis5;      //
//    union DisByte6_u               Dis6;      //
//    union DisByte7_u               Dis7;      //
//    union DisByte8_u               Dis8;      //
//    union DisByte9_u               Dis9;      //
//}DiscreteInputRegister;

typedef struct DataRegister_t
{
    uint16_t    current_limit_value;  //限流值       1-99.99  单位0.01KA   小数点位置可变
    uint16_t    initial_delay_angle_degree;  //初始定相值     0～3600　单位0.1°
    uint16_t    max_delay_angle_degree;  //最大限幅值     0～1500　单位0.1°
    uint16_t    voltage_Kp;  //电压环P 单位0.001
    uint16_t    voltage_Ki;  //电压环I 单位0.001
    uint16_t    current_Kp;  //电流环P 单位0.001
    uint16_t    current_Ki;  //电流环I 单位0.001
    uint16_t    voltage_range;  //电压量程 单位0.1V
    uint16_t    AC_range;  //交流电流量程    1～1023 对应 0～10000 ( * A→1000.0A) 数值范围1-9999
    uint16_t    DC_current_range;  //直流电流量程    1～1023 对应 1～10000 ( * KA→100.00KA)  数值范围1-9999
    uint16_t    fire_display_ratio;  //控制角导通角输出显示系数
    uint16_t    DC_feedback_amplitude;  //直流反馈幅度选择  00~07　分别对应相关量程选择
    uint16_t    AC_feedback_amplitude;  //交流反馈幅度选择   00~07　分别对应相关量程选择
    uint16_t    extern_given_amplitude;  //外部给定幅度选择      00~07　分别对应相关量程选择
    uint16_t    output_voltage_setpoint;  //电压给定 0~10000 单位0.1V
    uint16_t    AC_correction;  //交流电流修正系数  调整使正常工作时，交直反馈工作数值相等 100~3000
    uint16_t    DC_correction;  //直流电流修正系数  调整直流反馈于满量程时为最大限流值   100~3000
    uint16_t    angle_correction;  //控制角导通角修正系数    对应于196输出控制角导通角数据的变换系数(与数显表对应)   0～1000 对应 0～10.0V
    uint16_t    DC_current_setpoint1;  //直流自动给定（D）     0～10000　单位0.01KA    小数点位置可变
    uint16_t    DC_current_setpoint2;  //直流自动给定2（D）     0～10000　单位0.01KA
    uint16_t    manual_delay_angle_degree;  //手动开环给定(M)     0～1500　单位0.1°
    uint16_t    current_ramp_time;  //电流给定斜坡时间 单位100ms
    uint16_t    year;  //年 00~99
    uint16_t    month;  //月 1~12
    uint16_t    day;  //日 1~31
    uint16_t    hour;  //时 1~24
    uint16_t    minute;  //分 1~60
    uint16_t    second;  //秒 1~60
    uint16_t    None28;  //
    uint16_t    contrast;  //液晶对比度值       0～100
    uint16_t    ID;  //数控器站地址       00~255
    uint16_t    None31;
}DataRegister;
typedef struct
{
    uint16_t        DI_pulse_off:1;        //封锁脉冲   与DI 锁脉冲或软件锁对应   0 无　　1 有
    uint16_t        IO_drop_current:1;        //外部降电流 与DI 降电流对应   0 无　　1 有
    uint16_t        use_analog_setpoint:1;        //模拟给定   当前给定为模拟给定   0 不是　1 是
    uint16_t        setpoint_is_zero:1;        //给定回零    与DO对应，给定小于1.5%  0 非零　1 回零
    uint16_t        hot_standby:1;    //热备用状态    当前备用通道进入热备标志    0 不是　1 是
    uint16_t        use_DC1_feedback:1;    //通道1使用直流反馈
    uint16_t        use_AC1_feedback:1;    //通道1使用交流反馈
    uint16_t        use_DC2_feedback:1;    //通道2使用直流反馈
    uint16_t        use_AC2_feedback:1;    //通道2使用交流反馈
    uint16_t        manual:1;        //手动运行状态 当前工作通道处手动运行状态   0 不是　1 是
    uint16_t        host_normal:1;        //本机正常    与DO对应，通道上电正常接通  0 不是　1 是
    uint16_t        pulsing:1;        //脉冲工作   与面板脉冲工作指示灯对应，表明当前通道在发脉冲  0 不是　1 是
    uint16_t        ABconnected:1;        //主备连接    Link_OK　有效  0 不是　1 是
    uint16_t        ABcommunicating:1;    //主备通讯     0 无　　1 正常
    uint16_t        current_limiting:1;    //限流     0 不是　1 是
    uint16_t        pulse_reverse:1;        //输出反向       0 正向  1 反向
}half_Word0;
typedef struct
{
    uint16_t        intern_error:1;        //数控器内部故障    与面板指示对应，与DO对应所有内部（I）故障综合 0 无　　1 有
    uint16_t        exern_error:1;        //数控器外部故障   与面板指示对应，所有外部（O）故障综合 0 无　　1 有
    uint16_t        sync_error:1;        //缺相    O＿2＿A　与DO　对应    0 无　　1 有
    uint16_t        feedback_error:1;        //反馈异常   O＿3＿A　与DO　对应    0 无　　1 有
    uint16_t        all_sync_error:1;        //完全失同步      0无 1有
    uint16_t        None5:1;    //
    uint16_t        DC_exceeding:1;    //直流电流越限 O＿3＿A　与DO　对应    0 无　　1 有
    uint16_t        DC_error:1;        //直流反馈故障 I＿3＿B   0 无　　1 有
    uint16_t        AC_error:1;        //交流电路故障 I＿3＿B   0 无　　1 有
    uint16_t        DC2_error:1;        //模拟给定电路故障  I＿3＿B   0 无　　1 有
    uint16_t        AC2_error:1;        //主控通讯故障  I＿3＿A   0 无　　1 有
    uint16_t        EPROM_error:1;        //EPROM故障    I＿3＿A   0 无　　1 有
    uint16_t        memory_error:1;        //双口存储故障  I＿2＿A   0 无　　1 有
    uint16_t        None13:1;    //
    uint16_t        key_error:1;    //键盘故障   I＿3＿A   0 无　　1 有
    uint16_t        _196_error:1;        //196故障  I＿1＿A   0 无　　1 有

}half_Word1;
typedef struct
{
    uint16_t        pulse_error:1;        //脉冲故障   I＿1＿B   0 无　  1 有
    uint16_t        None1:1;        //
    uint16_t        None2:1;        //
    uint16_t        None3:1;        //
    uint16_t        None4:1;        //
    uint16_t        None5:1;    //
    uint16_t        None6:1;    //
    uint16_t        pulse_breakwire:1;        //脉冲断线   O＿1＿B   0 无　  1 有
    uint16_t        None8:1;        //
    uint16_t        None9:1;         //
    uint16_t        None10:1;         //
    uint16_t        None11:1;         //
    uint16_t        None12:1;        //
    uint16_t        None13:1;     //
    uint16_t        loss_strong_trigger:1;    //失强触发电源 O＿1＿B   0 无　  1 有
    uint16_t        None15:1;       //

}half_Word2;
typedef struct
{
    uint16_t        None0:1;        //
    uint16_t        working_channel:1;        //工作备用通道标志位 下传或设定值  0 备用　 1 工作
    uint16_t        pulse_off:1;        //脉冲封锁标志位 下传或设定值  0 未锁　 1 封锁
    uint16_t        None3:1;        //
    uint16_t        manual_on:1;        //手动开环/自动闭环标志位    下传或设定值  0 自动　 1 手动
    uint16_t        forbid_hot_standby:1;    //禁用热备标志位  下传或设定值  0 允许　 1 禁用
    uint16_t        None6:1;    //
    uint16_t        button_sound:1;        //按钮音响标志位
    uint16_t        None8:1;        //占空位的，不存数据
    uint16_t        None9:1;        //占空位的，不存数据
    uint16_t        None10:1;        //占空位的，不存数据
    uint16_t        None11:1;        //占空位的，不存数据
    uint16_t        None12:1;        //占空位的，不存数据
    uint16_t        None13:1;    //占空位的，不存数据
    uint16_t        None14:1;    //占空位的，不存数据
    uint16_t        None15:1;        //占空位的，不存数据
}half_Word3;
typedef struct
{
    uint16_t        None0:1;        //
    uint16_t        control_angle_display:1;        //控制角显示标志位  下传或设定值  0 控制角　1 导通角
    uint16_t        trigger_reverse:1;        //触发旋向标志位 下传或设定值  0 正向　   1 反向
    uint16_t        AC_display:1;        //交流显示有效 下传或设定值  0 无效　　 1 有效
    uint16_t        AC_feedback:1;        //主反馈交直选择标志位    下传或设定值  0 直流　　 1 交流
    uint16_t        two_feedback:1;    //单双反馈选择标志位    下传或设定值  0 单反馈　 1 双反馈
    uint16_t        display_filter:1;    //显示滤波   下传或设定值  0 无效　　 1 有效
    uint16_t        None7:1;        //
    uint16_t        None8:1;        //占空位的，不存数据
    uint16_t        None9:1;        //占空位的，不存数据
    uint16_t        None10:1;        //占空位的，不存数据
    uint16_t        None11:1;        //占空位的，不存数据
    uint16_t        None12:1;        //占空位的，不存数据
    uint16_t        None13:1;    //占空位的，不存数据
    uint16_t        None14:1;    //占空位的，不存数据
    uint16_t        None15:1;        //占空位的，不存数据

}half_Word4;
union half_Word0_u {
    uint16_t          all;
   half_Word0      bit;
};
union half_Word1_u {
    uint16_t          all;
   half_Word1      bit;
};
union half_Word2_u {
    uint16_t          all;
   half_Word2      bit;
};
union half_Word3_u {
    uint16_t          all;
   half_Word3      bit;
};
union half_Word4_u {
    uint16_t          all;
   half_Word4      bit;
};
typedef struct Zero_3Register_t
{
    union half_Word0_u   InputRegister0;             //表示上传数据的第0个16bit
    union half_Word1_u   InputRegister1;             //表示上传数据的第0个16bit
    union half_Word2_u   InputRegister2;             //表示上传数据的第0个16bit
    union half_Word3_u   InputRegister3;             //表示上传数据的第0个16bit
    union half_Word4_u   InputRegister4;             //表示上传数据的第0个16bit
    uint16_t    DC_engineer_value;  //直流电流工程值 0-1023
    uint16_t    DC_rectifier_output;  //当前整流输出直流电流数值 0-10000 单位0.01KA 小数点位置可变
    uint16_t    AC_rectifier_output;  //当前整流输出交流侧电流数值
    uint16_t    control_angle;  //运行控制角   0～1500　 单位0.1°
    uint16_t    fire_angle;  //运行导通角     0～1500　 单位0.1°
    uint16_t    DC_current_setpoint1;  //直流自动给定（D）     0～10000　单位0.01KA    小数点位置可变
    uint16_t    DC_current_setpoint2;  //直流自动给定2（D）     0～10000　单位0.01KA
    uint16_t    manual_delay_angle_degree;  //手动开环给定(M)     0～1500　单位0.1°
    uint16_t    sync_period;  //同步周期      0～999　 单位0.1Hz
    uint16_t    extern_simu_given;  //外部模拟给定值       0～1000　单位0.1%
    uint16_t    trigger_voltage;  //触发电源电压值       0～1000  单位0.1V
    uint16_t    current_limit_value;  //限流值       1-99.99  单位0.01KA   小数点位置可变
    uint16_t    initial_delay_angle_degree;  //初始定相值     0～3600　单位0.1°
    uint16_t    max_delay_angle_degree;  //最大限幅值     0～1500　单位0.1°
    uint16_t    PI_ratio;  //PI系数      0~1024
    uint16_t    Kp;  //P参数值      1~1023
    uint16_t    Ki;  //I参数值      1~1023
    uint16_t    AC_range;  //交流电流量程    1～1023 对应 0～10000 ( * A→1000.0A) 数值范围1-9999
    uint16_t    DC_range;  //直流电流量程    1～1023 对应 1～10000 ( * KA→100.00KA)  数值范围1-9999
    uint16_t    fire_display_ratio;  //控制角导通角输出显示系数
    uint16_t    DC_feedback_amplitude;  //直流反馈幅度选择  00~07　分别对应相关量程选择
    uint16_t    AC_feedback_amplitude;  //交流反馈幅度选择   00~07　分别对应相关量程选择
    uint16_t    extern_given_amplitude;  //外部给定幅度选择      00~07　分别对应相关量程选择
    uint16_t    None28;  //占空位的，不存数据
    uint16_t    AC_correction;  //交流电流修正系数  调整使正常工作时，交直反馈工作数值相等 100~3000
    uint16_t    DC_correction;  //直流电流修正系数  调整直流反馈于满量程时为最大限流值   100~3000
    uint16_t    angle_correction;  //控制角导通角修正系数    对应于196输出控制角导通角数据的变换系数(与数显表对应)   0～1000 对应 0～10.0V
    uint16_t    None32;  //占空位的，不存数据
    uint16_t    sync_loss_Time;  //同步全失时限       0～100　单位100 mS
    uint16_t    given_C_change_rate;  //电流给定变化率（步进值）     0～100　单位100 mS
    uint16_t    drop_C_rate;  //降电流变化率（步进值）      0～100　单位100 mS
    uint16_t    None36;  //
    uint16_t    None37;  //
    uint16_t    None38;  //
    uint16_t    year;  //年 00~99
    uint16_t    month;  //月 1~12
    uint16_t    day;  //日 1~31
    uint16_t    hour;  //时 1~24
    uint16_t    minute;  //分 1~60
    uint16_t    second;  //秒 1~60
    uint16_t    None45;  //
    uint16_t    contrast;  //液晶对比度值       0～100
    uint16_t    ID;  //数控器站地址       00~255
}Zero_3Register;


void initModbusData(void);
//定义四种寄存器
extern CoilRegister  CoilRegisterList1;
//extern DiscreteInputRegister  DiscreteInputRegisterList1;
extern DataRegister  DataRegisterList1;
extern Zero_3Register Zero_3RegisterList1;




#endif /* MODBUS_CONTENT_H_ */
