#include "modding.h"
#include "global.h"

RECOMP_IMPORT(".", void bridge_generate());

RECOMP_CALLBACK("*", recomp_on_init)
void init_generation() {
    bridge_generate();
}
