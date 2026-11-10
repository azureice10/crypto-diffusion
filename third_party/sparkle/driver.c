#include <stdio.h>
#include <stdint.h>
#include "sparkle.h"

int main(void) {
    int branches, steps;
    uint32_t state[16];
    while (scanf("%d %d", &branches, &steps) == 2) {
        if (branches != 4 && branches != 6 && branches != 8) return 2;
        for (int j = 0; j < 2 * branches; j++) {
            if (scanf("%x", &state[j]) != 1) return 3;
        }
        sparkle(state, branches, steps);
        for (int j = 0; j < 2 * branches; j++) printf("%08x", state[j]);
        printf("\n");
    }
    return 0;
}
