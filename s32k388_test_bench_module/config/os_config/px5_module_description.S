;/*
;
;                             XXXXXXXXXXXXXXXXXXXXXX                          XXXXXXXXXXXXXXXXXXXXXX                                         
;                               XXXXXXXXXXXXXXXXXXXXXX                      XXXXXXXXXXXXXXXXXXXXXX                                           
;                                 XXXXXXXXXXXXXXXXXXXXXX                  XXXXXXXXXXXXXXXXXXXXXX                                             
;                                   XXXXXXXXXXXXXXXXXXXXXX              XXXXXXXXXXXXXXXXXXXXXX                                               
;                                     XXXXXXXXXXXXXXXXXXXXXX          XXXXXXXXXXXXXXXXXXXXXX                                                 
;                                       XXXXXXXXXXXXXXXXXXXXXX      XXXXXXXXXXXXXXXXXXXXXX                                                   
;                                         XXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXX                                                     
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP           XXXXXXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXX         555555555  55555555555555555555555555555      
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP         XXXXXXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXX           555555555  55555555555555555555555555555      
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP         XXXXXXXXX   XXXXXXXXXXXXXXXXXXXXXX             555555555  55555555555555555555555555555      
;PPPPPPPPP                     PPPPPPPPPP         XXXXX   XXXXXXXXXXXXXXXXXXXXXX               555555555                                     
;PPPPPPPPP                     PPPPPPPPPP           X   XXXXXXXXXXXXXXXXXXXXXX                 555555555                                     
;                              PPPPPPPPPP             XXXXXXXXXXXXXXXXXXXXXX                   55555555555555555555555555555555555555        
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP             XXXXXXXXXXXXXXXXXXXXXX  XX                 5555555555555555555555555555555555555555      
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP             XXXXXXXXXXXXXXXXXXXXXX  XXXXXX               55555555555555555555555555555555555555555     
;PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP               XXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXX                                            55555555555    
;PPPPPPPPP                                    XXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXX           5555555555                     55555555555    
;PPPPPPPPP                                  XXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXXX         55555555555                   55555555555     
;PPPPPPPPP                                XXXXXXXXXXXXXXXXXXXXXX  XXXXXXXXXXXXXXXXXXXXXX        555555555555555555555555555555555555555      
;PPPPPPPPP                              XXXXXXXXXXXXXXXXXXXXXX      XXXXXXXXXXXXXXXXXXXXXX       5555555555555555555555555555555555555       
;PPPPPPPPP                            XXXXXXXXXXXXXXXXXXXXXX          XXXXXXXXXXXXXXXXXXXXXX       555555555555555555555555555555555         
;                                   XXXXXXXXXXXXXXXXXXXXXX              XXXXXXXXXXXXXXXXXXXXXX                                               
;                                 XXXXXXXXXXXXXXXXXXXXXX                  XXXXXXXXXXXXXXXXXXXXXX                                             
;                               XXXXXXXXXXXXXXXXXXXXXX                      XXXXXXXXXXXXXXXXXXXXXX                                           
;                             XXXXXXXXXXXXXXXXXXXXXX                          XXXXXXXXXXXXXXXXXXXXXX                                         
;                           XXXXXXXXXXXXXXXXXXXXXX                              XXXXXXXXXXXXXXXXXXXXXX                                       
;
;
;                             P T H R E A D S +         R T O S         by         B i l l   L a m i e
;
;
;Version 5.3.0.1
;
;
;Copyright (C) 2022-2025 PX5 - All Rights Reserved.
;
;You may use this software only under the terms specified in your license 
;from PX5. All other use is strictly prohibited. If you do not have a license 
;to use this software, please contact www.px5rtos.com to obtain one.
;
;*/
;
;/****************************************************************************
; *                                                                          *
; *       PX5 Module Description for Cortex-M7 & GCC Development Tools       *
; *                                                                          *
; ***************************************************************************/

    .syntax unified
    .cpu cortex-m7
    .thumb

    .section .text

    .p2align 3

    /* Define public symbols.  */
    .section .px5_module_descriptor_header
    .global px5_module_description


    /* Define common external references.  */

        .extern  px5_module_internal_thread_wrapper

        .align  4
px5_module_description:

        .word    0x4D4F4455                                          // 0x00  PX5 Module Signature
        .word    0x23232323                                          // 0x04  Reserved
        .word    0x23232323                                          // 0x08  Reserved
        .word    0x5645523A                                          // 0x0C  VER:
        .word    0x5                                                 // 0x10  Module Major Version
        .word    0x3                                                 // 0x14  Module Minor Version
        .word    0x0                                                 // 0x18  Module Update Version
        .word    0x0                                                 // 0x1C  Module Patch Version
        .word    0x53495A45                                          // 0x20  SIZE
        .word    32                                                  // 0x24  Container Size in 32-bit words
        .word    0x494E5354                                          // 0x28  INST
        .word    __code_size__                                       // 0x2C  Instruction Area Size in bytes
        .word    0x44415441                                          // 0x30  DATA
        .word    __total_data_size__                                 // 0x34  Data Area Size in bytes
        .word    0x41545452                                          // 0x38  ATTR
        .word    0                                                   // 0x3C  Module Attributes:
                                                                     //           Bit 0:  0 -> Privilege Mode; 1 -> User Mode
                                                                     //           Bit 1:  0 -> No Memory Protection; 1 -> Memory Protection
                                                                     //           Bits 2-31 Reserved
        .word    0x544F4F4C                                          // 0x40  TOOL:
        .word    0                                                   // 0x44  Tool ID:  0 -> GCC; 1 -> IAR; 2 -> Arm
        .word    0x57524150                                          // 0x48  WRAP
        .word    px5_module_internal_thread_wrapper - px5_module_description // 0x4C  Module internal thread wrapper function
        .word    1024                                                // 0x50  Module stack size
        .word    0x23232323                                          // 0x54  Reserved
        .word    0x23232323                                          // 0x58  Reserved
        .word    0x23232323                                          // 0x5C  Reserved
        .word    0x23232323                                          // 0x60  Reserved
        .word    0x23232323                                          // 0x64  Reserved
        .word    0x23232323                                          // 0x68  Reserved
        .word    0x23232323                                          // 0x6C  Reserved
        .word    0x23232323                                          // 0x70  Reserved
        .word    0x23232323                                          // 0x74  Reserved
        .word    0x4D4F4455                                          // 0x78  MODU
        .word    0x454E4420                                          // 0x7C  END

        .end
