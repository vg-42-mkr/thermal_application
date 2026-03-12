load("@aspect_bazel_lib//lib:transitions.bzl", "platform_transition_filegroup")
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

filegroup(
    name = "thermal_example_module_args_header",
    srcs = ["thermal_example_module_args.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "thermal_example_module_args_header_lib",
    hdrs = [
        "thermal_example_module_args.h",
    ],
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "thermal_example_module",
    srcs = [
        "thermal_example_module.c",
    ],
    additional_linker_inputs = ["module_linker_flash_s32k388.ld"],
    linkopts = [
        "-T $(location :module_linker_flash_s32k388.ld)",
        "-Wl,-u,_printf_float",
    ],
    deps = [
        "thermal_example_module_args_header_lib",
        "//s32k388_test_bench_module/config/net_config:px5_net",
        "//s32k388_test_bench_module/config/os_config:osal",
        "//s32k388_test_bench_module/config/psal_config:psal",
        "@fe56//src/ddal/api:ddal_api",
        ":simple_sil_thermal_ctrl_t3",
    ],
)

cc_library(
    name = "simple_sil_thermal_ctrl_t3",
    hdrs = [
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3.h",
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3_private.h",
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3_types.h",
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t4_math.h",
        "simple_thermal_sil_ctrl/sl_types_def.h",
        "simple_thermal_sil_ctrl/multiword_types.h",
        "simple_thermal_sil_ctrl/builtin_typeid_types.h",
    ],
    srcs = [
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3.c",
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t3_data.c",
        "simple_thermal_sil_ctrl/simple_sil_thermal_ctrl_t4_math.c",
    ],
    includes = ["."],
)



platform_transition_filegroup(
    name = "thermal_example_module.elf",
    srcs = [":thermal_example_module"],
    target_platform = "@fe56//toolchains/platforms:s32k5_bare_metal",
)
