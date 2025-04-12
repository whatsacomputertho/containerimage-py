"""
ByteUnit class

Contains static helper methods for formatting byte size measurements
"""
class ByteUnit:
    @staticmethod
    def format_size_bytes(size: int) -> str:
        """
        Format size in bytes as a human readable string, representing the size
        at its nearest byte unit

        Args:
        size (int): The size in bytes

        Returns:
        str: The size formatted as a human readable string (e.g. "2.51 MB")
        """
        units = ['B', 'KB', 'MB', 'GB']
        for suffix in units:
            if size < 1024:
                return f"{size:.2f} {suffix}"
            size /= 1024
        return f"{size:.2f} TB"