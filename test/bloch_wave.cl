// array[0 ... length - 1] position
// array[length ... length * 2 - 1] velocity

cfloat_t
calc_bloch_wave_single(cfloat_t self, cfloat_t left, cfloat_t right,
                       float t, float E)
{
    return self * E + (left + right) * t;
}

void
calc_bloch_wave(__global cfloat_t *res, __global const cfloat_t *in,
                float t, float slope, int len, int i)
{
    float E = i * slope;
    cfloat_t H = calc_bloch_wave_single(in[i], in[(i > 0 ? i : len) - 1],
                                        in[i < len - 1 ? (i + 1) : 0], t, E);
    res[i] = (cfloat_t)(H.y, -H.x);
}
