def f16_to_float(f16: int) -> float:
    sign = -1 if (f16 & 0x8000) != 0 else 1
    exponent = (f16 & 0x7C00) >> 10
    mantissa = f16 & 0x3FF

    if exponent == 0b11111:
        return float("nan") if mantissa != 0 else sign * float("inf")
    if exponent == 0:
        return sign * (2 ** (-14)) * (mantissa / 1024)

    return sign * (2 ** (exponent - 15)) * (1 + mantissa / 1024)


if __name__ == "__main__":
    import unittest
    import math

    class F16TestCase(unittest.TestCase):
        def test(self):
            # From https://en.wikipedia.org/wiki/Half-precision_floating-point_format#Half_precision_examples
            # Thank you Wikipedia editors <3
            vals = [
                (0, 0),
                (1, 0.000000059604645),
                (0x3FF, 0.000060975552),
                (0x400, 0.00006103515625),
                (0x3555, 0.33325195),
                (0x3BFF, 0.99951172),
                (0x3C00, 1.0),
                (0x3C01, 1.00097656),
                (0x4248, 3.140625),
                (0x67FF, 2047),
                (0x7BFF, 65504),
                (0x7C00, float("inf")),
                (0x8000, -float(0)),
                (0xC000, -2),
                (0xFC00, -float("inf")),
                (0x7F00, float("nan")),
            ]
            for i in vals:
                i, o, p = i if len(i) == 3 else (*i, 6)
                if math.isnan(o):
                    self.assertTrue(math.isnan(f16_to_float(i)), f"in: {i:x}")
                else:
                    self.assertAlmostEqual(f16_to_float(i), o, p, f"in: {i:x}")

    unittest.main()
