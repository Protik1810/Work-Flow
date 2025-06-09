# utils.py

def convert_number_to_words(number):
    """Converts a number (int or float) to its Indian English word representation."""
    if not isinstance(number, (int, float)): return "Invalid Number"
    if number < 0: return "Minus " + convert_number_to_words(abs(number))
    if number == 0: return "Zero Rupees Only"

    num_str = f"{number:.2f}"
    integer_part_str, decimal_part_str = num_str.split('.')
    rupees = int(integer_part_str)
    paise = int(decimal_part_str)

    def to_words(n, suffix=""):
        if n == 0: return ""
        
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                    "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        if n < 20:
            words = units[n]
        elif n < 100:
            words = tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        elif n < 1000:
            words = units[n // 100] + " Hundred" + (" and " + to_words(n % 100) if n % 100 != 0 else "")
        elif n < 100000:
            words = to_words(n // 1000, "Thousand") + (" " + to_words(n % 1000) if n % 1000 != 0 else "")
        elif n < 10000000:
            words = to_words(n // 100000, "Lakh") + (" " + to_words(n % 100000) if n % 100000 != 0 else "")
        else:
            words = to_words(n // 10000000, "Crore") + (" " + to_words(n % 10000000) if n % 10000000 != 0 else "")
        
        return words.strip() + (f" {suffix}" if suffix else "")

    rupees_words = to_words(rupees).strip()
    final_words = f"Rupees {rupees_words}"

    if paise > 0:
        paise_words = to_words(paise).strip()
        final_words += f" and Paise {paise_words}"

    return final_words.strip() + " Only"