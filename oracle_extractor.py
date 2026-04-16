"""
oracle_extractor.py

Demonstrates binary oracle attack mechanics against a local toy target.
Reads the concept in three passes, each more efficient than the last.

Run: python oracle_extractor.py

Learning goals:
1. Understand why yes/no answers leak information
2. See why binary search is exponentially faster than linear search
3. Count queries to understand the attack's practical cost
"""

from toy_oracle_target import ToyOracleChatbot
import string


# ============================================================
# PASS 1: LINEAR SEARCH (naive, slow, but easy to understand)
# ============================================================
# Idea: for each position in the secret, try every possible
# character one at a time. Ask "is it 'a'?", "is it 'b'?", etc.
#
# Cost: if the alphabet has N chars and the secret is L long,
# this takes roughly N * L queries in the worst case.
# For a 7-char secret over ~95 printable chars, that's ~665 queries.
# ============================================================

def extract_linear(bot: ToyOracleChatbot, max_length: int = 20) -> str:
    """Recover the secret one character at a time by trying every char."""
    alphabet = string.ascii_letters + string.digits  # 62 chars for simplicity
    extracted = ""

    # First: find the length of the secret
    # Ask: is the length exactly 1? 2? 3? ... until we get yes.
    for length_guess in range(1, max_length + 1):
        if bot.yes_no_question(lambda s, n=length_guess: len(s) == n):
            secret_length = length_guess
            break

    # Now for each position, try every character
    for position in range(secret_length):
        for char in alphabet:
            if bot.yes_no_question(
                lambda s, p=position, c=char: s[p] == c
            ):
                extracted += char
                break

    return extracted


# ============================================================
# PASS 2: BINARY SEARCH (efficient, the "real" oracle technique)
# ============================================================
# Idea: instead of asking "is it 'a'?" through the whole alphabet,
# ask questions that cut the possibility space in half each time.
#
# Example for alphabet a-z (26 chars):
#   "Is it less than 'n'?"  -> narrows to 13 possibilities
#   "Is it less than 'g'?"  -> narrows to 6 or 7
#   "Is it less than 'd'?"  -> narrows to 3 or 4
#   ... in about log2(26) ≈ 5 queries, you've found the char
#
# Cost: L * log2(N) queries. For 7 chars over 62-char alphabet,
# that's about 7 * 6 = 42 queries. That's ~16x faster than linear.
# ============================================================

def extract_binary(bot: ToyOracleChatbot, max_length: int = 20) -> str:
    """Recover the secret using binary search per character position."""
    alphabet = sorted(string.ascii_letters + string.digits)
    extracted = ""

    # Find length first (same as linear - length is small enough)
    for length_guess in range(1, max_length + 1):
        if bot.yes_no_question(lambda s, n=length_guess: len(s) == n):
            secret_length = length_guess
            break

    # For each position, binary-search the alphabet
    for position in range(secret_length):
        low, high = 0, len(alphabet) - 1

        # Narrow the range by halving
        while low < high:
            mid = (low + high) // 2
            midpoint_char = alphabet[mid]

            # "Is the character at this position <= midpoint_char?"
            is_low_half = bot.yes_no_question(
                lambda s, p=position, c=midpoint_char: s[p] <= c
            )

            if is_low_half:
                high = mid
            else:
                low = mid + 1

        extracted += alphabet[low]

    return extracted


# ============================================================
# PASS 3: BIT-LEVEL EXTRACTION (most efficient theoretically)
# ============================================================
# Idea: characters are stored as bytes. A byte has 8 bits.
# Extract each bit directly with a bitmask question.
#
# For each character position, ask 8 yes/no questions:
#   "Is bit 7 of this char set?"  (the 128s place)
#   "Is bit 6 of this char set?"  (the 64s place)
#   ... etc
# Reconstruct the byte from the bits.
#
# Cost: L * 8 queries. For a 7-char secret, that's 56 queries.
# Comparable to binary search but works for any byte value,
# not just printable chars.
# ============================================================

def extract_bitwise(bot: ToyOracleChatbot, max_length: int = 20) -> str:
    """Recover the secret by extracting each bit of each byte."""
    extracted = ""

    # Find length
    for length_guess in range(1, max_length + 1):
        if bot.yes_no_question(lambda s, n=length_guess: len(s) == n):
            secret_length = length_guess
            break

    # For each character, extract all 8 bits
    for position in range(secret_length):
        byte_value = 0
        for bit in range(7, -1, -1):  # high bit to low bit
            mask = 1 << bit
            # "Is bit `bit` of the character at `position` set?"
            bit_is_set = bot.yes_no_question(
                lambda s, p=position, m=mask: (ord(s[p]) & m) != 0
            )
            if bit_is_set:
                byte_value |= mask
        extracted += chr(byte_value)

    return extracted


# ============================================================
# DEMONSTRATION
# ============================================================

def demo(method_name: str, method_fn, secret: str):
    """Run one extraction method and report stats."""
    bot = ToyOracleChatbot(secret=secret)
    recovered = method_fn(bot)
    success = "✅" if recovered == secret else "❌"
    print(f"{success} {method_name:20} | "
          f"recovered: {recovered!r:15} | "
          f"queries: {bot.query_count}")


if __name__ == "__main__":
    SECRET = "hello42"
    print(f"Target secret: {SECRET!r} ({len(SECRET)} chars)")
    print("-" * 70)

    demo("Linear search",   extract_linear,  SECRET)
    demo("Binary search",   extract_binary,  SECRET)
    demo("Bitwise",         extract_bitwise, SECRET)

    print()
    print("Key insight: same information extracted, vastly different costs.")
    print("In a real attack, query count translates to:")
    print("  - Time (each query = round-trip to the LLM)")
    print("  - Cost (each query might be a paid API call)")
    print("  - Detectability (high query volume triggers rate limiting)")
