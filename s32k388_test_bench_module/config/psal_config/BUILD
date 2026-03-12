load("@fe56//src/psal:psal_builder.bzl", "psal_zenoh_pico_header_builder_px5")

psal_zenoh_pico_header_builder_px5(
    "s32k388_test_bench_module/config/os_config",
    "s32k388_test_bench_module/config/net_config",
    additional_copts = ["-DZENOH_PX5"],
    variant = "module",
)
