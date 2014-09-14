// array[0 ... length - 1] position
// array[length ... length * 2 - 1] velocity

static float
calc_wave_func(__global const float *in, float h, ulong len, int i)
{
    if (i < len) {
        return in[i + len];
    } else {
        int i2 = i - len;
        if (i2 >= 4 && i2 <= len - 5) {
            return (-(in[i2 - 4] + in[i2 + 4]) / 560.f
                    + (in[i2 - 3] + in[i2 + 3]) * (8.f / 315.f)
                    - (in[i2 - 2] + in[i2 + 2]) * (1.f / 5.f)
                    + (in[i2 - 1] + in[i2 + 1]) * (8.f / 5.f)
                    - in[i2] * (205.f / 72.f)) / h / h;
        } else if (i2 == 0 || i2 == len - 1) {
            return 0;
        } else if (i2 == 1 || i2 == len - 2) {
            return ((in[i2 - 1] + in[i2 + 1]) - in[i2] * 2) / h / h;
        } else if (i2 == 2 || i2 == len - 3) {
            return (-(in[i2 - 2] + in[i2 + 2]) / 12.f
                    + (in[i2 - 1] + in[i2 + 1]) * (4.f / 3.f)
                    - in[i2] * (5.f / 2.f)) / h / h;
        } else {
            // (i2 == 3 || i2 == len - 4)
            return ((in[i2 - 3] + in[i2 + 3]) / 90
                    - (in[i2 - 2] + in[i2 + 2]) * (3.f / 20.f)
                    + (in[i2 - 1] + in[i2 + 1]) * (3.f / 2.f)
                    - in[i2] * (49.f / 18.f)) / h / h;
        }
    }
}
