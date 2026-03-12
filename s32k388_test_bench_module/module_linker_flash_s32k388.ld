/* Highest address of the user mode stack */
_estack = ORIGIN(RAM) + LENGTH(RAM); /* end of "RAM" Ram type memory */

_Min_Heap_Size =  0x200; /* required amount of heap */
_Min_Stack_Size = 0x800; /* required amount of stack */

/* Memories definition */
MEMORY
{
  /* RAM    (xrw)   : ORIGIN = 0x20001000,   LENGTH = 0xE000 */
  RAM    (xrw)   : ORIGIN = 0x20458000,   LENGTH = 0x8000
  FLASH  (rx)    : ORIGIN = 0x00600000,   LENGTH = 0x40000
}

/* Sections */
SECTIONS
{
    __flash_link_address__ = ORIGIN(FLASH);
    __flash_size__ = LENGTH(FLASH);

    __ram_link_address__ = ORIGIN(RAM);
    __ram_size__ = LENGTH(RAM);

  /* The startup code into "FLASH" Rom type memory */
  /*.isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH */

  /* The program code and other data into "FLASH" Rom type memory */
  .text :
  {
    . = ALIGN(4);
    __code_start = .;
    *(.px5_module_description)
    KEEP(*(.px5_module_descriptor_header))
    *(.text)           /* .text sections (code) */
    *(.text*)          /* .text* sections (code) */
    *(.glue_7)         /* glue arm to thumb code */
    *(.glue_7t)        /* glue thumb to arm code */
    *(.eh_frame)

    KEEP (*(.init))
    KEEP (*(.fini))

    . = ALIGN(4);
    _etext = .;        /* define a global symbols at end of code */
  } >FLASH

  /* Constant data into "FLASH" Rom type memory */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)         /* .rodata sections (constants, strings, etc.) */
    *(.rodata*)        /* .rodata* sections (constants, strings, etc.) */
    . = ALIGN(4);
  } >FLASH

  .ARM.extab   : {
    . = ALIGN(4);
    *(.ARM.extab* .gnu.linkonce.armextab.*)
    . = ALIGN(4);
  } >FLASH

  .ARM : {
    . = ALIGN(4);
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
    . = ALIGN(4);
  } >FLASH

  .preinit_array     :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .init_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .fini_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .rel.text :
  {
    __rel_text_start__ = .;
    KEEP(*(.rel.text))
    KEEP(*(.rel.text*))
    __rel_text_end__ = .;
  } >FLASH
  __rel_text_size__ = __rel_text_end__ - __rel_text_start__;
  __rel_text_offset__ = __rel_text_start__ - ORIGIN(FLASH);

  .rel.dyn :
  {
    __rel_dyn_start__ = .;
    KEEP(*(.rel.dyn))
    KEEP(*(.rel.dyn*))
    KEEP(*(.rel.got))
    KEEP(*(.rel.plt))
    KEEP(*(.rel.bss))
    KEEP(*(.rel.iplt))
    __rel_dyn_end__ = .;
  } >FLASH
  __rel_dyn_size__ = __rel_dyn_end__ - __rel_dyn_start__;
  __rel_dyn_offset__ = __rel_dyn_start__ - ORIGIN(FLASH);

  .rel.data :
  {
    __rel_data_start__ = .;
    KEEP(*(.rel.data))
    KEEP(*(.rel.data*))
    __rel_data_end__ = .;
  } >FLASH
  __rel_data_size__ = __rel_data_end__ - __rel_data_start__;
  __rel_data_offset__ = __rel_data_start__ - ORIGIN(FLASH);

  .got :
  {
    . = ALIGN(4096);
    __total_data_start__ = .;
    __got_start__ = .;
    *(.got)
    *(.got.*)
    __got_end__ = .;
  } >RAM AT>FLASH
  __got_size__ = __got_end__ - __got_start__;
  __got_flash_offset__ = LOADADDR(.got) - ORIGIN(FLASH);
  __got_ram_offset__ =  __got_start__ - ORIGIN(RAM);

  __code_size__ = LOADADDR(.got) + __got_size__ - __code_start;

  /* Used by the startup to initialize data */
  _sidata = LOADADDR(.data);

  /* Initialized data sections into "RAM" Ram type memory */
  .data :
  {
    __data_start__ = .;
    _sdata = .;        /* create a global symbol at data start */
    *(.data)           /* .data sections */
    *(.data*)          /* .data* sections */
    *(.RamFunc)        /* .RamFunc sections */
    *(.RamFunc*)       /* .RamFunc* sections */

    . = ALIGN(4);
    _edata = .;        /* define a global symbol at data end */

   __data_end = .;
  } >RAM AT> FLASH

  __data_size__ = __data_end - __data_start__;
  __data_flash_offset__ = LOADADDR(.data) - ORIGIN(FLASH);
  __data_ram_offset__ = __data_start__ - ORIGIN(RAM);
  __data_load_start__ = LOADADDR(.data);

  /* Uninitialized data section into "RAM" Ram type memory */
  . = ALIGN(4);
  .bss (NOLOAD) :
  {
    /* This is used by the startup in order to initialize the .bss section */
    _sbss = .;         /* define a global symbol at bss start */
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)

    . = ALIGN(4);
    _ebss = .;         /* define a global symbol at bss end */
    __bss_end__ = _ebss;
  } >RAM

  __bss_size__ = __bss_end__ - __bss_start__;
  __bss_offset__ = __bss_start__ - ORIGIN(RAM);

  /* User_heap_stack section, used to check that there is enough "RAM" Ram  type memory left */
  /* For PX5 RTOS proc Stack */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    PROVIDE ( __StackLimit = .);
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
    PROVIDE ( __StackTop = .);
  } >RAM

  __total_data_size__ = . - __total_data_start__;

  /* Remove information from the compiler libraries */
  /DISCARD/ :
  {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }

  __px5_module_internal_flash_runtime_address_get_offset__ = px5_module_internal_flash_runtime_address_get - px5_module_description;
}
