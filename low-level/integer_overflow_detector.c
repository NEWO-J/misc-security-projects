#include <stdio.h>

int uadd_ok(unsigned x, unsigned y) {
    unsigned sum = x + y;
    if (sum < x || sum < y) {
        return 0;
    } 
    else {
        return 1;
    }
}

int main()
{
    int result = uadd_ok(4294967290, 6);
    if (result == 0) {
        printf("Overflow detected");
    } else {
        printf("No overflow detected");
    }
    
    return 0;
}