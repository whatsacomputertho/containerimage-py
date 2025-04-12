from image.byteunit import ByteUnit

def test_format_size_bytes():
    assert ByteUnit.format_size_bytes(256) == "256.00 B"
    assert ByteUnit.format_size_bytes(20992) == "20.50 KB"
    assert ByteUnit.format_size_bytes(316072263) == "301.43 MB"
    assert ByteUnit.format_size_bytes(3371549327) == "3.14 GB"
