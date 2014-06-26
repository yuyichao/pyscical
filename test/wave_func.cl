// array[0 ... length - 1] position
// array[length ... length * 2 - 1] velocity


void
calc_wave_func(__global float *res, __global const float *in,
               float h, int len, int i)
{
    if (i < len) {
        res[i] = in[i + len];
    } else {
        int i2 = i - len;
        if (i2 >= 4 && i2 <= len - 5) {
            res[i] = (-(in[i2 - 4] + in[i2 + 4]) / 560.
                      + (in[i2 - 3] + in[i2 + 3]) * (8. / 315.)
                      - (in[i2 - 2] + in[i2 + 2]) * (1. / 5.)
                      + (in[i2 - 1] + in[i2 + 1]) * (8. / 5.)
                      - in[i2] * (205. / 72.)) / h / h;
        } else if (i2 == 0 || i2 == len - 1) {
            res[i] = 0;
        } else if (i2 == 1 || i2 == len - 2) {
            res[i] = ((in[i2 - 1] + in[i2 + 1])
                      - in[i2] * 2) / h / h;
        } else if (i2 == 2 || i2 == len - 3) {
            res[i] = (-(in[i2 - 2] + in[i2 + 2]) / 12.
                      + (in[i2 - 1] + in[i2 + 1]) * (4. / 3.)
                      - in[i2] * (5. / 2.)) / h / h;
        } else if (i2 == 3 || i2 == len - 4) {
            res[i] = ((in[i2 - 3] + in[i2 + 3]) / 90
                      - (in[i2 - 2] + in[i2 + 2]) * (3. / 20.)
                      + (in[i2 - 1] + in[i2 + 1]) * (3. / 2.)
                      - in[i2] * (49. / 18.)) / h / h;
        }
    }
}
