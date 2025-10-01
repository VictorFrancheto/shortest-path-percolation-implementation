from src.utils import genrand64_int64, genrand64_real3, init_genrand64, mt

def test_genrand64_int64_returns_int():
    val = genrand64_int64()
    assert isinstance(val, int)
    # 64-bit integer must be within range
    assert 0 <= val < (1 << 64)


def test_genrand64_real3_returns_float():
    val = genrand64_real3()
    assert isinstance(val, float)
    # should be between 0 and 1
    assert 0.0 <= val < 1.0


def test_init_genrand64_sets_state():
    seed = 12345
    init_genrand64(seed)
    # check if global state is initialized
    assert mt[0] == seed
    assert all(isinstance(x, int) for x in mt)
