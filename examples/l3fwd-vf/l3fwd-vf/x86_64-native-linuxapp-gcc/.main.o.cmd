cmd_main.o = gcc -Wp,-MD,./.main.o.d.tmp -m64 -pthread  -march=native -DRTE_MACHINE_CPUFLAG_SSE -DRTE_MACHINE_CPUFLAG_SSE2 -DRTE_MACHINE_CPUFLAG_SSE3 -DRTE_MACHINE_CPUFLAG_SSSE3 -DRTE_MACHINE_CPUFLAG_SSE4_1 -DRTE_MACHINE_CPUFLAG_SSE4_2 -DRTE_MACHINE_CPUFLAG_AES -DRTE_MACHINE_CPUFLAG_PCLMULQDQ -DRTE_MACHINE_CPUFLAG_AVX -DRTE_MACHINE_CPUFLAG_RDRAND -DRTE_MACHINE_CPUFLAG_FSGSBASE -DRTE_MACHINE_CPUFLAG_F16C -DRTE_MACHINE_CPUFLAG_AVX2  -I/opt/dpdk-stable-16.07.2/examples/l3fwd-vf/l3fwd-vf/x86_64-native-linuxapp-gcc/include -I/opt/dpdk-stable-16.07.2//x86_64-native-linuxapp-gcc/include -include /opt/dpdk-stable-16.07.2//x86_64-native-linuxapp-gcc/include/rte_config.h -O3  -W -Wall -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wold-style-definition -Wpointer-arith -Wcast-align -Wnested-externs -Wcast-qual -Wformat-nonliteral -Wformat-security -Wundef -Wwrite-strings -Wno-return-type  -o main.o -c /opt/dpdk-stable-16.07.2/examples/l3fwd-vf/main.c 
